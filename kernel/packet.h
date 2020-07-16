/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */
#ifndef KERNEL_PACKET_H_
#define KERNEL_PACKET_H_

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

void packet_rx_start(void);
uint8_t packet_rx_u8(void);
uint16_t packet_rx_u16(void);
uint32_t packet_rx_u32(void);
uint64_t packet_rx_u64(void);
void packet_rx_data(uint8_t *data, size_t length);
void packet_rx_ignore_data(size_t length);
bool packet_rx_validate_crc(void);

void packet_tx_start(void);
void packet_tx_u8(uint8_t value);
void packet_tx_u16(uint16_t value);
void packet_tx_u32(uint32_t value);
void packet_tx_u64(uint64_t value);
void packet_tx_data(const uint8_t *data, size_t length);
void packet_tx_crc(void);

#endif /* KERNEL_PACKET_H_ */
