import RPi.GPIO as GPIO
from time import sleep
from samplebase import SampleBase
from vibrator import setVibrator
from gyroscope_handler import get_tilt_direction
from common_functions import setup_gpio, GameExit, update_button_states
from mqtt_client import MQTTClient
# for some reason it doesn't recognize the load_dotenv function directly
from dotenv import main
# so we have to import it from the main module
main.load_dotenv()

# MQTT Broker details
TOPIC_QUERY = "tictactoe/input"
TOPIC_RESPONSE = "tictactoe/output"


class TicTacToeGame(SampleBase):
    '''
    Main class for the Tic-Tac-Toe game.
    '''

    def __init__(self, *args, **kwargs):
        '''
        Initialize the Tic-Tac-Toe game instance.
        '''
        super(TicTacToeGame, self).__init__(*args, **kwargs)

        # Initialize MQTT client
        self.mqtt_client = MQTTClient(TOPIC_QUERY, TOPIC_RESPONSE)

        # Initialize empty grid and current position at the top-left corner
        self.grid = [[None for _ in range(3)] for _ in range(3)]
        self.current_position = (0, 0)
        self.game_over = False

        # GPIO setup and reset button states
        setup_gpio(self)
        self.blue_button = None
        self.red_button = None
        update_button_states(self)

    def draw_grid(self, canvas):
        '''
        Draw the Tic-Tac-Toe grid on the canvas.
        '''
        width = self.matrix.width
        height = self.matrix.height
        third_width = width // 3
        third_height = height // 3

        # it will iterate twice, so it will draw 2 vert. and 2 hor. lines
        for i in range(1, 3):
            line_x = i * third_width
            line_y = i * third_height
            for j in range(height):  # vertical lines
                canvas.SetPixel(line_x, j, 255, 255, 255)
            for k in range(width):  # horizontal lines
                canvas.SetPixel(k, line_y, 255, 255, 255)

    def draw_x(self, canvas, cx, cy, half_size, color):
        '''
        Draw an 'X' symbol on the canvas.

        Args:
            canvas: The drawing surface on which to draw the 'X' symbol.
            cx: The x-coordinate of the center of the 'X' symbol.
            cy: The y-coordinate of the center of the 'X' symbol.
            half_size: Half the size of the 'X' symbol, determining its length from the center to the ends.
            color: A tuple representing the RGB color values (e.g., (255, 0, 0) for red).
        '''
        for i in range(-half_size, half_size + 1):
            if 0 <= cx + i < self.matrix.width:
                if 0 <= cy + i < self.matrix.height:
                    # diagonal line from bottom-left to top-right
                    canvas.SetPixel(cx + i, cy + i, *color)
                if 0 <= cy - i < self.matrix.height:
                    # diagonal line from top-left to bottom-right
                    canvas.SetPixel(cx + i, cy - i, *color)

    def draw_o(self, canvas, cx, cy, radius, color):
        '''
        Draw an 'O' symbol on the canvas.
        '''
        x = radius
        y = 0
        radius_error = 1 - x

        # Loop to draw the circle using the midpoint circle algorithm
        while x >= y:
            for points in [
                (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                (cx + y, cy - x), (cx - y, cy - x)
            ]:
                px, py = points
                if (0 <= px < self.matrix.width
                        and 0 <= py < self.matrix.height):
                    canvas.SetPixel(px, py, *color)

            y += 1
            if radius_error < 0:
                radius_error += 2 * y + 1
            else:
                x -= 1
                radius_error += 2 * (y - x + 1)

    def highlight_cell(self, canvas, row, col, color, half_size):
        '''
        Highlight the selected cell with crosshairs or the symbol.
        '''
        width = self.matrix.width
        height = self.matrix.height
        third_width = width // 3
        third_height = height // 3
        cell_width_start = col * third_width
        cell_height_start = row * third_height
        cx = cell_width_start + third_width // 2
        cy = cell_height_start + third_height // 2

        # If the cell is empty, draw crosshairs
        if self.grid[row][col] is None:
            crosshair_color = (100, 100, 100)
            crosshair_length = min(third_width, third_height) // 4

            # Draw horizontal crosshair
            for i in range(cx - crosshair_length, cx + crosshair_length + 1):
                if 0 <= i < width:
                    canvas.SetPixel(i, cy, *crosshair_color)

            # Draw vertical crosshair
            for j in range(cy - crosshair_length, cy + crosshair_length + 1):
                if 0 <= j < height:
                    canvas.SetPixel(cx, j, *crosshair_color)

            # Draw inner square
            inner_square_size = min(third_width, third_height) // 8
            inner_square_color = (100, 100, 100)
            for i in range(cx - inner_square_size, cx + inner_square_size + 1):
                for j in range(cy - inner_square_size,
                               cy + inner_square_size + 1):
                    if 0 <= i < width and 0 <= j < height:
                        if i in (cx - inner_square_size, cx + inner_square_size
                                 ) or j in (cy - inner_square_size,
                                            cy + inner_square_size):
                            canvas.SetPixel(i, j, *inner_square_color)
        # If the cell is not empty, draw the symbol in another color
        else:
            symbol = self.grid[row][col]
            if symbol == "X":
                self.draw_x(canvas, cx, cy, half_size, (255, 0, 255))
            elif symbol == "O":
                self.draw_o(canvas, cx, cy, half_size, (0, 255, 255))

    def highlight_winning_line(self, canvas, winning_line, color1, color2):
        '''
        Highlight the winning line on the canvas.

        Args:
            self: The instance who calls the function.
            canvas: Drawing surface.
            winning_line: List of tuples with coordinates of the winning line.
            color1: RGB color tuple for the start of the gradient.
            color2: RGB color tuple for the end of the gradient.
        '''
        # Print for debugging purposes
        print(f"Highlighting winning line: {winning_line}")

        # Iterate through each cell in the winning line
        for i, (row, col) in enumerate(winning_line):
            # Calculate the x and y- cell center coordinates
            cx = col * (self.matrix.width // 3) + (self.matrix.width // 3) // 2
            cy = row * (self.matrix.height // 3) + (self.matrix.height //
                                                    3) // 2

            # Check if the cell contains an 'X'
            if self.grid[row][col] == "X":
                # Draw the 'X' symbol with a gradient effect
                for j in range(-(self.matrix.width // 12),
                               (self.matrix.width // 12) + 1):
                    # Check if the pixel is within the bounds of the matrix
                    if (0 <= cx + j < self.matrix.width
                            and 0 <= cy + j < self.matrix.height):
                        # Set the pixel for the diagonal from bottom-left to top-right
                        gradient_color = color1 if j < 0 else color2
                        canvas.SetPixel(cx + j, cy + j, *gradient_color)
                    # Check if the pixel is within the bounds of the matrix
                    if (0 <= cx + j < self.matrix.width
                            and 0 <= cy - j < self.matrix.height):
                        # Set the pixel for the diagonal from top-left to bottom-right
                        gradient_color = color1 if j < 0 else color2
                        canvas.SetPixel(cx + j, cy - j, *gradient_color)

            # Check if the cell contains an 'O'
            elif self.grid[row][col] == "O":
                # Define the radius for drawing the 'O' symbol
                radius = (self.matrix.width // 3) // 4
                x = radius
                y = 0
                radius_error = 1 - x

                # Draw the circle using the midpoint circle algorithm
                while x >= y:
                    # Calculate the interpolation factor for the gradient color
                    mix_factor = y / radius
                    # Interpolate between color1 and color2
                    current_color = tuple(
                        int(color1[k] * (1 - mix_factor) +
                            color2[k] * mix_factor) for k in range(3))
                    # Draw the circle points using symmetry
                    for points in [(cx + x, cy + y), (cx - x, cy + y),
                                   (cx + x, cy - y), (cx - x, cy - y),
                                   (cx + y, cy + x), (cx - y, cy + x),
                                   (cx + y, cy - x), (cx - y, cy - x)]:
                        px, py = points
                        # Check if the pixel is within the bounds of the matrix
                        if (0 <= px < self.matrix.width
                                and 0 <= py < self.matrix.height):
                            # Set the pixel with the current interpolated color
                            canvas.SetPixel(px, py, *current_color)

                    # Update y and adjust the radius error
                    y += 1
                    if radius_error < 0:
                        radius_error += 2 * y + 1
                    else:
                        x -= 1
                        radius_error += 2 * (y - x + 1)

    def update_display(self, winning_line=None):
        '''
        Update the LED matrix display with the current state of the Tic-Tac-Toe game.

        Args:
            self: The instance who calls the function.
            winning_line: List of tuples with coordinates of the winning line. (Optional)
        '''
        # Create a new canvas and draw the Tic-Tac-Toe grid
        offset_canvas = self.matrix.CreateFrameCanvas()
        self.draw_grid(offset_canvas)

        # Get the dimensions of the matrix display
        width = self.matrix.width
        height = self.matrix.height
        # Calculate the width and height of each grid cell
        third_width = width // 3
        third_height = height // 3
        # Calculate the radius and half size for the symbols
        radius = min(third_width, third_height) // 4
        half_size = radius

        # Iterate through the grid and draw 'X' or 'O' symbols
        for row in range(3):
            for col in range(3):
                # Calculate the center coordinates of the current cell
                cx = col * third_width + third_width // 2
                cy = row * third_height + third_height // 2
                if self.grid[row][col] == "X":
                    # Draw 'X' symbol at the center of the cell
                    self.draw_x(offset_canvas, cx, cy, half_size, (255, 0, 0))
                elif self.grid[row][col] == "O":
                    # Draw 'O' symbol at the center of the cell
                    self.draw_o(offset_canvas, cx, cy, radius, (0, 255, 0))

        # If there is a winning line, highlight it
        if winning_line:
            print(f"Drawing winning line: {winning_line}")
            self.highlight_winning_line(offset_canvas, winning_line,
                                        (255, 0, 255), (0, 255, 255))
        else:
            # Highlight the current cell position if there is no winning line
            current_row, current_col = self.current_position
            self.highlight_cell(offset_canvas, current_row, current_col,
                                (50, 50, 50), half_size)

        # Swap the canvas to update the display with the new frame
        self.matrix.SwapOnVSync(offset_canvas)

    def move_next(self, direction):
        '''
        Move to the next cell on the Tic-Tac-Toe grid, based on the given direction.

        Args:
            self: The instance who calls the function.
            direction: The direction to move ('UP', 'DOWN', 'LEFT', 'RIGHT', 'RIGHT_UP', 'LEFT_UP', 'RIGHT_DOWN', 'LEFT_DOWN').
        '''
        # Get the current position
        row, col = self.current_position

        # Move the position based on the given direction
        if direction == 'UP':
            # Move up if not at the top row
            if row > 0:
                row -= 1
        elif direction == 'DOWN':
            # Move down if not at the bottom row
            if row < 2:
                row += 1
        elif direction == 'LEFT':
            # Move left if not at the leftmost column
            if col > 0:
                col -= 1
        elif direction == 'RIGHT':
            # Move right if not at the rightmost column
            if col < 2:
                col += 1
        elif direction == 'RIGHT_UP':
            # Move diagonally right and up if not at the rightmost column and not at the top row
            if col < 2 and row > 0:
                col += 1
                row -= 1
        elif direction == 'LEFT_UP':
            # Move diagonally left and up if not at the leftmost column and not at the top row
            if col > 0 and row > 0:
                col -= 1
                row -= 1
        elif direction == 'RIGHT_DOWN':
            # Move diagonally right and down if not at the rightmost column and not at the bottom row
            if col < 2 and row < 2:
                col += 1
                row += 1
        elif direction == 'LEFT_DOWN':
            # Move diagonally left and down if not at the leftmost column and not at the bottom row
            if col > 0 and row < 2:
                col -= 1
                row += 1

        # Update the current position with the new values
        self.current_position = (row, col)
        # Refresh the display to reflect the new position
        self.update_display()

    def run(self):
        '''
        Run the Tic-Tac-Toe game loop.
        '''
        setup_gpio(self)
        self.update_display()

        try:
            while True:
                update_button_states(self)

                if self.game_over:
                    sleep(1)
                    self.exit_cleanly()
                    continue

                tilt_direction, magnitude = get_tilt_direction()
                if tilt_direction != 'NONE':
                    setVibrator(0.1)
                    self.move_next(tilt_direction)
                    sleep(0.2)

                if (self.blue_button == GPIO.LOW
                        and not self.red_button == GPIO.LOW):
                    payload = {
                        "grid": self.grid,
                        "current_player": "X",
                        "move": self.current_position
                    }

                    self.mqtt_client.publish(TOPIC_QUERY, payload)
                    response = self.mqtt_client.get_response()

                    if response["status"] == "move":
                        self.grid = response["grid"]
                        self.current_position = response["next_move"]
                        self.update_display()

                    elif response["status"] == "win":
                        self.grid = response["grid"]
                        winning_line = response.get("winning_line", [])
                        print("This is winning line: ", winning_line)
                        self.update_display(winning_line)
                        setVibrator(1.2)
                        self.game_over = True
                        print(f"Player {response['winner']} wins!")

                    elif response["status"] == "draw":
                        self.grid = response["grid"]
                        self.update_display()
                        setVibrator(1.2)
                        self.game_over = True
                        print("The game is a draw!")

                if (self.blue_button == GPIO.LOW
                        and self.red_button == GPIO.LOW):
                    self.__init__()
                    self.update_display()
                    sleep(0.3)

                if (self.red_button == GPIO.LOW
                        and self.blue_button != GPIO.LOW):
                    self.exit_cleanly()

                sleep(0.1)

        except KeyboardInterrupt:
            print("\nProgram exited by interrupt.")
        finally:
            GPIO.cleanup()

    def exit_cleanly(self):
        '''
        Exits the game cleanly and raises an exit exception.
        '''
        GPIO.cleanup()
        sleep(0.3)
        raise GameExit


if __name__ == "__main__":
    tic_tac_toe_with_buttons = TicTacToeGame()
    if not tic_tac_toe_with_buttons.process():
        tic_tac_toe_with_buttons.print_help()
