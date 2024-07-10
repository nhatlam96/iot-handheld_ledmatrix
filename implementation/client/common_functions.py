import RPi.GPIO as GPIO
from rgbmatrix import graphics
from os import path


class GameExit(Exception):
    pass


def update_button_states(self):
    """
    Updates the input states of the button variables: blue_button & red_button.

    Args:
        self: The instance who calls the function.
    """
    try:
        self.blue_button = GPIO.input(26)
        self.red_button = GPIO.input(16)
    except Exception as e:
        print(f"Error: {e}")


def clear_display(self, canvas):
    """
    Clears and updates the canvas.

    Args:
        self: The instance who calls the function.
        canvas: Drawing surface where the clear will be rendered.
    """

    try:
        canvas.Clear()
        self.matrix.SwapOnVSync(canvas)
    except Exception as e:
        print(f"Error: {e}")


def setup_gpio(self):
    """
    Sets the GPIO Mode to BCM, defines button pins and vibrator.

    Args:
        self: The instance who calls the function.
    """

    try:
        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.OUT)  # Vibrator
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Red button
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Blue button
    except Exception as e:
        print(f"Error: {e}")


def draw_centered_text(self, canvas, font, y, color, text, line_spacing=1):
    """
    Draws given text centered on the canvas. If text contains \\n newline,
    it will be split into multiple lines.

    Args:
        self: The instance who calls the function.
        canvas: Drawing surface where text will be rendered.
        font: Font used for the text.
        y: Coordinate (vertical position) where the text will start.
        color: Color of the text.
        text: String to be drawn. Can contain multiple lines separated by \\n.
        line_spacing: Multiplier for the space between lines (default is 1).
    """

    try:
        lines = text.split('\n')

        for i, line in enumerate(lines):
            # Calc y for current line
            current_y = y + i * font.height * line_spacing
            # Calc width for current line
            text_width = sum(font.CharacterWidth(ord(char)) for char in line)
            # Calc x start pos for centering
            x = (canvas.width - text_width) // 2
            graphics.DrawText(canvas, font, x, current_y, color, line)
    except Exception as e:
        print(f"Error: {e}")


def load_font(self,
              font_path='/home/pi/rpi-rgb-led-matrix/fonts/',
              font_name="5x8.bdf"):
    """
    Return font parameter with assigned and loaded font.

    Args:
        self: The instance who calls the function.
        font_path: Absolute path to font to be loaded.
        font_name: Name of the font, which is found in font_path.
    """

    try:
        full_font_path = path.join(font_path, font_name)
        font = graphics.Font()
        font.LoadFont(full_font_path)
        return font
    except Exception as e:
        print(f"Error: {e}")


def draw_rectangle_borders(self,
                           canvas,
                           x,
                           y,
                           width,
                           height,
                           border_thickness=4):
    """
    Draws a rectangle with a specified border thickness on the canvas.

    Args:
        self: The instance who calls the function.
        canvas: Drawing surface where rectangle will be rendered.
        x: x-Coordinate of top-left corner of the rectangle.
        y: y-Coordinate of top-left corner of the rectangle.
        width: Width of the rectangle.
        height: Height of the rectangle.
        border_thickness: Thickness of the rectangle's border (default 1 px).
    """

    try:
        rainbow_colors = [
            graphics.Color(255, 0, 0),       # Red
            graphics.Color(255, 165, 0),     # Orange
            graphics.Color(255, 255, 0),     # Yellow
            graphics.Color(0, 255, 0),       # Green
        ]

        # Draw diffrent colored borders
        for i in range(border_thickness):
            # Cycle through rainbow colors
            color_index = i % len(rainbow_colors)
            border_color = rainbow_colors[color_index]

            # Top border
            graphics.DrawLine(canvas, x, y + i, x + width - 1, y + i,
                              border_color)
            # Bottom border
            graphics.DrawLine(canvas, x, y + height - 1 - i, x + width - 1,
                              y + height - 1 - i, border_color)
            # Left border
            graphics.DrawLine(canvas, x + i, y, x + i, y + height - 1,
                              border_color)
            # Right border
            graphics.DrawLine(canvas, x + width - 1 - i, y, x + width - 1 - i,
                              y + height - 1, border_color)
    except Exception as e:
        print(f"Error: {e}")
