/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "packet.h"
#include "uart.h"
#include "watchdog.h"

#define COMMAND_GET_VERSION         0x0000
#define COMMAND_GET_BASE_ADDRESS    0x0001
#define COMMAND_READ                0x0002
#define COMMAND_WRITE               0x0003
#define COMMAND_EXECUTE             0x0004
#define COMMAND_RESET               0x0005
#define COMMAND_ERROR               0x0006

#define VERSION                     0x0100

#define ERRORCODE_INVALID_CRC       0x0001
#define ERRORCODE_INVALID_COMMAND   0x0002
#define ERRORCODE_INVALID_ARG       0x0003

extern uint64_t base;
const uint64_t base_address = (const uint64_t)&base;

typedef uint64_t (*func)(uint64_t x0, uint64_t x1, uint64_t x2, uint64_t x3,
                         uint64_t x4, uint64_t x5, uint64_t x6, uint64_t x7);

struct context {
    func function;
    uint64_t x0;
    uint64_t x1;
    uint64_t x2;
    uint64_t x3;
    uint64_t x4;
    uint64_t x5;
    uint64_t x6;
    uint64_t x7;
};

static void send_error(uint16_t error_code) {
    packet_tx_start();
    packet_tx_u16(COMMAND_ERROR);
    packet_tx_u16(error_code);
    packet_tx_crc();
}

static uint64_t execute(uint64_t context_address) {
    struct context *context = (struct context*) context_address;
    context->x0 = context->function(context->x0, context->x1, context->x2, context->x3,
                                    context->x4, context->x5, context->x6, context->x7);
    return context->x0;
}

int main(void) {
    uint16_t command = 0;
    uint64_t address = 0;
    uint32_t length = 0;
    uint64_t result = 0;

    uart_init(115200);

    while (1) {
        packet_rx_start();
        command = packet_rx_u16();

        switch (command) {
            case COMMAND_GET_VERSION:
                if (packet_rx_validate_crc()) {
                    packet_tx_start();
                    packet_tx_u16(command);
                    packet_tx_u16(VERSION);
                    packet_tx_crc();
                } else {
                    send_error(ERRORCODE_INVALID_CRC);
                }
                break;

            case COMMAND_GET_BASE_ADDRESS:
                if (packet_rx_validate_crc()) {
                    packet_tx_start();
                    packet_tx_u16(command);
                    packet_tx_u64(base_address);
                    packet_tx_crc();
                } else {
                    send_error(ERRORCODE_INVALID_CRC);
                }
                break;

            case COMMAND_READ:
                address = packet_rx_u64();
                length = packet_rx_u32();
                if (packet_rx_validate_crc()) {
                    packet_tx_start();
                    packet_tx_u16(command);
                    packet_tx_u64(address);
                    packet_tx_u32(length);
                    packet_tx_data((const uint8_t*) address, length);
                    packet_tx_crc();
                } else {
                    send_error(ERRORCODE_INVALID_CRC);
                }
                break;

            case COMMAND_WRITE:
                address = packet_rx_u64();
                length = packet_rx_u32();
                if (address >= base_address) {
                    /* Prevent overwriting kernel. */
                    packet_rx_data((uint8_t*) address, length);
                    if (packet_rx_validate_crc()) {
                        packet_tx_start();
                        packet_tx_u16(command);
                        packet_tx_u64(address);
                        packet_tx_u32(length);
                        packet_tx_crc();
                    } else {
                        send_error(ERRORCODE_INVALID_CRC);
                    }
                } else {
                    packet_rx_ignore_data(length);
                    packet_rx_validate_crc(); // Ignore possible error as this is already an invalid state
                    send_error(ERRORCODE_INVALID_ARG);
                }
                break;

            case COMMAND_EXECUTE:
                address = packet_rx_u64();
                if (packet_rx_validate_crc()) {
                    if (address >= base_address) {
                        result = execute(address);
                        packet_tx_start();
                        packet_tx_u16(command);
                        packet_tx_u64(address);
                        packet_tx_u64(result);
                        packet_tx_crc();
                    } else {
                        /* Prevent getting context from kernel area. */
                        send_error(ERRORCODE_INVALID_ARG);
                    }
                } else {
                    send_error(ERRORCODE_INVALID_CRC);
                }
                break;

            case COMMAND_RESET:
                if (packet_rx_validate_crc()) {
                    packet_tx_start();
                    packet_tx_u16(command);
                    packet_tx_crc();
                    uart_flush();

                    reset();
                } else {
                    send_error(ERRORCODE_INVALID_CRC);
                }
                break;

            default:
                send_error(ERRORCODE_INVALID_COMMAND);
        }

        uart_flush();
    }
}
