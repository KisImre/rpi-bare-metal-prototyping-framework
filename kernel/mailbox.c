/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "mailbox.h"
#include "iobase.h"
#include <stdint.h>

typedef struct mailbox {
    uint32_t read_write; /* 0x00 */
    uint32_t reserved[3];
    uint32_t peek; /* 0x10 */
    uint32_t sender; /* 0x14 */
    uint32_t status; /* 0x18 */
    uint32_t config; /* 0x1C */
}__attribute__((packed)) mailbox_t;

#define MAILBOX0                    ((volatile mailbox_t*)(IO_BASE + 0x0000B880))
#define MAILBOX1                    ((volatile mailbox_t*)(IO_BASE + 0x0000B8A0))

#define MAILBOX_FULL                (0x80000000)
#define MAILBOX_EMPTY               (0x40000000)

#define MAILBOX_CHANNEL_ARM_TO_VC   (8U)

static inline void dsb(void) {
    asm volatile("dsb sy");
}

static inline int mailbox_is_tx_full(volatile mailbox_t *mailbox) {
    dsb();
    return (mailbox->status & MAILBOX_FULL);
}

static inline int mailbox_is_rx_empty(volatile mailbox_t *mailbox) {
    dsb();
    return (mailbox->status & MAILBOX_EMPTY);
}

static inline void mailbox_write_request(volatile mailbox_t *mailbox,
                                         uint32_t request) {
    mailbox->read_write = request;
    dsb();
}

static inline uint32_t mailbox_read_response(volatile mailbox_t *mailbox) {
    dsb();
    return mailbox->read_write;
}

void mailbox_command(void *buffer) {
    uint32_t rw;
    while (mailbox_is_tx_full(MAILBOX0)) {
    }

    rw = (((uintptr_t) buffer) & 0xFFFFFFF0) | MAILBOX_CHANNEL_ARM_TO_VC;
    mailbox_write_request(MAILBOX1, rw);

    while (1) {
        while (mailbox_is_rx_empty(MAILBOX0)) {
        }

        if (mailbox_read_response(MAILBOX0) == rw) {
            break;
        }
    }
}
