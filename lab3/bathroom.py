from VirtualCopernicusNG import TkCircuit
from common import *
from gpiozero import LED, Button
import paho.mqtt.client as mqtt

ROOM_NAME = "Bathroom"

circuit = TkCircuit(get_configuration(ROOM_NAME))


@circuit.run
def main():
    led1 = Lamp(2, LED(21))
    led2 = Lamp(3, LED(22))

    button1, button2 = Button(11), Button(12)
    button1.when_pressed = lambda _: led1.change()
    button2.when_pressed = lambda _: led2.change()

    def on_connect(client, userdata, flags, rc):
        mqttc.publish(MQTT_GENERAL_TOPIC, ROOM_NAME + " connected")
        mqttc.subscribe(MQTT_LIGHT_TOPIC_FORMAT.format(led1.get_id()))
        mqttc.subscribe(MQTT_LIGHT_TOPIC_FORMAT.format(led2.get_id()))
        mqttc.subscribe(MQTT_ZONE2_TOPIC)

    def on_message(client, userdata, msg):
        do_action(msg, [led1, led2])

    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.will_set(MQTT_GENERAL_TOPIC, ROOM_NAME + " died")

    mqttc.connect(MQTT_ADDR, MQTT_PORT, 60)

    mqttc.loop_forever()
