import paho.mqtt.client as mqtt
import json
from random import shuffle, random


BROKER_ADDRESS = "143.93.191.153"
BROKER_PORT = 1885
TOPIC_QUERY = "labyrinth/query"
TOPIC_RESPONSE = "labyrinth/response"


def generate_maze(width, height, exit_position, start_position):
    '''
    Generate a maze, a depth-first search algorithm and
    randomly assign some walls as deadly walls.

    Args:
        width (int): Width of maze in cells.
        height (int): Height of maze in cells.
        exit_position: Exit coordinates of the maze.
        start_position: Start coordinates of the maze.

    Returns:
        maze (list): Generated maze with walls (1) and paths (0).
        deadlyWalls (list): Generated deadly walls from the maze list.
    '''

    deadlyWallProbability = 0.2

    # Init maze where each cell is a wall (1)
    maze = [[1 for _ in range(width)] for _ in range(height)]
    # Init stack with the starting postion
    stack = [(0, 0)]

    # Carves out paths in the maze, while cells are still in the stack
    while stack:
        # Current cell is the one on top of the stack
        x, y = stack[-1]
        # Mark the current cell as a path
        maze[y][x] = 0
        # List of potential neighboring cells (2 cells away)
        neighbors = [(x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)]
        # Randomly shuffles order of neighbors
        shuffle(neighbors)
        # For each neighboring cell
        for nx, ny in neighbors:
            # If the neighbors is within bounds of the maze and is a wall
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                # Set the cell between current and neigbor to a path (0)
                maze[(y + ny) // 2][(x + nx) // 2] = 0
                # Add the neighboring cell to the stack
                stack.append((nx, ny))
                break
        else:
            # Backtrack if no valid neighbors are found
            stack.pop()

    # Ensure the exit position is a path
    maze[exit_position[1]][exit_position[0]] = 0

    deadlyWalls = []
    # Generates deadly walls, by iterating over each cell in the maze.
    for y in range(height):
        for x in range(width):
            # If current cell is a wall and
            if (maze[y][x] == 1 and
                # If it is randomly assigned as a deadly wall and
                random() < deadlyWallProbability and
                # If it is not the start and exit positions
                (x, y) != (exit_position[0], exit_position[1]) and
                (x, y) != (start_position[0], start_position[1])):
                # Add the current cell to deadly walls
                deadlyWalls.append((x, y))

    return {"maze": maze, "deadlyWalls": deadlyWalls}


class MQTTSubscriber:

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        # self.client.subscribe(TOPIC_SUBSCRIBE)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to the MQTT broker")
            client.subscribe(TOPIC_QUERY)
        else:
            print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from the MQTT broker")

    def on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        print(f"Received message on topic '{message.topic}': {payload}")

        width = payload['width']
        height = payload['height']
        exit_position = payload['exit_position']
        start_position = payload['start_position']

        maze_data = generate_maze(width, height, exit_position, start_position)

        response = {'maze': maze_data['maze'], 'deadlyWalls': maze_data['deadlyWalls']}

        self.client.publish(TOPIC_RESPONSE, json.dumps(response))

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    mqtt_subscriber = MQTTSubscriber()
    input("Keyboard Interrupt to exit")
    mqtt_subscriber.disconnect()
