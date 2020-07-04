/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

#ifndef KERNEL_STRING_H_
#define KERNEL_STRING_H_

#include <stddef.h>

void *memcpy(void *dest, const void *src, size_t n);
void *memset(void *dest, int value, size_t n);

#endif  /* KERNEL_STRING_H_ */
