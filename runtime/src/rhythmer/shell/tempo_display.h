// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 jazzy rhythmer
#pragma once
#include <cmath>
#include <cstdint>
namespace rhythmer {
// Screen-thread presentation only. Never feed this result to a clock, audio,
// automation, recording, sample-length calculation or saved project tempo.
class TempoDisplay {
public:
    unsigned sample(unsigned raw, uint32_t now, bool external, unsigned source=0) {
        if(!external || !raw){ready=false;return 0;}
        const uint32_t elapsed=now-last;
        if(!ready || source!=input || elapsed>2000){
            ready=true;input=source;last=published=since=now;
            average=raw;shown=candidate=raw;pending=false;return shown;
        }
        last=now;
        const double time_constant=std::abs(double(raw)-average)>=10.0?150.0:750.0;
        average+=(double(raw)-average)*(-std::expm1(-double(elapsed)/time_constant));
        if(uint32_t(now-published)<250)return shown; // at most four displayed changes a second
        const unsigned rounded=unsigned(std::lround(average));
        const double difference=average-double(shown);
        if(rounded==shown || std::abs(difference)<0.75){pending=false;return shown;}
        // Larger real changes follow the average; small decimal changes must
        // persist, so a rounding boundary cannot flash between neighbouring digits.
        if(std::abs(difference)<=2.0){
            if(!pending || candidate!=rounded){candidate=rounded;since=now;pending=true;return shown;}
            if(uint32_t(now-since)<500)return shown;
        }
        shown=rounded;published=now;pending=false;return shown;
    }
private:
    bool ready=false,pending=false;
    unsigned input=0,shown=0,candidate=0;
    uint32_t last=0,published=0,since=0;
    double average=0;
};
}
