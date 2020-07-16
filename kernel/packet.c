/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "packet.h"
#include "uart.h"

static uint8_t rx_crc = 0xff;
static uint8_t tx_crc = 0xff;

static uint8_t crc_step(uint8_t crc, uint8_t data) {
    size_t i = 0;

    crc ^= data;
    for (i = 0; i < 8; i++) {
        if ((crc & 0x80) != 0) {
            crc = (crc << 1) ^ 0x07;
        } else {
            crc <<= 1;
        }
    }

    return crc;
}

void packet_rx_start(void) {
    rx_crc = 0;
}

uint8_t packet_rx_u8(void) {
    uint8_t value = 0;

    value = uart_rx();
    rx_crc = crc_step(rx_crc, value);
    return value;
}

uint16_t packet_rx_u16(void) {
    uint16_t value = 0;
    packet_rx_data((uint8_t *)&value, sizeof(value));
    return value;
}

uint32_t packet_rx_u32(void) {
    uint32_t value = 0;
    packet_rx_data((uint8_t *)&value, sizeof(value));
    return value;
}

uint64_t packet_rx_u64(void) {
    uint64_t value = 0;
    packet_rx_data((uint8_t *)&value, sizeof(value));
    return value;
}
void packet_rx_data(uint8_t *data, size_t length) {
    size_t i = 0;

    for (i = 0; i < length; i++) {
        data[i] = packet_rx_u8();
    }
}

void packet_rx_ignore_data(size_t length) {
    size_t i = 0;

    for (i = 0; i < length; i++) {
        packet_rx_u8();
    }
}

bool packet_rx_validate_crc(void) {
    return (uart_rx() == rx_crc);
}

void packet_tx_start(void) {
    tx_crc = 0;
}

void packet_tx_u8(uint8_t value) {
    tx_crc = crc_step(tx_crc, value);
    uart_tx(value);
}

void packet_tx_u16(uint16_t value) {
    packet_tx_data((uint8_t *)&value, sizeof(value));
}

void packet_tx_u32(uint32_t value) {
    packet_tx_data((uint8_t *)&value, sizeof(value));
}

void packet_tx_u64(uint64_t value) {
    packet_tx_data((uint8_t *)&value, sizeof(value));
}

void packet_tx_data(const uint8_t *data, size_t length) {
    size_t i = 0;

    for (i = 0; i < length; i++) {
        packet_tx_u8(data[i]);
    }
}

void packet_tx_crc(void) {
    uart_tx(tx_crc);
}
