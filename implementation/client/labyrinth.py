import RPi.GPIO as GPIO
from time import sleep
from random import shuffle, random
from samplebase import SampleBase
from rgbmatrix import graphics
from vibrator import setVibrator
from gyroscope_handler import get_tilt_direction
from common_functions import (
    clear_display,
    setup_gpio,
    draw_centered_text,
    load_font,
    GameExit,
    update_button_states
)
from mqtt_client import MQTTClient

# MQTT Broker details
TOPIC_QUERY = "labyrinth/query"
TOPIC_RESPONSE = "labyrinth/response"


class LabyrinthGame(SampleBase):
    """
    Main class for the labyrinth game.
    """

    def __init__(self, *args, **kwargs):
        super(LabyrinthGame, self).__init__(*args, **kwargs)

        # Initialize MQTT client
        self.mqtt_client = MQTTClient(TOPIC_QUERY, TOPIC_RESPONSE)

        # LED panel size in pixels
        self.led_pixel_x = 64
        self.led_pixel_y = 64

        # Cell size in pixels
        self.game_cell_size = 4

        # Game dimensions in cells (16x16 cells)
        self.game_dimension_x = int(self.led_pixel_x / self.game_cell_size)
        self.game_dimension_y = int(self.led_pixel_y / self.game_cell_size)

        # Game-specific variables
        # Exit postion is bottom-left
        self.exit_position = (0, self.game_dimension_y - 1)
        # Start position is top-right
        self.start_position = (self.game_dimension_x - 1, 0)
        # Player's starting position
        self.current_position = self.start_position
        self.game_over = False
        self.game_won = False

        # Request maze from server via MQTT
        self.grid, self.deadlyWalls = self.request_maze_from_server(self.game_dimension_x,
                                                                    self.game_dimension_y,
                                                                    self.exit_position,
                                                                    self.start_position
                                                                    )

        # GPIO setup
        setup_gpio(self)

        # Font setup
        self.font = load_font(self)
        # Yellow text color
        self.text_color = graphics.Color(200, 200, 0)
        # Black for paths
        self.bg_color = graphics.Color(0, 0, 0)
        # White for walls
        self.bg_alt_color = graphics.Color(255, 255, 255)
        # Orange for deadly walls
        self.bg_deadly_wall_color = graphics.Color(187, 69, 111)
        # Green for the player
        self.player_colour = graphics.Color(0, 255, 0)
        # Red for the exit
        self.exit_positon_colour = graphics.Color(255, 0, 0)

        # Button states setup
        self.blue_button = None
        self.red_button = None
        update_button_states(self)

    def request_maze_from_server(self, width, height, exit_position, start_position):
        '''
        Request maze generation from the server via MQTT.

        Args:
            self: The instance who calls the function.
            width (int): Width of maze in cells.
            height (int): Height of maze in cells.

        Returns:
            list: Generated maze with walls (1) and paths (0).
        '''

        request = {'width': width, 'height': height,
                   'exit_position': exit_position,
                   'start_position': start_position}
        self.mqtt_client.publish(TOPIC_QUERY, request)
        response = self.mqtt_client.get_response()
        fixedWalls = [tuple(sublist) for sublist in response['deadlyWalls']]
        return response['maze'], fixedWalls

    def draw_grid(self, canvas):
        '''
        Draws the maze grid, player and exit position of the canvas.

        Args:
            self: The instance who calls the function.
            canvas: Drawing suface.

        Returns:
            list: Generated maze with walls (1) and paths (0).
        '''

        # Iterates over each cell in the grid
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                # If the current cell is in deadly walls
                if (x, y) in self.deadlyWalls:
                    # Set it's colour as deadly wall
                    color = self.bg_deadly_wall_color
                # If the current cell is a wall
                elif self.grid[y][x] == 1:
                    # Set it's colour as normal wall
                    color = self.bg_alt_color
                # Otherwise, set it's colour as a path
                else:
                    color = self.bg_color

                # Draw each cell as the appropriate size (game_cell_size)
                # dy and dx are offsets within each cell
                for dy in range(self.game_cell_size):
                    for dx in range(self.game_cell_size):
                        # Sets the Pixel at the current positon
                        canvas.SetPixel(x * self.game_cell_size + dx,
                                        y * self.game_cell_size + dy,
                                        color.red, color.green, color.blue)

        # Get current position of the player
        cx, cy = self.current_position

        # Draw the current position of the player
        # dy and dx are offsets within the player cell
        for dy in range(self.game_cell_size):
            for dx in range(self.game_cell_size):
                # Sets the Pixel at the current position
                canvas.SetPixel(cx * self.game_cell_size + dx,
                                cy * self.game_cell_size + dy,
                                self.player_colour.red,
                                self.player_colour.green,
                                self.player_colour.blue)

        # Get position of the exit
        ex, ey = self.exit_position

        # Draw the exit position
        # dy and dx are offsets within the exit cell
        for dy in range(self.game_cell_size):
            for dx in range(self.game_cell_size):
                # Sets the Pixel at the current position
                canvas.SetPixel(ex * self.game_cell_size + dx,
                                ey * self.game_cell_size + dy,
                                self.exit_positon_colour.red,
                                self.exit_positon_colour.green,
                                self.exit_positon_colour.blue)

    def update_display(self, canvas, message=None):
        '''
        Updates the display on the canvas.
        If a message is provided, display it centered.

        Args:
            self: The instance who calls the function.
            canvas: Drawing surface.
            message (str): Message to be displayed (optional).
        '''

        # Draws current state of the maze on the canvas
        self.draw_grid(canvas)
        # If message is provided
        if message:
            canvas.Clear()
            # Draw the message as centered text
            draw_centered_text(self, canvas, self.font, 20, self.text_color,
                               message)
        # Update display with newly drawn canvas
        self.matrix.SwapOnVSync(canvas)

    def move_player(self, canvas, direction):
        '''
        Move the player in specified direction, if the move is valid.
        Updates the position and display on the canvas.

        Args:
            self: The instance who calls the function.
            canvas: Drawing surface.
            direction (str): The direction in which the player wants to move.
        '''

        # Get's current player positon
        x, y = self.current_position
        # Initializes copy of current player positoin
        new_x, new_y = x, y

        # If moving up is within bounds
        if direction == 'UP' and y > 0:
            # If target cell is deadly wall
            if (x, y - 1) in self.deadlyWalls:
                self.game_over = True
            # If target cell is wall or exit position
            elif self.grid[y - 1][x] == 0 or (x + 1, y) == self.exit_position:
                new_y -= 1
        # If moving down is within bounds
        elif direction == 'DOWN' and y < len(self.grid) - 1:
            # If target cell is deadly wall
            if (x, y + 1) in self.deadlyWalls:
                self.game_over = True
            # If target cell is a wall or exit position
            elif self.grid[y + 1][x] == 0 or (x, y + 1) == self.exit_position:
                new_y += 1
        # If moving left is within bounds
        elif direction == 'LEFT' and x > 0:
            # If target cell is deadly wall
            if (x - 1, y) in self.deadlyWalls:
                self.game_over = True
            # If target cell is a wall or exit position
            elif self.grid[y][x - 1] == 0 or (x + 1, y) == self.exit_position:
                new_x -= 1
        # If moving right is within bounds
        elif direction == 'RIGHT' and x < len(self.grid[0]) - 1:
            # If target cell is deadly wall
            if (x + 1, y) in self.deadlyWalls:
                self.game_over = True
            # If target cell is a wall or exit position
            if self.grid[y][x + 1] == 0 or (x + 1, y) == self.exit_position:
                new_x += 1

        # If game is not over
        if not self.game_over:
            # Set new postion to current
            self.current_position = (new_x, new_y)
            self.update_display(canvas)

    def run(self):
        '''
        Main method of the game.
        Handels the game flow, including initializing the game,
        updating the display, handling user input and
        managing the game state (win, loss, restart).

        Args:
            self: The instance who calls the function.
        '''

        # Initial setup of game loop
        setup_gpio(self)
        # Create new canvas
        canvas = self.matrix.CreateFrameCanvas()
        # Update display with initial state of game
        self.update_display(canvas)

        try:
            game_over_message_shown = False

            while True:
                update_button_states(self)

                if self.game_won:
                    if not game_over_message_shown:
                        self.update_display(canvas, "You won!")
                        game_over_message_shown = True
                        setVibrator(1.2)
                        sleep(1)
                    if game_over_message_shown:
                        self.exit_cleanly(canvas)
                    sleep(0.3)
                    continue

                if self.game_over:
                    game_over_message_shown = self.restart_game(canvas,
                                                                "Gameover!")
                    sleep(0.3)
                    continue

                # If both buttons are pressed
                if (self.blue_button == GPIO.LOW and
                   self.red_button == GPIO.LOW):
                    game_over_message_shown = self.restart_game(canvas,
                                                                "Restarting!")
                    sleep(0.3)

                # Get tilt direction and magnitue of the game board
                tilt_direction, tilt_magnitude = get_tilt_direction()

                # If tilt direction is not none
                if tilt_direction != 'NONE':
                    # Constrain the speed_factor min 0.1 and max 1
                    speed_factor = max(0.1, min(1, tilt_magnitude))
                    # Calculate the sleep_time via speed factor
                    sleep_time = 0.1 * (1 - speed_factor)

                    self.move_player(canvas, tilt_direction)
                    if self.current_position == self.exit_position:
                        self.game_won = True
                        game_over_message_shown = False
                        sleep(1)

                    # Sleep based on sleep_facor
                    sleep(sleep_time)

                # If blue button, but not red button is pressed
                if (self.blue_button == GPIO.LOW and
                   self.red_button != GPIO.LOW):
                    sleep(0.3)

                # If red button, but not blue button is pressed
                if (self.red_button == GPIO.LOW and
                   self.blue_button != GPIO.LOW):
                    setVibrator(0.1)
                    self.exit_cleanly(canvas)

                sleep(0.1)

        except KeyboardInterrupt:
            print("\nProgram exited by interrupt.")

        finally:
            GPIO.cleanup()

    def exit_cleanly(self, canvas):
        '''
        Exits the game cleanly, displays a exit message,
        cleans up the display and raises a exit exception.

        Args:
            self: The instance who calls the function.
            canvas: Drawing surface.

        Raises:
            GameExit: Exception raised to cleanly exit the game.
        '''
        self.update_display(canvas, "Exiting!")
        sleep(1)
        clear_display(self, canvas)
        GPIO.cleanup()
        sleep(0.3)
        raise GameExit

    def restart_game(self, canvas, message):
        '''
        Restarts the game, displays a restart message,
        cleans up the display and reinitializes the game.

        Args:
            self: The instance who calls the function.
            canvas: Drawing surface.
            message (str): Message to be displayed.

        Return:
            bool: The status of the game_over_message.
        '''
        self.update_display(canvas, message)
        setVibrator(1.2)
        sleep(1)
        clear_display(self, canvas)
        self.__init__()
        self.update_display(canvas)
        game_over_message_shown = False
        return game_over_message_shown


if __name__ == "__main__":
    labyrinth_game = LabyrinthGame()
    if not labyrinth_game.process():
        labyrinth_game.print_help()
