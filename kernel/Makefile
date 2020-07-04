# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

CROSS_COMPILE ?= aarch64-linux-gnu-

BUILDDIR ?= build

objs += mailbox.o
objs += main.o
objs += startup.o
objs += string.o
objs += uart.o
objs += watchdog.o

objs := $(addprefix $(BUILDDIR)/,$(objs))
deps := $(objs:%.o=%.d)

ldscript := kernel.ld

CFLAGS += -I. -O2 -Wall -Werror -fdata-sections -ffunction-sections
LDFLAGS += --gc-sections

CC := $(CROSS_COMPILE)gcc
AS := $(CROSS_COMPILE)as
LD := $(CROSS_COMPILE)ld
OBJCOPY := $(CROSS_COMPILE)objcopy
OBJDUMP := $(CROSS_COMPILE)objdump
MKDIR := mkdir -p

.PHONY: all app bootloader emulator clean

all: kernel8.img $(BUILDDIR)/kernel8.dump
	@echo "Kernel build finished"

clean:
	@echo "Cleaning"
	@rm -rf $(BUILDDIR) *.img

%.img: $(BUILDDIR)/%.elf
	@echo "COPY 	$@"
	@$(OBJCOPY) -O binary $< $@

%.dump: %.elf
	@echo "DUMP 	$@"
	@$(OBJDUMP) -d $(<) > $(@)

$(BUILDDIR)/kernel8.elf: $(ldscript) $(objs)
	@echo "LD   	$@"
	@$(LD) $(LDFLAGS) -T $(ldscript) $(objs) -o $@ -M > $(BUILDDIR)/kernel8.map

$(BUILDDIR)/%.o: %.c
	@echo "CC   	$@"
	@$(MKDIR) $(dir $(@))
	@$(CC) $(CFLAGS) -MMD -MP -MF$(@:%.o=%.d) -MT$@ -c $< -o $@

$(BUILDDIR)/%.o: %.s
	@echo "AS   	$@"
	@$(MKDIR) $(dir $(@))
	@$(AS) $(ASFLAGS) -c $< -o $@

-include $(deps)
