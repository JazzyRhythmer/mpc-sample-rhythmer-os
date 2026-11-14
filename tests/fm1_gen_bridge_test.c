// SPDX-License-Identifier: GPL-3.0-only
#include "bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static struct Fm1GenResult a,b;
int main(void){
 if(rhythmer_fm1_bridge_size()!=sizeof(a)){fprintf(stderr,"FM1 event ABI mismatch\n");return 5;}
 for(unsigned genre=0;genre<=60;genre++)for(unsigned seed=1;seed<=3;seed++){
  rhythmer_fm1_generate(genre,seed*173,70,50,0,&a);rhythmer_fm1_generate(genre,seed*173,70,50,0,&b);
  if(memcmp(&a,&b,sizeof(a))){fprintf(stderr,"Non-deterministic genre=%u seed=%u\n",genre,seed);return 1;}
  if(a.role[0]!=0||!a.count||!a.steps){fprintf(stderr,"Invalid four-track roles genre=%u count=%u\n",genre,a.count);return 2;}
  for(unsigned i=0;i<a.count;i++)if(a.events[i].track>3||a.events[i].key>127||a.events[i].step>=a.steps||!a.events[i].length){fprintf(stderr,"Bounds genre=%u seed=%u index=%u count=%u steps=%u t=%u key=%u step=%u length=%u\n",genre,seed,i,a.count,a.steps,a.events[i].track,a.events[i].key,a.events[i].step,a.events[i].length);return 3;}
 }
 unsigned recent[8]={0};
 for(unsigned call=0;call<12;call++){rhythmer_fm1_generate(2,call?a.seed:731,70,50,1,&a);for(unsigned n=0;n<8;n++)if(call&&recent[n]&&recent[n]==a.seed+1)return 6;for(unsigned n=7;n;n--)recent[n]=recent[n-1];recent[0]=call?a.seed+1:0;}
 uint8_t n[64]={0},f[64]={0},n2[64]={0},f2[64]={0},cfg[5]={70,50,35,2,2};uint32_t s=123,t=123;
 acid_generate(n,f,64,cfg,&s,0,0,0x5ad);acid_generate(n2,f2,64,cfg,&t,0,0,0x5ad);
 if(memcmp(n,n2,64)||memcmp(f,f2,64)||s!=t)return 4;
 puts("Original FM-1 GEN: 61 menu choices x 3 seeds deterministic, T1 kit / T2-4 melodic; original TB-3PO deterministic");return 0;
}
