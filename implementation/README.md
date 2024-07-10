# File structure of the implementation

## Hardware documentation

- In the *docs/hardware* directory, you will find:
  - Setup instructions for the hardware
  - Which pins are used by which hardware
  - Autodesk Fusion files for the case
- All used hardware is found in the README.md in the base dir

## Software documentation

- In the *docs/software* directory, you will find
  - Setup instructions for the needed packages and modules
  - Setup instructions for the PI including
    - Enabling I2C
    - Setting up WLAN
  - How to create a service for running python scripts automaticly
  - How to run the pygame scripts (parameters)
  - How to setup and run the MQTT server

## Case files

- In the *case* directory, you will find the Autodesk Fusion files for the case
- With the following link, you can access the case in the browser: [Case](http://a360.co/3QWGV2a)

## Client files

- In the *client* directory, you will find the client code that are run by the raspberry pi

## Server files

- In the *server* directory, you will find the server code that are run by the VM and docker
- the adress of the server is: `electronicaemporium@iot.it.hs-worms.de`
  - (check implementation/docs/software/setup_&_start_mqtt_docker.md for more information)
