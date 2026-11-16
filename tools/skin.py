#!/usr/bin/env python3
"""Black/white pixel geometry using existing render/layout infrastructure."""
from pathlib import Path
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET


def apply(root):
    def patch(relative, before, after):
        p=root/'src/rhythmer/ui'/relative
        text=p.read_text()
        if text.count(before)!=1: raise RuntimeError(f'Skin anchor changed: {relative}: {before[:60]}')
        p.write_text(text.replace(before,after))

    p=root/'src/rhythmer/ui/tokens.h'
    text=p.read_text()
    start=text.index('inline const juce::Colour bg =')
    end=text.index('\n}',start)
    text=text[:start]+'''inline const juce::Colour bg = hex(0x000000), panel = hex(0x101010), surf = hex(0x171717), raised = hex(0x262626),
    quiet = hex(0x0A0A0A), line = hex(0x383838), text = hex(0xFFFFFF), sec = hex(0xE0E0E0), mid = hex(0xB8B8B8),
    dim = hex(0x888888), rec = hex(0xFFFFFF), amber = hex(0xD0D0D0), play = hex(0xFFFFFF);
''' + text[end:]
    # Screen accents are achromatic. Original physical pad colour mapping stays in shades.h.
    text=re.sub(r'return hex\((?:track|loop)_shades\[[^;]+;', 'return colour::text;',text)
    text=text.replace('unsigned track)', 'unsigned /*track*/)').replace('unsigned track, unsigned knob)', 'unsigned /*track*/, unsigned /*knob*/)')
    text=text.replace('unsigned loop)', 'unsigned /*loop*/)').replace('unsigned loop, unsigned knob)', 'unsigned /*loop*/, unsigned /*knob*/)')
    text=text.replace('NIGHT palette, one colour per track','RHYTHMER monochrome palette, numbered tracks')
    p.write_text(text)
    patch('paint.cpp', 'if (radius > 0) g.fillRoundedRectangle(x, y, w, h, radius);\n    else g.fillRect(juce::Rectangle<float>(x, y, w, h));',
          '(void)radius;\n    g.fillRect(juce::Rectangle<float>(std::round(x), std::round(y), std::round(w), std::round(h)));')
    patch('paint.cpp', 'g.drawRoundedRectangle(x + half, y + half, w - thickness, h - thickness, radius, thickness);',
          '(void)radius;\n    g.drawRect(juce::Rectangle<float>(x + half, y + half, w - thickness, h - thickness), thickness);')
    patch('paint.cpp', 'g.fillEllipse(cx - r, cy - r, 2 * r, 2 * r);',
          'if(r<=3) g.fillRect(juce::Rectangle<float>(std::round(cx-r),std::round(cy-r),2*r,2*r));\n    else g.fillEllipse(cx-r,cy-r,2*r,2*r);')
    apply_boot(root)
    p=root/'src/rhythmer/ui/knobs.cpp'
    text=p.read_text()
    # Original 5x7 numeric glyphs, code-native rather than a new font/library dependency.
    glyphs=['01110' '10001' '10011' '10101' '11001' '10001' '01110',
            '00100' '01100' '00100' '00100' '00100' '00100' '01110',
            '01110' '10001' '00001' '00010' '00100' '01000' '11111',
            '11110' '00001' '00001' '01110' '00001' '00001' '11110',
            '00010' '00110' '01010' '10010' '11111' '00010' '00010',
            '11111' '10000' '10000' '11110' '00001' '00001' '11110',
            '01110' '10000' '10000' '11110' '10001' '10001' '01110',
            '11111' '00001' '00010' '00100' '01000' '01000' '01000',
            '01110' '10001' '10001' '01110' '10001' '10001' '01110',
            '01110' '10001' '10001' '01111' '00001' '00001' '01110',
            '00000' '00000' '00000' '11111' '00000' '00000' '00000',
            '00000' '00000' '00000' '00000' '00000' '00100' '00100']
    helper='''
namespace {
float pixel_number(Paint& p,const juce::String& value,float x,float y,float room,juce::Colour ink) {
    static const char* glyphs[] {GLYPHS};
    if(value.isEmpty()||value.length()*12-2>room)return -1;
    for(auto c:value)if(!((c>='0'&&c<='9')||c=='-'||c=='.'))return -1;
    unsigned col=0;
    for(auto c:value) {
        const char* bits=glyphs[c=='-'?10:c=='.'?11:c-'0'];
        for(unsigned yy=0;yy<7;yy++)for(unsigned xx=0;xx<5;xx++)
            if(bits[yy*5+xx]=='1')p.fill(x+col*12+xx*2,y+yy*2,2,2,ink);
        ++col;
    }
    return float(col*12-2);
}
}
'''.replace('GLYPHS',','.join('"'+g+'"' for g in glyphs))
    text=text.replace('namespace rhythmer::ui {','namespace rhythmer::ui {\n'+helper)
    before='float vw = p.text(c.value, inner, low ? top + 23 : top + 15, room, low ? 16 : 22, shown);'
    after='''float vw = low?-1:pixel_number(p,c.value,inner,top+19,room,value.colour);
        if(vw<0) vw = p.text(c.value, inner, low ? top + 23 : top + 15, room, low ? 16 : 22, shown);'''
    if text.count(before)!=1:raise RuntimeError('Pixel value anchor changed')
    text=text.replace(before,after)
    start=text.index('        p.fill(inner, gy, iw, 2, colour::line, 1);');end=text.index('        if (c.state == State::Pickup',start)
    text=text[:start]+'''        // Sixteen discrete pixels: numeric values remain exact in the card above.
        for(unsigned cell=0;cell<16;cell++) {
            float at=(cell+0.5f)/16;
            bool lit=c.bipolar?(at>=std::min(0.5f,fill)&&at<=std::max(0.5f,fill)):at<fill;
            p.fill(inner+cell*iw/16,gy,3,2,lit?colour::text:colour::line);
        }
''' + text[end:]
    p.write_text(text)
    print('Applied RHYTHMER monochrome/pixel skin; existing layouts and readable text sizes retained')


def apply_boot(root):
    source=Path(__file__).resolve().parents[1]
    shutil.copy2(source/'extensions/ui/boot.cpp',root/'src/rhythmer/ui/boot.cpp')
    svg=ET.parse(source/'assets/device/mpc-sample.svg').getroot()
    x,y,w,h=map(float,svg.attrib['viewBox'].split())
    header=['// Official inMusic device mark; assets/device/NOTICE.md. Not CC0 RHYTHMER artwork.',
            '#pragma once','namespace rhythmer::ui {',
            'struct DeviceMarkPath { const char* commands; bool nonzero, filled, white; float stroke; bool stroke_white; };',
            f'inline constexpr float device_mark_x={x}f, device_mark_y={y}f, device_mark_w={w}f;',
            'inline constexpr DeviceMarkPath device_mark_paths[] {']
    for path in svg.findall('{http://www.w3.org/2000/svg}path'):
        commands=re.sub(r'([MLCZ])',lambda m:' '+m.group(1).lower()+' ',path.attrib['d']).replace(',',' ')
        header.append('{'+','.join([json.dumps(commands),str(path.attrib.get('fill-rule')!='evenodd').lower(),
                     str(path.attrib['fill']!='none').lower(),str(path.attrib['fill']=='#ffffff').lower(),
                     str(float(path.attrib.get('stroke-width',1)))+'f' if path.attrib.get('stroke','none')!='none' else '0.0f',
                     str(path.attrib.get('stroke')=='#ffffff').lower()])+'},')
    header+=['};','}']
    (root/'src/rhythmer/ui/device_mark.h').write_text('\n'.join(header)+'\n')
    svg=ET.parse(source/'assets/brand/rhythmer-os.svg').getroot()
    header=['// Original Rhythmer OS wordmark by jazzy rhythmer. CC0-1.0.',
            '#pragma once','#include "rhythmer/ui/device_mark.h"','namespace rhythmer::ui {',
            'inline constexpr DeviceMarkPath rhythmer_mark_paths[] {']
    for group in svg.findall('{http://www.w3.org/2000/svg}g'):
        for path in group.findall('{http://www.w3.org/2000/svg}path'):
            commands=re.sub(r'([MLCZ])',lambda m:' '+m.group(1).lower()+' ',path.attrib['d'])
            header.append('{'+json.dumps(commands)+',true,true,true,'+group.attrib['stroke-width']+'f,true},')
    header+=['};','}']
    (root/'src/rhythmer/ui/rhythmer_mark.h').write_text('\n'.join(header)+'\n')
    p=root/'src/rhythmer/tools.cpp'
    text=p.read_text()
    start=text.index('    for (uint32_t ms = 0;; ms += 1000 / 30) {',text.index('int boot_frames('))
    end=text.index('    std::cout << "RHYTHMER_BOOT frames="',start)
    text=text[:start]+'''    ui::BootAnimation boot2;
    for (uint32_t ms = 0;; ms += 1000 / 30) {
        for(int scale:{1,2}) {
            auto& animation=scale==1?boot:boot2;
            juce::Image image(juce::Image::ARGB,screen_width*scale,screen_height*scale,true);
            {
                juce::Graphics g(image);g.addTransform(juce::AffineTransform::scale(float(scale)));
                if(animation.covers(ms))animation.draw(g,ms);
                else {draw(g,*snapshot);animation.draw(g,ms);}
            }
            char name[40];std::snprintf(name,sizeof name,"/boot-%03u%s.png",written,scale==2?"@2x":"");
            save_png(image,folder+name);
        }
        ++written;if(boot.finished(ms))break;
    }
''' + text[end:]
    p.write_text(text)


if __name__=='__main__':apply(Path(sys.argv[1]))
