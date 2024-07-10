import RPi.GPIO as GPIO
from time import sleep


def setVibrator(sec: float) -> None:
    """
    Activates the vibrator for a specified duration.

    Args:
        sec (float): Duration in seconds for which the vibrator will be active.
    """

    try:
        GPIO.output(5, GPIO.HIGH)
        sleep(sec)  # Vibrator active for specified duration
        GPIO.output(5, GPIO.LOW)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.output(5, GPIO.LOW)


if __name__ == "__main__":
    from common_functions import setup_gpio
    setup_gpio()

    try:
        setVibrator(1.5)
    except KeyboardInterrupt:
        print("\nProgram exited by interrupt.")
    finally:
        GPIO.cleanup()
