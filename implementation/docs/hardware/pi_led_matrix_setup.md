# LED Matrix Setup

## Specifications

- **Supply Voltage:** 5V / approximately 4A per LED matrix
- **Maximum Consumption:** 40W
- **Resolution:** 64 x 64
- **Number of LEDs:** 4096

## Connecting the Hardware

1. **Connect LED Power Cable:**
   - Connect the power cable to the LED matrix.
   - Connect the power cable to the power supply.
2. **Connect HUB75 Connector:**
   - Use a ribbon cable to connect the HUB75 connector to the IN port on the matrix.
3. **Connect Pins to Raspberry Pi:**
   - Refer to Reference 2 for GPIO and IN diagram.
   - All connector cables (16) are needed except N.
   - LE is E, LA is A, LB is B, LC is C, LD is D.

## Setting up & Testing the Software

1. **Disable Audio Module:**
   - `sudo nano /boot/firmware/config.txt`
   - Change `dtparam=audio=on` to `dtparam=audio=off`
   - Reboot and run `lsmod` to check for `snd_bcm2835`. If present, run:

    ```bash
    cat <<EOF | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf
    blacklist snd_bcm2835
    EOF

    sudo update-initramfs -u
    ```

   - Reboot.
2. **Install Matrix Packages:** Refer to Reference 2. Only Matrix 1 is used.
3. **Install Python Packages:** Refer to Reference 2.

4. **Build and Install Python Packages:**

  ```bash
  cd ~/rpi-rgb-led-matrix
  make build-python
  sudo make install-python
  sudo setcap 'cap_sys_nice=eip' /usr/bin/python3.11
  ```

5. **Activate Virtual Environment:**
  `source venv/bin/activate`

6. **Test Commands:**

```bash
sudo ~/rpi-rgb-led-matrix/examples-api-use/demo -D 0 --led-rows=64 --led-cols=64 --led-slowdown-gpio=4
sudo ~/rpi-rgb-led-matrix/examples-api-use/scrolling-text-example --led-rows=64 --led-cols=64 --led-slowdown-gpio=4 -f ~/LED_props/cherry-10-b.bdf Hallo Welt!
sudo ~/rpi-rgb-led-matrix/examples-api-use/text-example -f ~/LED_props/cherry-10-b.bdf --led-rows=64 --led-cols=64
python3 ~/rpi-rgb-led-matrix/bindings/python/samples/simple-square.py --led-no-hardware-pulse=true --led-cols=64 --led-rows=64 --led-slowdown-gpio=4
sudo python3 ~/rpi-rgb-led-matrix/bindings/python/samples/image-viewer.py ~/LED_props/Wikipedia_Logo.png --led-cols=64 --led-rows=64 --led-slowdown-gpio=4
python3 ~/rpi-rgb-led-matrix/bindings/python/samples/main-gyro.py --led-no-hardware-pulse=true --led-rows=64 --led-cols=64 --led-slowdown-gpio=5
```

## References and Ressources

1. [LED-Matrix Datasheet](https://joy-it.net/files/files/Produkte/LED-Matrix01/LED-Matrix01_Datasheet_2022-07-25.pdf)
2. [LED-Matrix Manual](https://joy-it.net/files/files/Produkte/RB-MatrixCtrl/RB-MatrixCtrl_Manual_2021-08-05.pdf)
3. [LED-Matrix-Controllboard Datasheet](https://cdn-reichelt.de/documents/datenblatt/A300/DATASHEETRB-MATRIXCTRL.pdf)
4. [LED-Matrix-Controllboard Manual](https://cdn-reichelt.de/documents/datenblatt/A300/RB-MATRIXCTRL-ANLEITUNG.pdf)
5. [RGBMatrixEmulator](https://pypi.org/project/RGBMatrixEmulator/) / [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)
6. [Connect LED-Panel with PI](https://howchoo.com/pi/raspberry-pi-led-matrix-panel/)
