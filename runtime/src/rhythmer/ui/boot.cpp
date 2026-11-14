// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Kerem Kilic (Ellic Studio)
// RHYTHMER startup composition and geometry: jazzy rhythmer.
// Official MPC Sample mark: inMusic Brands, Inc.; see assets/device/NOTICE.md.
#include "rhythmer/ui/boot.h"
#include "rhythmer/ui/boot_art.h"
#include "rhythmer/ui/device_mark.h"
#include "rhythmer/ui/rhythmer_mark.h"
#include <algorithm>
#include <array>
#include <cmath>
#include "rhythmer/ui/paint.h"

namespace rhythmer {
#include "rhythmer/pages/performance_art.inc"
namespace ui {
namespace {
juce::Image decode(const char* base64) {
    juce::MemoryOutputStream png;
    if(!juce::Base64::convertFromBase64(png,base64))return {};
    auto image=juce::ImageFileFormat::loadFrom(png.getData(),png.getDataSize());
    if(!image.isValid()||image.getWidth()!=320||image.getHeight()!=240)return {};
    return image.convertedToFormat(juce::Image::ARGB);
}
float smooth(float t) {t=std::clamp(t,0.0f,1.0f);return t*t*(3-2*t);}
void device_mark(juce::Graphics& g,float alpha) {
    auto transform=juce::AffineTransform::translation(-device_mark_x,-device_mark_y)
        .scaled(280.0f/device_mark_w).translated(20,24);
    // Cache the official outlines once. Draw paths into the destination itself,
    // so @2x and the live Graphics transform never enlarge a 320px logo bitmap.
    static const auto paths=[] {
        std::array<juce::Path,std::size(device_mark_paths)> result;
        for(size_t i=0;i<result.size();++i){result[i].restoreFromString(device_mark_paths[i].commands);result[i].setUsingNonZeroWinding(device_mark_paths[i].nonzero);}
        return result;
    }();
    for(size_t i=0;i<paths.size();++i) {
        const auto& item=device_mark_paths[i];const auto& path=paths[i];
        if(item.filled) {
            g.setColour((item.white?juce::Colours::white:juce::Colours::black).withAlpha(alpha));g.fillPath(path,transform);
        }
        if(item.stroke>0) {
            g.setColour((item.stroke_white?juce::Colours::white:juce::Colours::black).withAlpha(alpha));
            g.strokePath(path,juce::PathStrokeType(item.stroke),transform);
        }
    }
}
void rhythmer_mark(juce::Graphics& g,float progress,float alpha) {
    static const auto paths=[] {
        std::array<juce::Path,std::size(rhythmer_mark_paths)> result;
        for(size_t i=0;i<result.size();++i)result[i].restoreFromString(rhythmer_mark_paths[i].commands);
        return result;
    }();
    const auto transform=juce::AffineTransform::translation(62.0f,85.0f);
    g.setColour(juce::Colours::white);
    for(size_t i=0;i<paths.size();++i){
        float settle=smooth((progress-float(i)*0.035f)/0.64f);
        float drift=(1-settle)*(i%2?5.0f:-5.0f);
        g.setColour(juce::Colours::white.withAlpha(settle*alpha));
        g.fillPath(paths[i],transform.translated(drift,-drift*0.6f));
    }
}
}
uint32_t BootAnimation::elapsed(uint32_t now) {
    if(!started){started=true;start=now;}return now-start;
}
bool BootAnimation::finished(uint32_t now) {
    if(!loaded)load();
    return broken||elapsed(now)>=fade_from+out_ms;
}
bool BootAnimation::covers(uint32_t now){return !finished(now)&&elapsed(now)<fade_from;}
void BootAnimation::skip(uint32_t now){fade_from=std::min(fade_from,elapsed(now));}
void BootAnimation::load() {
    loaded=true;logo=decode(boot_logo_png);backdrop=decode(boot_backdrop_png);
    broken=!logo.isValid()||!backdrop.isValid();if(broken)return;
    canvas=juce::Image(juce::Image::ARGB,320,240,false);
}
void BootAnimation::compose(uint32_t at) {
    if(composed==int64_t(at))return;
    composed=at;
    juce::Graphics g(canvas);g.fillAll(juce::Colours::black);
    if(at<black_ms)return;
    const int ms=int(at-black_ms);
    // Author signature only; all animated geometry and brand marks are drawn
    // into the destination at its native resolution in draw().
    juce::Graphics::ScopedSaveState save(g);g.reduceClipRegion(0,122,320,22);
    g.setOpacity(smooth((ms-1050)/480.0f));g.drawImageAt(logo,0,0);

}
void BootAnimation::draw(juce::Graphics& g,uint32_t now) {
    if(finished(now))return;
    uint32_t at=elapsed(now);compose(std::min(at,fade_from));
    float opacity=at<fade_from?1.0f:1.0f-smooth(float(at-fade_from)/float(out_ms));
    {
        juce::Graphics::ScopedSaveState save(g);
        g.setImageResamplingQuality(juce::Graphics::lowResamplingQuality);
        g.setOpacity(opacity);g.drawImageAt(canvas,0,0);
    }
    const uint32_t mark_at=std::min(at,fade_from);
    if(mark_at>=black_ms){
        const float ms=float(mark_at-black_ms),t=ms*.001f;
        const float unfold=smooth(ms/1050.0f),settle=smooth((ms-850)/700.0f);
        juce::Graphics::ScopedSaveState save(g);
        // A massive interlocking monument, built from solid rectangular
        // blocks. Opposing tiers lock together before the brand reveal.
        struct V {float x,y,z;};struct Face {std::array<V,4> v;float z,light;};
        std::array<Face,96> faces{};unsigned count=0;
        const float yaw=.52f+t*.24f,tilt=.36f+.12f*std::sin(t*.8f);
        auto rotate=[&](V v){float xx=v.x*std::cos(yaw)+v.z*std::sin(yaw),zz=-v.x*std::sin(yaw)+v.z*std::cos(yaw);return V{xx,v.y*std::cos(tilt)-zz*std::sin(tilt),v.y*std::sin(tilt)+zz*std::cos(tilt)};};
        auto block=[&](V centre,V size){
            std::array<V,8> vertices;
            for(int n=0;n<8;++n)vertices[size_t(n)]=rotate({centre.x+(n&1?size.x:-size.x),centre.y+(n&2?size.y:-size.y),centre.z+(n&4?size.z:-size.z)});
            const std::array<std::array<int,4>,6> sides{{{{0,1,3,2}},{{4,6,7,5}},{{0,4,5,1}},{{2,3,7,6}},{{0,2,6,4}},{{1,5,7,3}}}};
            const float lights[]{.22f,.75f,.34f,.95f,.42f,.64f};
            for(size_t n=0;n<sides.size();++n){Face face{{},0,lights[n]};for(size_t k=0;k<4;++k){face.v[k]=vertices[size_t(sides[n][k])];face.z+=face.v[k].z*.25f;}faces[count++]=face;}
        };
        const float spread=(1-unfold)*1.6f;
        for(int tier=0;tier<5;++tier){
            const float y=(tier-2)*.32f,slide=(tier%2?1.0f:-1.0f)*spread;
            if(tier%2)block({slide,y,0},{.34f,.135f,1.03f});
            else block({0,y,slide},{1.03f,.135f,.34f});
        }
        block({-.7f,-.03f,-.7f-spread},{.16f,.86f,.16f});
        block({.7f,-.03f,.7f+spread},{.16f,.86f,.16f});
        std::sort(faces.begin(),faces.begin()+count,[](const Face& a,const Face& b){return a.z<b.z;});
        const float hero=smooth(ms/300.0f)*(1-settle*.94f)*opacity;
        for(unsigned i=0;i<count;++i){const auto& f=faces[i];juce::Path path;
            for(unsigned n=0;n<4;++n){const auto& v=f.v[n];float depth=3.3f/(3.3f-v.z*.4f),xx=160+v.x*99*depth,yy=104+v.y*78*depth;if(n)path.lineTo(xx,yy);else path.startNewSubPath(xx,yy);}path.closeSubPath();
            const float shade=std::clamp(f.light+f.z*.16f,.12f,.9f);
            g.setColour(juce::Colour::fromFloatRGBA(shade,shade,shade,hero));g.fillPath(path);
            g.setColour(juce::Colours::white.withAlpha(hero*.85f));g.strokePath(path,juce::PathStrokeType(.6f));
        }
        // Render the real engine sculptures at miniature scale. The small
        // adapter supplies deterministic startup gestures, never DSP or notes.
        struct BootSignal {
            struct Ui {int track=0;} ui;
            struct Track {uint8_t last_note=60;struct Mix {int pan=0;} mix;} current;
            std::array<int16_t,16> held_keys{};
            std::array<float,16> meters{};
            uint32_t now=0;
            const Track& track()const{return current;}
        } signal;
        signal.held_keys.fill(-1);signal.held_keys[0]=60;signal.meters.fill(.55f);signal.now=mark_at;
        const char* engines[]{"Sophie","Aphex","Plaits","Break Engine"};
        ui::Paint painter(g);
        for(int k=0;k<4;++k){float appear=smooth((ms-1100-k*100)/500.0f);if(appear<=0)continue;
            signal.ui.track=k;signal.current.last_note=uint8_t(48+k*5);
            performance_art(painter,signal,engines[k],"Startup",20+k*74,158+(1-appear)*12,58,47,k*3,appear*opacity,true);
        }

    }
    if(mark_at>=black_ms+450){
        juce::Graphics::ScopedSaveState save(g);
        const float reveal=smooth(float(mark_at-black_ms-450)/600.0f);
        device_mark(g,opacity*reveal);
    }
    if(mark_at>=black_ms+700){
        juce::Graphics::ScopedSaveState save(g);
        const float reveal=smooth(float(mark_at-black_ms-700)/750.0f);
        rhythmer_mark(g,reveal,opacity);
    }
}
} // namespace ui
} // namespace rhythmer
