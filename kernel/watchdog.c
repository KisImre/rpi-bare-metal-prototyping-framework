/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "watchdog.h"
#include "iobase.h"
#include <stdint.h>

#define WATCHDOG_BASE       (IO_BASE + 0x00100000)
#define WATCHDOG_RSTC       (*(volatile uint32_t *)(WATCHDOG_BASE + 0x1C))
#define WATCHDOG_RSTS       (*(volatile uint32_t *)(WATCHDOG_BASE + 0x1C))
#define WATCHDOG_WDOG       (*(volatile uint32_t *)(WATCHDOG_BASE + 0x1C))
#define WATCHDOG_PASSWORD   (0x5A000000)
#define WATCHDOG_FULL_RESET (0x00000020)

void reset(void) {
    uint32_t temp;

    temp = WATCHDOG_RSTS & ~0xFFFFFAAA; /* Select partition 0 */
    WATCHDOG_RSTS = WATCHDOG_PASSWORD | temp;
    WATCHDOG_WDOG = WATCHDOG_PASSWORD | 10; /* 10 tick timeout */
    WATCHDOG_RSTC = WATCHDOG_PASSWORD | WATCHDOG_FULL_RESET;
}
