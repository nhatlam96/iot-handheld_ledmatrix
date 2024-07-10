# First time pigame setup

1. `ssh pi@ip` pw: `wasd1234`
2. Copy files from `/raspverrypi/*` to `pi@ip:/home/pi/`
3. `sudo apt update && sudo apt install python3-pip mosquitto mosquitto-clients -y`
4. `pip install -r requirements.txt`

# Run pigames

1. `source ~/venv/bin/activate && python3 ~/rpi-rgb-led-matrix/bindings/python/samples/menu.py --led-no-hardware-pulse=true --led-rows=64 --led-cols=64 --led-slowdown-gpio=5`
