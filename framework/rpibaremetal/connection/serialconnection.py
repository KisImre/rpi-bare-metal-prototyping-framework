# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

""" Connection implementation for serial ports. """

from serial import Serial, SerialException, SerialTimeoutException
from rpibaremetal.connection.connection import Connection

class SerialConnection(Connection):
    """ Connection implementation for serial ports. """

    def __init__(self, serial_port, baudrate):
        Connection.__init__(self)
        try:
            self.port = Serial(serial_port, baudrate)
        except (SerialException, SerialTimeoutException) as exception:
            raise self.ConnectionException(exception)

    def send(self, data):
        try:
            self.port.write(data)
        except (SerialException, SerialTimeoutException) as exception:
            raise self.ConnectionException(exception)

    def recv(self, length):
        try:
            return self.port.read(length)
        except (SerialException, SerialTimeoutException) as exception:
            raise self.ConnectionException(exception)
