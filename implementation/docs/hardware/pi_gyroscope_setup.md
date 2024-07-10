# Gyroscope Setup

## Remarks

- The LED on the gyroscope should light up, indicating it is correctly connected.

## Specifications

- **Chipsets:**
  - MS5611 (Barometer)
  - HMC5883L (3-Axis Magnetometer)
  - MPU6050 (3-Axis Gyroscope & Triaxial Accelerometer)
- **Communication:** I2C Interface
- **Power Supply:** 3-5V

## RaspberryPi software config

- Enable I2C
  - Run `sudo raspi-config`
  - Interface Options -> I2C -> Enable
  - Follow the tutorial (Reference 3), but use Python 3 and install GPIO with `sudo apt install python3-rpi.gpio pigpio python3-pigpio`.

## Connecting the hardware

- Connect VCC_IN to 3V (Pin 1)
- Connect GND to GND (Pin 9)
- Connect SCL to GPIO 3 (SCL, Pin 5)
- Connect SDA to GPIO 2 (SDA, Pin 3)
- Note: Pins used: 1 (3V), 5 (SCL), 9 (GND), 3 (SDA)

## Testing

- Test if the gyroscope is correctly connected with `sudo i2cdetect -y 1`

## References and Ressources

1. [Gyroscope Datasheet](https://www.berrybase.de/Pixelpdfdata/Articlepdf/id/4639/onumber/GY-86)
2. [Gyroscope python lib smbus2](https://pypi.org/project/smbus2/)
3. [Gyroscope Tutorial for RaspberryPi](https://www.raspberrypistarterkits.com/guide/raspberry-pi-accelerometer-gyroscope/)
4. [How to use gyrosope in python](https://www.electronicwings.com/raspberry-pi/mpu6050-accelerometergyroscope-interfacing-with-raspberry-pi)
