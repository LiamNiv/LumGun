import socket
from protocol import *
from AESHelper import AESHelper
from protocol import *

# class meant to handle the communication with the server by a player


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.10.128"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.pos = self.connect()

    def getPos(self):
        """method in charge of getting the original spawn position

        Returns:
            list: the spawn position of the player
        """
        return self.pos

    def connect(self):
        """connecting to the server and receiving first information

        Returns:
            list: spawn pos
        """
        try:
            self.client.connect(self.addr)
            return self.client.recv(1000).decode()
        except socket.error as e:
            print(e)

    def send(self, data):
        """
        method that simplifies information flow to one
        function that send and returns what is received
        """
        try:
            # check is the data is already bytes and if not it converts it
            if not isinstance(data, bytes):
                data = data.encode()

            # send data
            self.client.send(data)

            return self.client.recv(1000)
        except socket.error as e:
            print(e)

    def send_before(self, data):
        """
        method that simplifies information flow to one
        function that send and returns what is received
        """
        try:
            # check is the data is already bytes and if not it converts it
            if not isinstance(data, bytes):
                data = data.encode()

            # send data
            self.client.send(data)

            return self.client.recv(1000).decode()
        except socket.error as e:
            print(e)

    def send_no_answer(self, data):
        """
        simple method that sends info
        """
        try:
            # check is the data is already bytes and if not it converts it
            if not isinstance(data, bytes):
                data = data.encode()

            # send data
            self.client.send(data)
        except socket.error as e:
            print(e)
