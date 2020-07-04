/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#include "string.h"

void* memcpy(void *dest, const void *src, size_t n) {
    char *d = dest;

    while (n--) {
        *d++ = *(const char *)src++;
    }

    return dest;
}

void *memset(void *dest, int value, size_t n) {
    char *d = dest;

    while (n--) {
        *d++ = value;
    }

    return dest;
}
