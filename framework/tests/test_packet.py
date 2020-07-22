# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

import unittest
from rpibaremetal.packet import Packet

class TestPacket(unittest.TestCase): #pylint: disable=too-many-public-methods
    """ This class is responsible for testing Packet class. """
    U8 = 0x12
    U16 = 0x1234
    U32 = 0x12345678
    U64 = 0x1234567890abcdef
    DATA = [0x12, 0x34, 0x56, 0x78, 0x90]
    CRC = 0xad
    EMPTY_CRC = 0x00

    U8_DATA = [0x12]
    U16_DATA = [0x34, 0x12]
    U32_DATA = [0x78, 0x56, 0x34, 0x12]
    U64_DATA = [0xef, 0xcd, 0xab, 0x90, 0x78, 0x56, 0x34, 0x12]

    def setUp(self):
        self.packet = Packet()

    def assert_packet_data(self, data):
        self.assertEqual(self.packet.get_raw_data(), bytes(data), "Invalid raw data in packet")

    def test_push_u8(self):
        self.assertEqual(self.packet, self.packet.push_u8(self.U8))
        self.assert_packet_data(self.U8_DATA)

    def test_push_u16(self):
        self.assertEqual(self.packet, self.packet.push_u16(self.U16))
        self.assert_packet_data(self.U16_DATA)

    def test_push_u32(self):
        self.assertEqual(self.packet, self.packet.push_u32(self.U32))
        self.assert_packet_data(self.U32_DATA)

    def test_push_u64(self):
        self.assertEqual(self.packet, self.packet.push_u64(self.U64))
        self.assert_packet_data(self.U64_DATA)

    def test_push_data(self):
        self.assertEqual(self.packet, self.packet.push_data(bytes(self.DATA)))
        self.assert_packet_data(self.DATA)

    def test_pop_u8(self):
        self.packet.push_u8(self.U8)
        self.assertEqual(self.packet.pop_u8(), self.U8, "Invalid pop_u8 result")
        self.assert_packet_data([])

    def test_pop_u16(self):
        self.packet.push_u16(self.U16)
        self.assertEqual(self.packet.pop_u16(), self.U16, "Invalid pop_u16 result")
        self.assert_packet_data([])

    def test_pop_u32(self):
        self.packet.push_u32(self.U32)
        self.assertEqual(self.packet.pop_u32(), self.U32, "Invalid pop_u32 result")
        self.assert_packet_data([])

    def test_pop_u64(self):
        self.packet.push_u64(self.U64)
        self.assertEqual(self.packet.pop_u64(), self.U64, "Invalid pop_u64 result")
        self.assert_packet_data([])

    def test_pop_data(self):
        self.packet.push_data(bytes(self.DATA))
        self.assertEqual(self.packet.pop_data(len(self.DATA)), bytes(self.DATA),
                         "Invalid pop_data result")
        self.assert_packet_data([])

    def test_pop_data_remainder(self):
        self.packet.push_data(bytes(self.DATA))
        self.assertEqual(self.packet.pop_data(len(self.DATA) - 2), bytes(self.DATA[:-2]),
                         "Invalid pop result")
        self.assert_packet_data(self.DATA[-2:])

    def test_peek_u8(self):
        self.packet.push_u8(self.U8)
        self.assertEqual(self.packet.peek_u8(), self.U8, "Invalid peek_u8 result")
        self.assert_packet_data(self.U8_DATA)

    def test_peek_u16(self):
        self.packet.push_u16(self.U16)
        self.assertEqual(self.packet.peek_u16(), self.U16, "Invalid peek_u16 result")
        self.assert_packet_data(self.U16_DATA)

    def test_peek_u32(self):
        self.packet.push_u32(self.U32)
        self.assertEqual(self.packet.peek_u32(), self.U32, "Invalid peek_u32 result")
        self.assert_packet_data(self.U32_DATA)

    def test_peek_u64(self):
        self.packet.push_u64(self.U64)
        self.assertEqual(self.packet.peek_u64(), self.U64, "Invalid peek_u64 result")
        self.assert_packet_data(self.U64_DATA)

    def test_peek_data(self):
        self.packet.push_data(bytes(self.DATA))
        self.assertEqual(self.packet.peek_data(len(self.DATA)), bytes(self.DATA),
                         "Invalid peek_data result")
        self.assert_packet_data(self.DATA)

    def test_add_crc(self):
        self.packet.push_data(bytes(self.DATA))
        self.assertEqual(self.packet, self.packet.add_crc())
        self.assert_packet_data(self.DATA + [self.CRC])

    def test_add_crc_empty(self):
        self.assertEqual(self.packet, self.packet.add_crc())
        self.assert_packet_data([self.EMPTY_CRC])

    def test_check_crc_ok(self):
        self.packet.push_data(bytes(self.DATA))
        self.assertEqual(self.packet, self.packet.add_crc())
        self.assertEqual(self.packet.check_crc(), True, "Invalid check_crc result")

    def test_check_crc_fail(self):
        self.packet.push_data(bytes(self.DATA))
        # No add_crc here
        self.assertEqual(self.packet.check_crc(), False, "Invalid check_crc result")

if __name__ == "__main__":
    unittest.main()
