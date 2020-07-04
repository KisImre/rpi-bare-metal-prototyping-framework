/*
 * Copyright (c) 2020, Kis Imre. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

ENTRY(Reset_Handler)

SECTIONS
{
	.init 0x0000 :
	{
		*(.init)
	}

	.text  :
	{
		*(.text)
		*(.text*)
		*(.rodata)
		*(.rodata*)
	}

	.data :
	{
		*(.data)
		*(.data*)
	}

	.bss :
	{
		. = ALIGN(8);
		__bss_start = .;
		*(.bss)
		*(.bss*)
		*(COMMON)
		. = ALIGN(8);
		__bss_end = .;
	}
	
	stack = 0x1000;

	/DISCARD/ :
	{
		*(*)
	}
}