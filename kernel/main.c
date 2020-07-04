/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "uart.h"
#include "watchdog.h"

int main(void) {
    uart_init(115200);

    uart_tx('T');
    uart_tx('E');
    uart_tx('S');
    uart_tx('T');
    uart_tx('\r');
    uart_tx('\n');

    uart_flush();

    reset();
}
