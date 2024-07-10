import RPi.GPIO as GPIO
from time import sleep
from os import system
from samplebase import SampleBase
from rgbmatrix import graphics
from vibrator import setVibrator
from gyroscope_handler import get_tilt_direction
from labyrinth import LabyrinthGame
from tictactoe import TicTacToeGame
from common_functions import (
    clear_display,
    setup_gpio,
    draw_centered_text,
    load_font,
    draw_rectangle_borders,
    GameExit,
    update_button_states
)


class Menu(SampleBase):
    """
    Main class for the menu.
    """

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

        # LED panel size in pixels
        self.led_pixel_x = 64
        self.led_pixel_y = 64

        # Menu-specific variables
        self.options = ["TicTacToe", "Labyrinth", "Shutdown"]
        self.selected_option = 0
        self.game_running = False

        # GPIO setup
        setup_gpio(self)

        # Font setup
        self.font = load_font(self)
        # White text color
        self.text_color = graphics.Color(128, 128, 128)
        # Red alternate text color
        self.text_alt_color = graphics.Color(255, 0, 0)
        # Black background color
        self.bg_color = graphics.Color(0, 0, 0)

        # Button states
        self.blue_button = None
        self.red_button = None
        update_button_states(self)

    def draw_menu(self, canvas):
        '''
        Draws the menu, draws the border, displays all options and
        marks the selected option.

        Args:
            self: The instance who calls the function.
            canvas: Drawing suface.
        '''

        canvas.Clear()

        # Iterates over each pixel of the LED
        for y in range(self.led_pixel_y):
            for x in range(self.led_pixel_x):
                # Sets the Pixel at the current positon to background color
                canvas.SetPixel(x, y, self.bg_color.red, self.bg_color.green,
                                self.bg_color.blue)

        # Draws the border around the menu
        draw_rectangle_borders(self,
                               canvas,
                               0,
                               0,
                               self.led_pixel_x,
                               self.led_pixel_y,
                               border_thickness=4)

        # Iterates over menu options
        for i, option in enumerate(self.options):
            # Sets the color of menu items
            color = (self.text_alt_color
                     if i == self.selected_option else self.text_color)
            # Draws the menu options centered
            draw_centered_text(self, canvas, self.font,
                               15 if i == 0 else 12 + i * 20, color, option)

        # Update display with newly drawn canvas
        self.matrix.SwapOnVSync(canvas)

    def run(self):
        '''
        Main method of the menu.
        Handels the menu flow, including initializing the menu,
        updating the display and handling user input.

        Args:
            self: The instance who calls the function.
        '''

        # Initial setup of menu loop
        setup_gpio(self)
        # Create new canvas
        canvas = self.matrix.CreateFrameCanvas()
        # Update display with initial state of menu
        self.draw_menu(canvas)

        try:
            while True:
                if not self.game_running:
                    update_button_states(self)

                    # Get tilt direction and magnitue of the game board
                    tilt_direction, tilt_magnitude = get_tilt_direction()

                    # If tilt direction is up
                    if tilt_direction == 'UP':
                        # Set selected option to navigated option
                        self.selected_option = ((self.selected_option - 1) %
                                                len(self.options))
                        self.draw_menu(canvas)
                        setVibrator(0.1)
                        sleep(0.3)
                    # If tilt direction is down
                    elif tilt_direction == 'DOWN':
                        # Set selected option to navigated option
                        self.selected_option = ((self.selected_option + 1) %
                                                len(self.options))
                        setVibrator(0.1)
                        self.draw_menu(canvas)
                        sleep(0.3)

                    # If blue button is pressed
                    if self.blue_button == GPIO.LOW:
                        # If selected option is tictactoe
                        if self.selected_option == 0:
                            self.start_tictactoe(canvas)
                        # If selected option is labyrinth
                        elif self.selected_option == 1:
                            self.start_labyrinth(canvas)
                        # If selected option is shutdown
                        elif self.selected_option == 2:
                            self.pi_shutdown(canvas)
                            self.draw_menu(canvas)
                        sleep(0.3)

                    sleep(0.1)

        except GameExit:
            pass

        except KeyboardInterrupt:
            print("\nProgram exited by interrupt.")

        finally:
            GPIO.cleanup()

    def start_labyrinth(self, canvas):
        '''
        Starts the labyrinth game.
        Clears the display, runs the game and then returns to menu.

        Args:
            self: The instance who calls the function.
            canvas: Drawing suface.
        '''

        self.game_running = True
        clear_display(self, canvas)
        GPIO.cleanup()
        sleep(0.3)
        try:
            labyrinth_game = LabyrinthGame()
            labyrinth_game.process()
        except GameExit:
            pass
        finally:
            self.game_running = False
            setup_gpio(self)
            self.draw_menu(canvas)

    def start_tictactoe(self, canvas):
        '''
        Starts the tictactoe game.
        Clears the display, runs the game and then returns to menu.

        Args:
            self: The instance who calls the function.
            canvas: Drawing suface.
        '''

        self.game_running = True
        clear_display(self, canvas)
        GPIO.cleanup()
        sleep(0.3)
        try:
            ticTacToeGame = TicTacToeGame()
            ticTacToeGame.process()
        except GameExit:
            pass
        finally:
            self.game_running = False
            setup_gpio(self)
            self.draw_menu(canvas)

    def pi_shutdown(self, canvas):
        '''
        Starts the shutdown dialogue.
        Shows a confirm message and shuts down if confirmed.

        Args:
            self: The instance who calls the function.
            canvas: Drawing suface.
        '''

        confirmation_text = "Shutdown?\n\n[R] = NO \n[B] = YES"

        canvas.Clear()

        sleep(1.5)

        draw_centered_text(self, canvas, self.font, 20, self.text_color,
                           confirmation_text)
        self.matrix.SwapOnVSync(canvas)

        while True:
            update_button_states(self)

            if self.blue_button == GPIO.LOW and self.red_button != GPIO.LOW:
                GPIO.cleanup()
                sleep(1)
                system("sudo shutdown now")
                break
            if self.red_button == GPIO.LOW and self.blue_button != GPIO.LOW:
                break
            sleep(0.1)


if __name__ == "__main__":
    menu = Menu()
    if not menu.process():
        menu.print_help()
