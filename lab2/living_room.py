from gpiozero import LED, Button

from VirtualCopernicusNG import TkCircuit
from common import *

circuit = TkCircuit(get_configuration("Living room"))


@circuit.run
def main():
    conn = Connection()

    floor = Floor.F1
    room = Room.LIVING_ROOM
    led1 = Lamp(floor, room, DeviceType.LAMP1, 1, LED(21))

    button1 = Button(11)
    button1.when_pressed = lambda _: led1.change()

    button2 = Button(12)  # kitchen lamp
    button2.when_pressed = lambda _: conn.send("f1;kitchen;lamp1;1;change")

    while True:
        command = conn.recv()
        data = conn.parse_packet(command, [led1])
        if not data:
            continue

        devices, operation = data

        ops = {
            operation.CHANGE: Lamp.change,
            operation.OFF: Lamp.off,
            operation.ON: Lamp.on
        }

        for d in devices:
            ops[operation].__call__(d)
