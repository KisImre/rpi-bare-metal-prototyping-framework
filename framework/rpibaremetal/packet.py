# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

""" This class is handles the serialization of data before sending it the target. """

import struct

class Packet:
    """ This class is responsible for serializing data before sending it the target. """

    def __init__(self):
        self.data = bytes()

    def get_raw_data(self):
        """ Returns the serialized raw data of the message. """
        return self.data

    def push_u8(self, value):
        """ Appends an 8 bit unsigned value to the end of the message. """
        self.data += struct.pack("B", value)

    def push_u16(self, value):
        """ Appends a little endian 16 bit unsigned value to the end of the message. """
        self.data += struct.pack("<H", value)

    def push_u32(self, value):
        """ Appends a little endian 32 bit unsigned value to the end of the  message. """
        self.data += struct.pack("<I", value)

    def push_u64(self, value):
        """ Appends a little endian 64 bit unsigned value to the end of the message. """
        self.data += struct.pack("<Q", value)

    def push_data(self, data):
        """ Appends raw data to the message. """
        self.data += data

    def pop_u8(self):
        """ Returns and removes an 8 bit unsigned value from the start of the message. """
        raw = self.data[0:1]
        self.data = self.data[1:]
        return struct.unpack("B", raw)[0]

    def pop_u16(self):
        """
        Returns and removes a little endian 16 bit unsigned value from the start of the message.
        """
        raw = self.data[0:2]
        self.data = self.data[2:]
        return struct.unpack("<H", raw)[0]

    def pop_u32(self):
        """
        Returns and removes a little endian 32 bit unsigned value from the start of the message.
        """
        raw = self.data[0:4]
        self.data = self.data[4:]
        return struct.unpack("<I", raw)[0]

    def pop_u64(self):
        """
        Returns and removes a little endian 64 bit unsigned value from the start of the message.
        """
        raw = self.data[0:8]
        self.data = self.data[8:]
        return struct.unpack("<Q", raw)[0]

    def pop_data(self, length):
        """ Returns and removes raw data from the start of the message for the given length. """
        raw = self.data[0:length]
        self.data = self.data[length:]
        return raw

    def peek_u8(self):
        """ Returns an 8 bit unsigned value from the start of the message without removing it. """
        return struct.unpack("B", self.data[0:1])[0]

    def peek_u16(self):
        """
        Returns a little endian 16 bit unsigned value from the start of the message without
        removing it.
        """
        return struct.unpack("<H", self.data[0:2])[0]

    def peek_u32(self):
        """
        Returns a little endian 32 bit unsigned value from the start of the message without
        removing it.
        """
        return struct.unpack("<I", self.data[0:4])[0]

    def peek_u64(self):
        """
        Returns a little endian 64 bit unsigned value from the start of the message without
        removing it.
        """
        return struct.unpack("<Q", self.data[0:8])[0]

    def peek_data(self, length):
        """
        Return raw data from the start of the message for the given length without removing it.
        """
        return self.data[0:length]

    def add_crc(self):
        """ Adds an 8 bit CRC to the end of the message. """
        self.push_u8(Packet.calculate_crc(self.data))

    def check_crc(self):
        """ Checks if the last byte of the message is a valid CRC for the message. """
        return self.data[-1] == Packet.calculate_crc(self.data[:-1])

    @staticmethod
    def calculate_crc(data):
        """ Calculates CRC-8 with 0x7 polynomial and 0 as a starting value. """
        crc = 0

        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x07) & 0x00ff
                else:
                    crc = (crc << 1) & 0x00ff

        return crc
