// SPDX-License-Identifier: AGPL-3.0-only
// Uses the existing control-thread read and stable shown IDs. No audio changes.
void PluginRack::edit_panel(unsigned entry,unsigned page,unsigned half,PluginPanel& out) const {
    const auto previous=out.design&&out.entry==entry&&out.design_page<out.design_count?out.design_pages[out.design_page]:PluginDesignPage{};
    const auto revision=out.layout_revision;const bool preserve=out.design&&out.entry==entry;
    panel(entry,0,out);
    if(out.status!=PluginStatus::Ready)return;
    std::lock_guard<std::mutex> held(lock);auto* h=entries[entry].live;if(!h)return;
    if(!is_sound_rack(h->instance.get()))return;
    out.design=true;out.params={};out.window={};
    if(!sound_rack_design_pages(h->instance.get(),out))return;
    out.design_page=uint16_t(std::min<unsigned>(page,out.design_count-1));
    if(preserve&&revision!=out.layout_revision){
        out.design_page=0;
        for(unsigned i=0;i<out.design_count;++i)if(std::string(out.design_pages[i].title)==previous.title){out.design_page=uint16_t(i);if(out.design_pages[i].part>=previous.part)break;}
    }
    const auto& selected=out.design_pages[out.design_page];out.design_half=uint8_t(selected.shown[3]>=0?std::min(half,1u):0u);
    const auto& params=h->instance->getParameters();out.window={};out.params={};
    for(unsigned k=0;k<6;++k){int at=selected.shown[k];if(at<0||unsigned(at)>=h->shown.size())continue;
        auto& card=out.window[k];auto* p=params[h->shown[size_t(at)]];card.used=true;card.shown=int16_t(at);
        put(card.name,sizeof card.name,p->getName(int(sizeof card.name)-1).trim().toStdString());float v=p->getValue();
        put(card.text,sizeof card.text,tidy(p->getText(v,96).trim().toStdString()));card.value=int16_t(std::lround(std::clamp(v,0.0f,1.0f)*plugin_param_max));
        card.initial=int16_t(std::lround(std::clamp(p->getDefaultValue(),0.0f,1.0f)*plugin_param_max));
        const int steps=p->getNumSteps();card.steps=steps>=2&&steps<plugin_param_max?uint16_t(steps):0;
    }
    for(unsigned k=0;k<3;++k)out.params[k]=out.window[out.design_half*3+k];
    if(sound_rack_revision(h->instance.get())!=out.layout_revision){out.params={};out.window={};out.design=false;out.status=PluginStatus::Loading;}
}
