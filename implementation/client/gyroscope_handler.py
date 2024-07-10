import smbus
from time import sleep

# Some MPU6050 Registers and their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# MPU6050 device address
Device_Address = 0x68

# Initialize SMBus
bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards


def MPU_Init():
    """
    Initialize the MPU6050 sensor.
    """

    # Write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    # Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)
    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    # Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):
    """
    Read raw data from the given address.

    Args:
        addr: The register address to read data from.

    Returns:
        The raw sensor value.
    """

    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    # Concatenate higher and lower value
    value = ((high << 8) | low)
    # Get signed value from mpu6050 with concat value
    if (value > 32768):
        value = value - 65536
    return value


def get_sensor_data():
    """
    Get accelerometer and gyroscope data.

    Returns:
        Accelerometer and gyroscope data in form:
        Ax, Ay, Az, Gx, Gy, Gz
    """

    gyro_x = read_raw_data(ACCEL_XOUT_H)
    gyro_y = read_raw_data(ACCEL_YOUT_H)
    gyro_z = read_raw_data(ACCEL_ZOUT_H)
    acc_x = read_raw_data(GYRO_XOUT_H)
    acc_y = read_raw_data(GYRO_YOUT_H)
    acc_z = read_raw_data(GYRO_ZOUT_H)

    Ax = acc_x / 131.0
    Ay = acc_y / 131.0
    Az = acc_z / 131.0
    Gx = gyro_x / 16384.0
    Gy = gyro_y / 16384.0
    Gz = gyro_z / 16384.0

    return Ax, Ay, Az, Gx, Gy, Gz


def get_tilt_direction():
    """
    Determine the tilt direction based on gyroscope data.

    Returns:
        Tilt direction and its magnitude in form:
        direction, tilt_magnitude
    """

    try:
        Ax, Ay, Az, Gx, Gy, Gz = get_sensor_data()

        # Calculate tilt magnitude
        tilt_magnitude = max(abs(Gx), abs(Gy))

        # Decide the direction
        if Gx >= 0.3 and Gy < 0.2 and Gy > -0.2:
            return "RIGHT", tilt_magnitude
        elif Gx <= -0.3 and Gy < 0.2 and Gy > -0.2:
            return "LEFT", tilt_magnitude
        elif Gy >= 0.3 and Gx < 0.2 and Gx > -0.2:
            return "UP", tilt_magnitude
        elif Gy <= -0.3 and Gx < 0.2 and Gx > -0.2:
            return "DOWN", tilt_magnitude
        elif (Gx >= 0.2 and Gy >= 0.2):
            return "RIGHT_UP", tilt_magnitude
        elif (Gx <= -0.2 and Gy >= 0.2):
            return "LEFT_UP", tilt_magnitude
        elif (Gx >= 0.2 and Gy <= -0.2):
            return "RIGHT_DOWN", tilt_magnitude
        elif (Gx <= -0.2 and Gy <= -0.2):
            return "LEFT_DOWN", tilt_magnitude
        else:
            return "NONE", 0
    except Exception as e:
        print(f"Error: {e}")


MPU_Init()

if __name__ == "__main__":
    try:
        while True:
            directionReturn, tilt_magnitude = get_tilt_direction()
            if directionReturn != "NONE":
                Ax, Ay, Az, Gx, Gy, Gz = get_sensor_data()
                print(
                    f"\033[1;33m{directionReturn}\033[0m\t"
                    f"\033[1;33mGx= \033[34m{Gx:.2f}\033[0mg\t",
                    f"\033[1;33mGy= \033[34m{Gy:.2f}\033[0mg\t",
                    f"\033[1;33mGz= \033[34m{Gz:.2f}\033[0mg"
                )
                sleep(1)
            sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram exited by interrupt.")
