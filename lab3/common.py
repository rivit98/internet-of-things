from copy import copy
from enum import Enum

from gpiozero import LED

APARTAMENT_NAME = "ag_house"
MQTT_ADDR = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_GENERAL_TOPIC = APARTAMENT_NAME + "/service"
MQTT_ZONE1_TOPIC = APARTAMENT_NAME + "/zone1/light"
MQTT_ZONE2_TOPIC = APARTAMENT_NAME + "/zone2/light"
MQTT_LIGHT_TOPIC_FORMAT = APARTAMENT_NAME + "/light/{}"

def get_configuration(room_name):
    return {
        "name": room_name,
        "sheet": "sheet_smarthouse.png",
        "width": 332,
        "height": 300,
        "leds": [
            {"x": 112, "y": 70, "name": "LED 1", "pin": 21},
            {"x": 71, "y": 141, "name": "LED 2", "pin": 22}
        ],
        "buttons": [
            {"x": 242, "y": 146, "name": "Button 1", "pin": 11},
            {"x": 200, "y": 217, "name": "Button 2", "pin": 12},
        ],
    }


class State(Enum):
    DISABLED = 0
    ENABLED = 1


class Lamp:
    def __init__(self, id, led: LED, initial_state=State.DISABLED):
        self.id = id
        self.led = led
        self.state = initial_state
        if self.state == State.ENABLED:
            self.on()

    def get_id(self):
        return self.id

    def is_enabled(self):
        return self.state == State.ENABLED

    def off(self):
        self.state = State.DISABLED
        self.led.off()
        print(self)

    def on(self):
        self.state = State.ENABLED
        self.led.on()
        print(self)

    def change(self):
        if self.is_enabled():
            self.off()
        else:
            self.on()

    def __str__(self):
        return "lamp id:{} {}".format(self.id, self.state.name)


def do_action(msg, lamp_list):
    topic = msg.topic
    msg = msg.payload.decode().lower()
    op = {
        "toggle": Lamp.change,
        "off": Lamp.off,
        "on": Lamp.on
    }[msg]

    try:
        parts = topic.split('/')
        lamp_id = int(parts[-1])
        lamp_list = list(filter(lambda x: x.get_id() == lamp_id, lamp_list))
    except ValueError:
        pass


    for lamp in lamp_list:
        op.__call__(lamp)
