// SPDX-License-Identifier: GPL-3.0-only
#pragma once
inline const char* break_variation_status(bool chop,bool hold,bool playing,unsigned activity,unsigned variation,unsigned drift){
    if(chop)return "INACTIVE / Choose LOOP on SOURCE";
    if(hold)return "PATTERN HOLD ON / OFF to vary";
    if(!(activity&2))return playing?"READY / Pattern needs a chop gate":"READY / PLAY or hold a chop pad";
    if(!variation && !drift)return "READY / Raise Variation or Drift";
    return "ACTIVE / Changes at internal bars";
}
inline const char* break_stretch_status(bool playing,unsigned activity){
    if(activity&4)return "STRETCH ACTIVE / Shape this hit";
    return playing || (activity&2) ? "WAITING / Hold P3 on ROLLS" : "READY / PLAY + hold P3 on ROLLS";
}
