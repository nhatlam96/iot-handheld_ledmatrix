# Service erstellen für pigame

1. `sudo nano /etc/systemd/system/pigame.service`
2. Insert and save:
    ```
    [Unit]
    Description=Run PiGame on boot
    After=network.target

    [Service]
    ExecStart=/bin/bash -c 'source /home/pi/venv/bin/activate && exec python3 /home/pi/rpi-rgb-led-matrix/bindings/python/samples/menu.py --led-no-hardware-pulse=true --led-rows=64 --led-cols=64 --led-slowdown-gpio=5'
    WorkingDirectory=/home/pi
    User=pi
    Group=pi
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
3. `sudo systemctl daemon-reload`
4. `sudo systemctl enable pigame.service`
5. `sudo systemctl start pigame.service`