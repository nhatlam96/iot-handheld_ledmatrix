# Setup & Start MQTT Docker

## First time server setup

1. Server
   1. `ssh electronicaemporium@iot.it.hs-worms.de` pw: `M!^!AqbNx89iMP`
   2. copy files from `/server/*` to `electronicaemporium@iot.it.hs-worms.de:/home/`

2. Docker (run commands on server)
   1. `docker stop electronicaemporium-mqtt && docker rm electronicaemporium-mqtt && docker rmi electronicaemporium-mqtt`
   2. `docker build -t electronicaemporium-mqtt /home/electronicaemporium/.`
   3. `docker run -it --name electronicaemporium-mqtt -u 0 -p 1885:1885 electronicaemporium-mqtt bash`
      - `mosquitto -c /etc/mosquitto/mosquitto.conf &`
   4. new terminal: `ssh electronicaemporium@iot.it.hs-worms.de` pw: `M!^!AqbNx89iMP`
      - `docker exec -it -u root electronicaemporium-mqtt bash`
      - `python3 mqtt_tictactoe.py`

## Start server

1. Server
   1. Connect to VPN or HS network
   2. `ssh electronicaemporium@iot.it.hs-worms.de` pw: `M!^!AqbNx89iMP`

2. Docker
   1. `docker exec -it -u root electronicaemporium-mqtt bash`
      1. `mosquitto -c /etc/mosquitto/mosquitto.conf`
      2. `python3 mqtt_master.py`
      3. THIS WONT WORK: `mosquitto -c /etc/mosquitto/mosquitto.conf && python3 mqtt_master.py`
         - You have to input these commands separately!
