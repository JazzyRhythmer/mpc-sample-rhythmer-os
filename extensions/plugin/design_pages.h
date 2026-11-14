// SPDX-License-Identifier: AGPL-3.0-only
// Presentation-only mapping. Each slot retains its original shown parameter ID.
#pragma once
#include "rhythmer/plugin/plugin_panel.h"
#include <map>
#include <vector>
#include <string>
#include <cstdio>
namespace rhythmer {
struct PluginDesignControl {int shown,order;std::string group;};
inline std::vector<PluginDesignPage> build_plugin_design_pages(const std::vector<PluginDesignControl>& controls){
    std::map<std::pair<int,std::string>,std::vector<int>> groups;
    for(const auto& c:controls)groups[{c.order,c.group.empty()?"VOICE":c.group}].push_back(c.shown);
    std::vector<PluginDesignPage> pages;
    for(const auto& pair:groups){const auto& ids=pair.second;unsigned parts=unsigned((ids.size()+5)/6);
        for(unsigned part=0;part<parts;++part){PluginDesignPage p;std::snprintf(p.title,sizeof p.title,"%s",pair.first.second.c_str());p.part=uint16_t(part+1);p.parts=uint16_t(parts);
            for(unsigned k=0;k<6&&part*6+k<ids.size();++k)p.shown[k]=int16_t(ids[part*6+k]);
            pages.push_back(p);
        }
    }
    return pages;
}
}
