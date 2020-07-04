/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#ifndef UART_H_
#define UART_H_

#include <stdint.h>

void uart_init(uint32_t baud_rate);
void uart_deinit(void);

void uart_tx(uint8_t c);
uint8_t uart_rx(void);
void uart_flush(void);

#endif /* UART_H_ */
