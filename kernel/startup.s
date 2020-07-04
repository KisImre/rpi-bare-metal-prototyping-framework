/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

	.section .init
	.global Reset_Handler
Reset_Handler:
	mrs x0, mpidr_el1
	and x0, x0, #0x3
	cbz x0, Primary_Core_Handler
	/* Secondary cores are waiting for event i.e. sleeping */
	wfe
	b Secondary_Core_Handler

Primary_Core_Handler:
	adr x0, stack
	mov sp, x0
	b main

Secondary_Core_Handler:
	b Secondary_Core_Handler
