#!/usr/bin/env python3
"""Render shared 0.2.0 guide text into local website/offline HTML; never publish."""
from pathlib import Path
import argparse
import hashlib
import html
import importlib.util
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/runtime')
PAGES={'index.html':'MANUAL_020_EN.md','quickstart.html':'FIRST_GROOVE_020_EN.md',
       'essentials.html':'QUICK_REFERENCE_020_EN.md','structure.html':'SYSTEM_MAP_020_EN.md',
       'manual-ko.html':'USER_MANUAL_KO_DRAFT.md','first-groove-ko.html':'FIRST_GROOVE_020_KO.md',
       'controls-ko.html':'GETTING_STARTED_KO.md'}
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:30px}body{margin:0;background:#0c0d0d;color:#eee;font:16px/1.7 Arial,Helvetica,sans-serif}a{color:inherit;text-underline-offset:4px}a:hover{color:#fff}header{padding:24px 4vw;border-bottom:1px solid #353737}header strong{font-size:21px;letter-spacing:-.6px}header span{color:#aaa;font-size:13px}header nav{display:flex;gap:12px 24px;flex-wrap:wrap;margin-top:18px;font-size:14px}.layout{display:grid;grid-template-columns:250px minmax(0,900px);gap:38px;max-width:1250px;margin:32px auto;padding:0 24px}aside{position:sticky;top:20px;align-self:start;max-height:90vh;overflow:auto;font-size:13px}summary{cursor:pointer;font-weight:bold;padding:12px 0}.toc a{display:block;padding:6px 10px;color:#bbb;text-decoration:none;border-left:1px solid #353737}.doc{min-width:0;padding-bottom:70px}.doc h1{font-size:clamp(32px,4vw,54px);line-height:1.08;letter-spacing:-1.5px;margin:12px 0 28px}.doc h2{font-size:28px;line-height:1.25;border-top:1px solid #454747;padding-top:30px;margin:48px 0 18px;letter-spacing:-.7px}.doc h3{font-size:21px;line-height:1.3;margin:30px 0 12px}.doc p,.doc li{max-width:82ch}.doc li{padding-bottom:8px}.doc ol{padding-left:26px}.doc img{max-width:100%;height:auto;border:1px solid #353737;display:block;margin:24px 0}.doc table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.55;overflow-wrap:anywhere;margin:20px 0}.doc th,.doc td{border:1px solid #454747;padding:12px;vertical-align:top;text-align:left}.doc th{background:#202222}.doc td:first-child{min-width:95px}.key,code{background:#202222;color:#fff;padding:2px 4px;border:1px solid #454747;font-size:.9em}.key{line-height:2.2}.notice{padding:14px 18px;border:1px solid #626565;margin:0 0 24px;font-size:14px}.language{display:flex;gap:18px;flex-wrap:wrap}footer{border-top:1px solid #353737;padding:26px 4vw;color:#aaa;font-size:13px}.doc pre{overflow:auto} @media(max-width:900px){.layout{display:block;margin-top:12px;padding:0 18px}aside{position:static;max-height:none;margin-bottom:26px}.doc h1{font-size:36px}.doc h2{font-size:25px}.doc table{font-size:12px}.doc th,.doc td{padding:8px}.doc td:first-child{min-width:70px}.doc li{padding-bottom:10px}}@media print{body{background:white;color:black;font-size:11pt}.layout{display:block;max-width:none;margin:0;padding:0}header,aside,.notice,footer{display:none}.doc{padding:0}.doc h1{font-size:25pt}.doc h2{font-size:18pt;break-after:avoid}.doc h3{break-after:avoid}.doc table{font-size:9pt}.doc th{background:#eee}.doc img{max-height:250mm;object-fit:contain;break-inside:avoid}.key,code{background:#eee;color:black}.doc a{color:black}}'''

def render(output, offline=False):
    spec=importlib.util.spec_from_file_location('device_manual_converter',RUNTIME/'tools/web_bundle.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output.mkdir(parents=True,exist_ok=True);(output/'guide-020.css').write_text(CSS)
    (output/'images').mkdir(exist_ok=True)
    for n in ('essential-controls','os-structure'):
        shutil.copy2(ROOT/'assets/manual'/(n+'.svg'),output/'images'/(n+'.svg'))
    for p in (ROOT/'assets/manual').glob('020-*.png'):shutil.copy2(p,output/'images'/p.name)
    shutil.copy2(ROOT/'vendor/rhythmer/LICENSE',output/'LICENSE.txt')
    reverse={v:k for k,v in PAGES.items()};manifest={}
    for page,name in PAGES.items():
        source=RUNTIME/'docs/guide'/name
        converter=module.Converter(source);text=source.read_text();body=converter.convert(text)
        for doc,target in reverse.items():body=body.replace('/docs/manual/'+doc[:-3],target)
        for n in ('essential-controls','os-structure'):body=body.replace('/img/rhythmer/'+n+'.png','images/'+n+'.svg')
        body=re.sub(r'/img/rhythmer/(020-[^"<>]+\.png)',r'images/\1',body)
        if page=='index.html':
            aliases={'start':'3-start-a-project-and-add-an-instrument','acid-generator':'11-use-acid-gen','break-manipulator':'12-load-a-break-and-return-to-its-controls','break-performance':'brk-perf-what-each-page-does','credits':'credits-and-testing-status'}
            for alias,target in aliases.items():body=re.sub(r'(<h[23] id="'+re.escape(target)+r'">)',r'<span id="'+alias+r'"></span>\1',body,count=1)
        title=text.splitlines()[0].lstrip('# ');ko=page.endswith('-ko.html')
        toc=''.join('<a href="#'+html.escape(anchor)+'">'+html.escape(label)+'</a>' for level,label,anchor in converter.headings if level==2)
        header='<header><strong>RHYTHMER OS 0.2.0</strong> <span> / MPC SAMPLE · USER GUIDE</span><nav><a href="../">Website</a><a href="index.html">Manual</a><a href="quickstart.html">First Groove</a><a href="essentials.html">Controls</a><a href="structure.html">System structure</a><a href="manual-ko.html">한국어</a><a href="../installer/">Installation</a></nav></header>'
        if offline:
            header=header.replace('href="../"','href="https://jazzyrhythmer.github.io/mpc-sample/"').replace('href="../installer/"','href="https://jazzyrhythmer.github.io/mpc-sample/installer/"')
        notice='이 문서는 0.2.0 화면의 조작을 설명합니다. 먼저 헤더의 트랙 번호와 현재 버튼명을 확인하세요.' if ko else 'These instructions use the 0.2.0 controls. Check the selected track number and current button labels before each action.'
        document='<!doctype html><html lang="'+('ko' if ko else 'en')+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' — MPC Sample</title><link rel="stylesheet" href="guide-020.css"></head><body>'+header+'<div class="layout"><aside><details class="toc" id="contents"><summary>'+('목차' if ko else 'On this page')+'</summary>'+toc+'</details></aside><main class="doc"><p class="notice">'+notice+'</p>'+body+'</main></div><footer>RHYTHMER OS — by jazzy rhythmer. Based on Melodee by Kerem Kiliç (Ellic Studio), sample-base and credited engine projects. Early beta; software examples are not physical-device recordings. <a href="LICENSE.txt">Licence</a></footer><script>document.getElementById("contents").open=matchMedia("(min-width:901px)").matches;</script></body></html>'
        (output/page).write_text(document)
        manifest[page]={'version':'0.2.0','source':name,'source_sha256':hashlib.sha256((ROOT/'docs'/name).read_bytes()).hexdigest(),'sections':len(converter.headings),'publication_performed_by_generator':False}
    (output/'guide-020-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Rendered',len(PAGES),'practical guide pages; publication not performed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--offline',action='store_true');args=p.parse_args();render(args.output_dir,args.offline)
