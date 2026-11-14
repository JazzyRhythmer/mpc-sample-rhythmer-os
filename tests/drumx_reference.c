/* SPDX-License-Identifier: GPL-3.0-only */
/* Unscoped, original C voice: independent bit-comparison reference. */
#include <stdint.h>
#include <string.h>
#include "felucca_tables.h"
#include "helpers.h"
#include "../ports/drumx/original/drumx_voice.c"
static dx_voice_t ref;
void drumx_reference_reset(unsigned kit,unsigned lane) {
    memcpy(dx_kit,DX_KITS[kit].lane,sizeof dx_kit);
    memcpy(dx_lay,DX_KITS[kit].lay,sizeof dx_lay);
    memset(&ref,0,sizeof ref);dx_tone=0;dx_hands=0;dx_trigger(&ref);
    (void)lane;
}
void drumx_reference_block(unsigned lane,unsigned block,int32_t *out) {
    dx_tone=(uint8_t)((block/17)%256);dx_hands=(block/29)%16;
    if(block==127)dx_choke(&ref);
    dx_run(&dx_kit[lane],&ref,block%128,(int)(block%65)-32,(int)(block%33)-16,
        (int)(block%25)-12,(int)(block%17)-8,block%128,block%128,out,32);
}
