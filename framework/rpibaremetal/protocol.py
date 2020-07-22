# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

"""
The module contains the classes related to the protocol interpretation for sending commands to the
target.
"""

from rpibaremetal.packet import Packet
from rpibaremetal.connection.connection import Connection

class Protocol:
    """ The class handles the protocol interpretation for sending commands to the target. """

    COMMAND_GET_VERSION = 0x0000
    COMMAND_GET_BASE_ADDRESS = 0x0001
    COMMAND_READ = 0x0002
    COMMAND_WRITE = 0x0003
    COMMAND_EXECUTE = 0x0004
    COMMAND_RESET = 0x0005
    COMMAND_ERROR = 0x0006

    ERRORCODE_INVALID_CRC = 0x0001
    ERRORCODE_INVALID_COMMAND = 0x0002
    ERRORCODE_INVALID_ARG = 0x0003

    TYPE_DATA = 0
    TYPE_U8 = 1
    TYPE_U16 = 2
    TYPE_U32 = 4
    TYPE_U64 = 8

    class ProtocolException(Exception):
        """ Protocol specific exception type. """

    def __init__(self, connection):
        self.connection = connection

    def get_version(self):
        """ Queries the protocol version. """
        response = {"version": {"type": Protocol.TYPE_U16}}
        result = self.do_transaction(Protocol.COMMAND_GET_VERSION, {}, response)
        return result["version"]

    def get_base_address(self):
        """ Queries the base address of the memory area which is available for the user. """
        response = {"address": {"type": Protocol.TYPE_U64}}
        result = self.do_transaction(Protocol.COMMAND_GET_BASE_ADDRESS, {}, response)
        return result["address"]

    def read(self, address, length):
        """ Reads data from the gives address for the specified length in bytes. """
        request = {"address": {"type": Protocol.TYPE_U64, "value": address},
                   "length": {"type": Protocol.TYPE_U32, "value": length}}
        response = {"address": {"type": Protocol.TYPE_U64},
                    "length": {"type": Protocol.TYPE_U32},
                    "data": {"type": Protocol.TYPE_DATA, "length": length}}
        result = self.do_transaction(Protocol.COMMAND_READ, request, response)
        if result["address"] != address or result["length"] != length:
            raise self.ProtocolException("Different address or length in response")
        return result["data"]

    def write(self, address, data):
        """ Writes data to the given address. """
        request = {"address": {"type": Protocol.TYPE_U64, "value": address},
                   "length": {"type": Protocol.TYPE_U32, "value": len(data)},
                   "data": {"type": Protocol.TYPE_DATA, "value": data}}
        response = {"address": {"type": Protocol.TYPE_U64},
                    "length": {"type": Protocol.TYPE_U32}}
        result = self.do_transaction(Protocol.COMMAND_WRITE, request, response)
        if result["address"] != address or result["length"] != len(data):
            raise self.ProtocolException("Different address or length in response")

    def execute(self, address):
        """ Executes a context of the given address. """
        request = {"address": {"type": Protocol.TYPE_U64, "value": address}}
        response = {"address": {"type": Protocol.TYPE_U64},
                    "result": {"type": Protocol.TYPE_U64}}
        result = self.do_transaction(Protocol.COMMAND_EXECUTE, request, response)
        if result["address"] != address:
            raise self.ProtocolException("Different address in response")
        return result["result"]

    def reset(self):
        """ Resets the target. """
        self.do_transaction(Protocol.COMMAND_RESET, {}, {})

    def do_transaction(self, command, request, response):
        """ Sends a requests and receives a response of a the given message descriptors. """
        self.send_request(command, request)
        response_packet = self.recv_response(command, response)
        return self.process_response(response, response_packet)

    def send_request(self, command, request):
        """ Builds a request packet and sends it. """
        packet = Packet()
        packet.push_u16(command)

        for request_key in request:
            element = request[request_key]

            if element["type"] == Protocol.TYPE_U8:
                packet.push_u8(element["value"])
            elif element["type"] == Protocol.TYPE_U16:
                packet.push_u16(element["value"])
            elif element["type"] == Protocol.TYPE_U32:
                packet.push_u32(element["value"])
            elif element["type"] == Protocol.TYPE_U64:
                packet.push_u64(element["value"])
            elif element["type"] == Protocol.TYPE_DATA:
                packet.push_data(element["value"])
            else:
                raise self.ProtocolException("Invalid data type: " + str(element["type"]))
        packet.add_crc()

        try:
            self.connection.send(packet.get_raw_data())
        except Connection.ConnectionException as exception:
            raise self.ProtocolException(exception)

    def recv_response(self, command, response):
        """ Receives a response packet of the calculated length. """
        response_payload_length = Protocol.calculate_response_length(response)

        try:
            packet = Packet()
            packet.push_data(self.connection.recv(2)) # Command bytes
            response_command = packet.peek_u16()
            if command != response_command:
                if Protocol.COMMAND_ERROR == response_command:
                    packet.push_data(self.connection.recv(5))
                    if not packet.check_crc():
                        raise self.ProtocolException("Invalid CRC in error response")

                    self.process_error_packet(packet)

                raise self.ProtocolException("Invalid response command: 0x%04X" % response_command)

            packet.push_data(self.connection.recv(response_payload_length))
            if not packet.check_crc():
                raise self.ProtocolException("Invalid CRC in response")
        except Connection.ConnectionException as exception:
            raise self.ProtocolException(exception)

        return packet

    def process_response(self, response, packet):
        """ Parses the response elements into an object. """
        result = {}
        packet.pop_u16() # Command
        for response_key in response:
            element = response[response_key]

            if element["type"] == Protocol.TYPE_U8:
                result[response_key] = packet.pop_u8()
            elif element["type"] == Protocol.TYPE_U16:
                result[response_key] = packet.pop_u16()
            elif element["type"] == Protocol.TYPE_U32:
                result[response_key] = packet.pop_u32()
            elif element["type"] == Protocol.TYPE_U64:
                result[response_key] = packet.pop_u64()
            elif element["type"] == Protocol.TYPE_DATA:
                result[response_key] = packet.pop_data(element["length"])
            else:
                raise self.ProtocolException("Invalid data type: " + str(element["type"]))

        return result

    @staticmethod
    def calculate_response_length(response):
        """ Calculates the expected length of the reponse by the response descriptor. """
        length = 0
        for response_key in response:
            element = response[response_key]
            length += element["type"] if element["type"] else element["length"]
        length += 1 # CRC
        return length

    def process_error_packet(self, packet):
        """ Processes the error packet and raises exceptions according to the error code. """
        packet.pop_u16() # Command
        error_code = packet.pop_u16()

        if error_code == Protocol.ERRORCODE_INVALID_CRC:
            raise self.ProtocolException("Invalid CRC was received by the target")
        if error_code == Protocol.ERRORCODE_INVALID_COMMAND:
            raise self.ProtocolException("Invalid command was received by the target")
        if error_code == Protocol.ERRORCODE_INVALID_ARG:
            raise self.ProtocolException("Invalid argument was received by the target")
        raise self.ProtocolException("Unknown error code was received: 0x%04X" % error_code)
