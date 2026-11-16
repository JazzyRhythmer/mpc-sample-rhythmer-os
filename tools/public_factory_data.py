#!/usr/bin/env python3
"""Public builds retain the engines' own Init states, without external patch banks."""
from pathlib import Path


def write_empty_bank(ident, output):
    output = Path(output)
    notice = '/* SPDX-License-Identifier: GPL-3.0-only\n * Rhythmer adaptation, jazzy rhythmer, 2026. No external factory data.\n * Zero-count storage declarations only; original engine initialization is unchanged. */\n'
    if ident == 'prophet':
        body = '''#pragma once
#define P5_FACTORY_N 0u
#define P5_FACTORY_BYTES 1u
static const uint8_t P5_FBASE[133] = {0};
static const uint8_t P5_FWIDTH[133] = {0};
static const uint8_t P5_FPACK[1] = {0};
'''
    elif ident == 'elixir':
        body = '''#define FACTORY_NKITS 0u
#define FK_BYTES 1u
static const uint8_t FK_LO[247] = {0};
static const uint8_t FK_W[247] = {0};
static const uint8_t FACTORY_NAMES[1][8] = {{0}};
static const uint8_t FACTORY_BITS[1][1] = {{0}};
'''
    else:
        raise ValueError(ident)
    output.write_text(notice + body)
