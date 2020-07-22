# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

import unittest
from rpibaremetal.connection.connection import Connection
from rpibaremetal.packet import Packet
from rpibaremetal.protocol import Protocol

class MockConnection(Connection):
    """ Mock implementation of the Connection interface. """

    def __init__(self, test_case):
        Connection.__init__(self)

        self.test_case = test_case
        self.send_buffer = []
        self.recv_buffer = []

    def check_empty(self):
        self.test_case.assertEqual(self.send_buffer, [])
        self.test_case.assertEqual(self.recv_buffer, [])

    def expect_send(self, data):
        self.send_buffer += data

    def expect_recv(self, data):
        self.recv_buffer += data

    def send(self, data):
        if not self.send_buffer:
            raise Connection.ConnectionException("No data")
        temp = bytes(self.send_buffer[:len(data)])
        self.send_buffer = self.send_buffer[len(data):]
        self.test_case.assertEqual(temp, data)

    def recv(self, length):
        if not self.recv_buffer:
            raise Connection.ConnectionException("No data")
        result = self.recv_buffer[:length]
        self.recv_buffer = self.recv_buffer[length:]
        return bytes(result)

class TestProtocol(unittest.TestCase): #pylint: disable=too-many-public-methods
    """ This class is responsible for testing Protocol class. """
    VERSION = 0x1234
    BASE = 0x1234567890abcdef
    ADDR = BASE
    DATA = bytes([0, 1, 2, 3, 4, 5, 6, 7])
    RESULT = 0xfedcba0987654321

    def setUp(self):
        self.connection = MockConnection(self)
        self.protocol = Protocol(self.connection)

    def tearDown(self):
        self.connection.check_empty()

    def expect_transaction(self, request, response):
        self.connection.expect_send(request.get_raw_data())
        self.connection.expect_recv(response.get_raw_data())

    def expect_protocol_error(self, msg):
        return self.assertRaisesRegex(Protocol.ProtocolException, msg)

    @staticmethod
    def create_error_packet(error_code):
        return Packet().push_u16(Protocol.COMMAND_ERROR).push_u16(error_code).add_crc()

    # get_version

    def test_get_version(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_VERSION).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_GET_VERSION).push_u16(self.VERSION).add_crc()
        self.expect_transaction(request, response)
        self.assertEqual(self.protocol.get_version(), self.VERSION, "Invalid version")

    def test_get_version_crc_response_error(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_VERSION).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_GET_VERSION).push_u16(self.VERSION).push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*response"):
            self.protocol.get_version()

    def test_get_version_crc_target_error(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_VERSION).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_CRC)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*target"):
            self.protocol.get_version()

    def test_get_version_invalid_arg_error(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_VERSION).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_ARG)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*argument"):
            self.protocol.get_version()

    # get_base_address

    def test_get_base_address(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_BASE_ADDRESS).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_GET_BASE_ADDRESS).push_u64(self.BASE). \
            add_crc()
        self.expect_transaction(request, response)
        self.assertEqual(self.protocol.get_base_address(), self.BASE, "Invalid base address")

    def test_get_base_address_crc_response_error(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_BASE_ADDRESS).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_GET_BASE_ADDRESS).push_u64(self.BASE). \
            push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*response"):
            self.protocol.get_base_address()

    def test_get_base_address_crc_target_error(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_BASE_ADDRESS).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_CRC)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*target"):
            self.protocol.get_base_address()

    def test_get_base_address_invalid_arg_error(self):
        request = Packet().push_u16(Protocol.COMMAND_GET_BASE_ADDRESS).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_ARG)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*argument"):
            self.protocol.get_base_address()

    # read

    def test_read(self):
        request = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        self.expect_transaction(request, response)
        self.assertEqual(self.protocol.read(self.ADDR, len(self.DATA)), self.DATA, "Invalid data")

    def test_read_crc_error(self):
        request = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
        push_u32(len(self.DATA)).push_data(self.DATA).push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*response"):
            self.protocol.read(self.ADDR, len(self.DATA))

    def test_read_different_address(self):
        request = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR + 1). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Different.*address"):
            self.protocol.read(self.ADDR, len(self.DATA))

    def test_read_different_length(self):
        request = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA) + 1).push_data(self.DATA).add_crc()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Different.*length"):
            self.protocol.read(self.ADDR, len(self.DATA))

    def test_read_crc_target_error(self):
        request = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_CRC)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*target"):
            self.protocol.read(self.ADDR, len(self.DATA))

    def test_read_invalid_arg_error(self):
        request = Packet().push_u16(Protocol.COMMAND_READ).push_u64(self.ADDR). \
        push_u32(len(self.DATA)).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_ARG)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*argument"):
            self.protocol.read(self.ADDR, len(self.DATA))

    # write

    def test_write(self):
        request = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).add_crc()
        self.expect_transaction(request, response)
        self.protocol.write(self.ADDR, self.DATA)

    def test_write_crc_error(self):
        request = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*response"):
            self.protocol.write(self.ADDR, self.DATA)

    def test_write_different_address(self):
        request = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR + 1). \
            push_u32(len(self.DATA)).add_crc()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Different.*address"):
            self.protocol.write(self.ADDR, self.DATA)

    def test_write_different_length(self):
        request = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA) + 1).add_crc()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Different.*length"):
            self.protocol.write(self.ADDR, self.DATA)

    def test_write_crc_target_error(self):
        request = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_CRC)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*target"):
            self.protocol.write(self.ADDR, self.DATA)

    def test_write_invalid_arg_error(self):
        request = Packet().push_u16(Protocol.COMMAND_WRITE).push_u64(self.ADDR). \
            push_u32(len(self.DATA)).push_data(self.DATA).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_ARG)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*argument"):
            self.protocol.write(self.ADDR, self.DATA)

    # execute

    def test_execute(self):
        request = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR). \
            push_u64(self.RESULT).add_crc()
        self.expect_transaction(request, response)
        self.assertEqual(self.protocol.execute(self.ADDR), self.RESULT, "Invalid result")

    def test_execute_crc_error(self):
        request = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR). \
            push_u64(self.RESULT).push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*response"):
            self.protocol.execute(self.ADDR)

    def test_execute_different_address(self):
        request = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR + 1). \
            push_u64(self.RESULT).add_crc()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Different.*address"):
            self.protocol.execute(self.ADDR)

    def test_execute_crc_target_error(self):
        request = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_CRC)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*target"):
            self.protocol.execute(self.ADDR)

    def test_execute_invalid_arg_error(self):
        request = Packet().push_u16(Protocol.COMMAND_EXECUTE).push_u64(self.ADDR).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_ARG)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*argument"):
            self.protocol.execute(self.ADDR)

    # reset

    def test_reset(self):
        request = Packet().push_u16(Protocol.COMMAND_RESET).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_RESET).add_crc()
        self.expect_transaction(request, response)
        self.protocol.reset()

    def test_reset_crc_error(self):
        request = Packet().push_u16(Protocol.COMMAND_RESET).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_RESET).push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*response"):
            self.protocol.reset()

    def test_reset_crc_target_error(self):
        request = Packet().push_u16(Protocol.COMMAND_RESET).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_CRC)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*target"):
            self.protocol.reset()

    # do_transaction

    def test_invalid_response_code(self):
        request = Packet().push_u16(0).add_crc()
        response = Packet().push_u16(0xffff)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*command"):
            self.protocol.do_transaction(0, {}, {})

    def test_invalid_error_code(self):
        request = Packet().push_u16(0).add_crc()
        response = TestProtocol.create_error_packet(0xffff)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Unknown.*error"):
            self.protocol.do_transaction(0, {}, {})

    def test_invalid_error_crc(self):
        request = Packet().push_u16(0).add_crc()
        response = Packet().push_u16(Protocol.COMMAND_ERROR).push_u8(0)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("CRC.*error"):
            self.protocol.do_transaction(0, {}, {})

    def test_invalid_command(self):
        request = Packet().push_u16(0).add_crc()
        response = TestProtocol.create_error_packet(Protocol.ERRORCODE_INVALID_COMMAND)
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*command.*target"):
            self.protocol.do_transaction(0, {}, {})

    def test_send_error(self):
        request = Packet()
        response = Packet()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("No data"):
            self.protocol.do_transaction(0, {}, {})

    def test_recv_error(self):
        request = Packet().push_u16(0).add_crc()
        response = Packet()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("No data"):
            self.protocol.do_transaction(0, {}, {})

    def test_send_all_types(self):
        request = Packet().push_u16(0).push_u8(0).push_u16(1).push_u32(2).push_u64(3). \
            push_data(bytes([0, 1, 2, 3])).add_crc()
        response = Packet().push_u16(0).add_crc()
        self.expect_transaction(request, response)
        self.protocol.do_transaction(0, {
            "u8": {"type": Protocol.TYPE_U8, "value": 0},
            "u16": {"type": Protocol.TYPE_U16, "value": 1},
            "u32": {"type": Protocol.TYPE_U32, "value": 2},
            "u64": {"type": Protocol.TYPE_U64, "value": 3},
            "data": {"type": Protocol.TYPE_DATA, "value": bytes([0, 1, 2, 3])},
            }, {})

    def test_recv_all_types(self):
        request = Packet().push_u16(0).add_crc()
        response = Packet().push_u16(0).push_u8(0).push_u16(1).push_u32(2).push_u64(3). \
            push_data(bytes([0, 1, 2, 3])).add_crc()
        self.expect_transaction(request, response)
        result = self.protocol.do_transaction(0, {}, {
            "u8": {"type": Protocol.TYPE_U8},
            "u16": {"type": Protocol.TYPE_U16},
            "u32": {"type": Protocol.TYPE_U32},
            "u64": {"type": Protocol.TYPE_U64},
            "data": {"type": Protocol.TYPE_DATA, "length": 4},
            })
        self.assertEqual(result["u8"], 0)
        self.assertEqual(result["u16"], 1)
        self.assertEqual(result["u32"], 2)
        self.assertEqual(result["u64"], 3)
        self.assertEqual(result["data"], bytes([0, 1, 2, 3]))

    def test_invalid_send_type(self):
        with self.expect_protocol_error("Invalid.*type"):
            self.protocol.do_transaction(0, {"test": {"type": 0xffff, "value": 1}}, {})

    def test_invalid_recv_type(self):
        request = Packet().push_u16(0).add_crc()
        response = Packet().push_u16(0).add_crc()
        self.expect_transaction(request, response)
        with self.expect_protocol_error("Invalid.*type"):
            self.protocol.do_transaction(0, {}, {"test": {"type": 0xffff, "value": 1}})

if __name__ == "__main__":
    unittest.main()
