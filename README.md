# Electronica Emporium

- N = Luong, Nhat-Lam
- P = Sandler, Paul
- NP = Both

## Individual and group work packages

- server:
  - N: .env (deleted secret), Dockerfile, mosquitto.conf, mqtt_tictactoe.py
  - P: mqtt_laby.py
- client:
  - N: .env (deleted secret), tictactoe.py
  - P: labyrinth.py, menu.py, common_functions.py
  - NP: mqtt_client.py, vibrator.py, gyroscope_handler.py

## Project timeline

- **Project planning**
  - [x] (NP) Architecture, Project plan, general and individual work packages, hardware research and orders
- **Project implementation**
  - Hardware
    - [x] Setup and testing
      - [x] (N) Connect Buttons and test
      - [x] (N) Research docker and pi connection (MQTT protocol)
      - [x] (N) Research Docker with ChatGPT-3.5 Turbo API
      - [x] (P) Connect LED and test
      - [x] (P) Connect LED to Power Supply and test
      - [x] (P) Connect LED Controller board and test
      - [x] (P) Connect Gyroscope and test
      - [x] (N) Connect Vibration motor and test
    - [x] (NP + DesignLab) Design and creation of the case
    - [x] (NP) Setup VM & Connect Gaming Board
  - Coding
    - [x] (P) Implement input logic (Detect Sensor inputs, process inputs)
    - [x] (P) Implement consistent sensor data transfer to VM
    - [x] (N) Implement output logic (Display the game selection, feedback for input on dispaly)
    - [x] (N) Implement AI API functionality and connection
    - [x] (N) Implement TicTacToe
    - [x] (P) Gyroscope inputs for tictactoe & reset state after each input
    - [x] (P) Implement Labyrinth Game
    - [x] (P) Implement game selection logic (Selection between multiple games, use processed inputs)
    - [x] (NP) Test output/response from input server
    - [x] (NP) Connect input/response server/service with openapi server/service
    - [x] (NP) Testing, bug fixing, quality improvments
- **Project Documentation and Presentation**
  - [x] (NP) Repo Cleanup
  - [x] (NP) Documentation
  - [x] (NP) Presentation

## Hardware

### Rented

| Type                | Name                               | Quantity |
|---------------------|------------------------------------|----------|
| Gateway & Connector | RaspberryPi 4 Model B              | 1        |
| Other               | RaspberryPi 15 Watt Power Supply   | 1        |
| Other               | SD Card                            | 1        |
| Application         | LED-Matrix-Panel 64x64             | 1        |
| Sensor              | Buttons (Accept, Decline)          | 2        |
| Other               | Power Supply 50 Watt               | 1        |
| Sensor              | Gyroscope 3-Axis                   | 1        |
| Actuator            | Vibration Motor                    | 1        |

### To be returned (unused)

| Type                | Name                               | Quantity |
|---------------------|------------------------------------|----------|
| Sensor              | Gyroscope 3-Axis                   | 1        |
| Other               | Shield für RGB-LED-Matrix          | 1        |
