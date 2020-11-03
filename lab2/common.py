import socket
import struct
from enum import Enum

from gpiozero import LED


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


class Floor(Enum):
    ALL = 0
    F1 = 1
    F2 = 2


class Room(Enum):
    ALL = 0
    LOBBY = 1
    KITCHEN = 2
    LIVING_ROOM = 3
    BEDROOM = 4
    BATHROOM = 5


class DeviceType(Enum):
    ALL = 0
    LAMP1 = 1
    SHUTTER = 2


class Operation(Enum):
    ON = 0
    OFF = 1
    CHANGE = 2


class State(Enum):
    DISABLED = 0
    ENABLED = 1


class ID(Enum):
    ALL = -1


class Device:
    def __init__(self, floor, room, device, id):
        self.floor = floor
        self.room = room
        self.device_type = device
        self.id = id


class Shutter(Device):
    def __init__(self, floor, room, device, id, connection):
        super().__init__(floor, room, device, id)
        self.connection = connection

    def shut_down(self):
        self.connection.send("*;*;*;*;off")


class Lamp(Device):
    def __init__(self, floor, room, device, id, led: LED, initial_state=State.DISABLED):
        super().__init__(floor, room, device, id)
        self.led = led
        self.state = initial_state

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
        return "{} {} {} (id:{}) {}".format(self.floor.name, self.room.name, self.device_type.name, self.id, self.state.name)


class NetworkConfig:
    MCAST_GRP = '236.0.0.0'
    MCAST_PORT = 3456


class Connection:
    def __init__(self):
        self.port = NetworkConfig.MCAST_PORT
        self.ip = NetworkConfig.MCAST_GRP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        mreq = struct.pack("4sl", socket.inet_aton(self.ip), socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def send(self, command):
        self.sock.sendto(command.encode('utf-8'), (self.ip, self.port))

    def recv(self):
        command = self.sock.recv(1024)
        command = command.decode("utf-8")
        return command

    def parse_packet(self, command, device_list):
        floor, room, device, id, operation = command.split(';')
        floor = {
            "*": Floor.ALL,
            "f1": Floor.F1,
            "f2": Floor.F2
        }[floor]

        room = {
            "*": Room.ALL,
            "lobby": Room.LOBBY,
            "kitchen": Room.KITCHEN,
            "living_room": Room.LIVING_ROOM,
            "bedroom": Room.BEDROOM,
            "bathroom": Room.BATHROOM
        }[room]

        device = {
            "*": DeviceType.ALL,
            "lamp1": DeviceType.LAMP1,
            "shutter": DeviceType.SHUTTER
        }[device]

        if id == '*':
            id = ID.ALL
        else:
            id = int(id)

        operation = {
            "on": Operation.ON,
            "off": Operation.OFF,
            "change": Operation.CHANGE,
        }[operation]


        devices = filter(lambda d: floor == Floor.ALL or d.floor == floor, device_list)
        devices = filter(lambda d: room == Room.ALL or d.room == room, devices)
        devices = filter(lambda d: device == DeviceType.ALL or d.device_type == device, devices)
        devices = filter(lambda d: id == ID.ALL or id == d.id, devices)
        devices = list(devices)
        if len(devices) == 0:
            return None

        return devices, operation
