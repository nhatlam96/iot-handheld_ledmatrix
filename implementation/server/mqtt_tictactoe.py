import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "143.93.191.153"
BROKER_PORT = 1885
TOPIC_SUBSCRIBE = "tictactoe/input"
TOPIC_RESPONSE = "tictactoe/output"
load_dotenv()


def check_winner(grid):
    winning_lines = [[(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)],
                     [(2, 0), (2, 1), (2, 2)], [(0, 0), (1, 0), (2, 0)],
                     [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
                     [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]
    print("Current Grid:")
    for row in grid:
        print(row)

    for line in winning_lines:
        print(f"Checking line: {line}")
        if grid[line[0][0]][line[0][1]] == grid[line[1][0]][
                line[1][1]] == grid[line[2][0]][line[2][1]] and grid[
                    line[0][0]][line[0][1]] is not None:
            print(f"Winning line found: {line}")
            return grid[line[0][0]][line[0][1]], line
    return None, []


def is_draw(grid):
    for row in grid:
        if None in row:
            return False
    return True


def get_next_move(grid, player):
    for r in range(3):
        for c in range(3):
            if grid[r][c] is None:
                return (r, c)
    return None


class MQTTSubscriber:

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        self.client.subscribe(TOPIC_SUBSCRIBE)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to the MQTT broker")
        else:
            print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from the MQTT broker")

    def on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        print(f"Received message on topic '{message.topic}': {payload}")

        grid = payload["grid"]
        current_player = payload["current_player"]
        move = payload["move"]

        # Place the player's move
        grid[move[0]][move[1]] = current_player
        print("Updated Grid after move:")
        for row in grid:
            print(row)

        winner, winning_line = check_winner(grid)
        if winner:
            print(f"Winner found: {winner}")
            response = {
                "status": "win",
                "grid": grid,
                "winner": winner,
                "winning_line": winning_line
            }
        elif is_draw(grid):
            response = {"status": "draw", "grid": grid}
        else:
            next_move = get_next_move(grid, "O")
            if next_move:
                grid[next_move[0]][next_move[1]] = "O"
                print("Grid after O's move:")
                for row in grid:
                    print(row)
                winner, winning_line = check_winner(grid)
                if winner:
                    print(f"Winner found: {winner}")
                    response = {
                        "status": "win",
                        "grid": grid,
                        "winner": winner,
                        "winning_line": winning_line
                    }
                else:
                    response = {
                        "status": "move",
                        "grid": grid,
                        "next_move": next_move
                    }
            else:
                response = {"status": "error", "message": "No valid moves"}

        print("Publishing response: ", response)
        self.client.publish(TOPIC_RESPONSE, json.dumps(response))

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    mqtt_subscriber = MQTTSubscriber()
    input("Keyboard Interrupt to exit")
    mqtt_subscriber.disconnect()
