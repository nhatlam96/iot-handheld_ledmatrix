from time import sleep
import paho.mqtt.client as mqtt
import json


# MQTT Broker details
BROKER_ADDRESS = "143.93.191.153"
BROKER_PORT = 1885


class MQTTClient:
    '''
    Handles MQTT communication for querying and receiving responses.
    '''

    def __init__(self, topic_query, topic_response):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.response = None
        self.topic_query = topic_query
        self.topic_response = topic_response

        # after 60 seconds of inactivity, the connection will be tested by MQTT
        self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        self.client.subscribe(self.topic_response)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        '''
        Callback when the client connects to the MQTT broker.
        '''
        # rc is the connection result or reason code
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print(f"Failed to connect with result code {rc}")

    def on_message(self, client, userdata, msg):
        '''
        Callback when a message is received from the MQTT broker.
        '''
        payload = json.loads(msg.payload.decode("utf-8"))
        if msg.topic == self.topic_response:
            # Set the response to the received payload from the broker
            self.response = payload

    def publish(self, topic, payload):
        '''
        Publish a message to a specific MQTT topic.
        '''
        # Reset response, so it doesn't use the previous one
        self.response = None
        self.client.publish(topic, json.dumps(payload))
        # after publishing the message, the on_message callback will be called
        # and the self.response will be set to the received payload

    def get_response(self):
        '''
        Wait and get the response
        '''
        while self.response is None:
            sleep(0.1)
        return self.response
