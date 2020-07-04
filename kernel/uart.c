/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "uart.h"
#include "iobase.h"
#include "mailbox.h"

#define UART_BASE   (IO_BASE + 0x201000)

#define UART_DR     (*(volatile uint32_t *)(UART_BASE + 0x00))
#define UART_FR     (*(volatile uint32_t *)(UART_BASE + 0x18))
#define UART_IBRD   (*(volatile uint32_t *)(UART_BASE + 0x24))
#define UART_FBRD   (*(volatile uint32_t *)(UART_BASE + 0x28))
#define UART_LCRH   (*(volatile uint32_t *)(UART_BASE + 0x2C))
#define UART_CR     (*(volatile uint32_t *)(UART_BASE + 0x30))

#define GPIO_GPFSEL (*(volatile uint32_t *)(IO_BASE + 0x00200004))

static uint32_t mailbox_message[8] __attribute__((aligned(16)));

void uart_clock_set_rate(uint32_t rate) {
    mailbox_message[0] = sizeof(mailbox_message); /* Size */
    mailbox_message[1] = 0x00000000; /* Code */
    mailbox_message[2] = 0x00038002; /* Tag: set clock rate */
    mailbox_message[3] = 12; /* Size */
    mailbox_message[4] = 0; /* Code */
    mailbox_message[5] = 0x02; /* Clock ID: UART */
    mailbox_message[6] = rate; /* Clock rate */
    mailbox_message[7] = 0; /* Skip turbo */

    mailbox_command(mailbox_message);
}

void uart_init(uint32_t baud_rate) {
    uint32_t base_clock = 50000000;

    /* Deinit */
    UART_CR = 0x00;

    uart_clock_set_rate(base_clock);

    /* UART TX/RX pins: 14, 15 */
    GPIO_GPFSEL &= 0xfffc0fff;
    GPIO_GPFSEL |= 0x00024000;

    base_clock <<= 6;
    base_clock /= (baud_rate << 4);

    /* Set baud rate */
    UART_FBRD = base_clock & 0x3f;
    UART_IBRD = base_clock >> 6;

    UART_LCRH = 0x70; /* 8 bit, FIFO enable */
    UART_CR = 0x0301;

    uart_flush();
}

void uart_tx(uint8_t c) {
    /* Waiting for FIFO not full */
    while ((UART_FR & (1 << 5))) {
    }
    UART_DR = c;
}

uint8_t uart_rx(void) {
    /* Waiting for FIFO not empty */
    while ((UART_FR & (1 << 4))) {
    }
    return UART_DR;
}

void uart_flush(void) {
    while ((UART_FR & 0x90) != 0x90) {
    }
}
