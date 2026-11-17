#!/usr/bin/env python3
"""Render the illustrated English manual and First Groove, online or offline."""
from pathlib import Path
import argparse, hashlib, html, importlib.util, json, re, shutil, struct

ROOT = Path(__file__).resolve().parents[1]
WEB_ASSETS = ROOT/'assets/manual/web'
RUNTIME = Path('/Volumes/SSD/Development/BuildCache/rhythmer-os/runtime')
PAGES = {'index.html':'MANUAL_020_EN.md', 'quickstart.html':'FIRST_GROOVE_020_EN.md'}
ALIASES = {'manual-ko.html':'index.html', 'first-groove-ko.html':'quickstart.html',
           'controls-ko.html':'index.html#essential-controls',
           'essentials.html':'index.html#essential-controls', 'structure.html':'index.html#system-structure'}
VIDEO = 'https://github.com/jazzyrhythmer/mpc-sample-rhythmer-os/releases/download/v0.4.0-beta.3-r2/RHYTHMER-Your-First-Groove-YouTube-v4.mp4'
CSS = '''
:root{color-scheme:dark;--bg:#0c0d0d;--fg:#eee;--muted:#aaa;--line:#343636}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:100px}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.75 Arial,Helvetica,sans-serif}
a{color:inherit;text-underline-offset:4px}a:hover{color:white}a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid white;outline-offset:5px}
.skip{position:absolute;top:-70px;left:20px}.skip:focus{top:8px;z-index:200;background:white;color:black;padding:8px}
.manual-shell{max-width:1320px;margin:0 auto;padding:32px 48px 90px}.manual-trail{display:flex;gap:12px;font:10px/1.6 monospace;color:var(--muted);letter-spacing:.07em;margin-bottom:32px}.manual-trail a{text-decoration:none}
.manual-layout{display:grid;grid-template-columns:230px minmax(0,870px);gap:42px}.manual-layout aside{position:sticky;top:85px;align-self:start;max-height:calc(100vh - 110px);overflow:auto;font-size:12px;padding-right:10px}.toc summary{cursor:pointer;font:700 11px/1.5 monospace;letter-spacing:.08em;padding:0 0 18px}.toc a{display:block;padding:7px 12px;color:#aaa;text-decoration:none;border-left:1px solid var(--line);line-height:1.5}.toc a:hover,.toc a[aria-current]{color:white;border-left:2px solid white;background:#171919}.doc{min-width:0}.doc h1{font-size:clamp(40px,5.5vw,72px);line-height:1.04;letter-spacing:-.065em;margin:0 0 25px;font-weight:900}.doc>p:first-of-type{font-size:18px;color:#bbb;line-height:1.65}.doc h2{font-size:clamp(27px,3vw,36px);line-height:1.18;border-top:1px solid #454747;padding-top:34px;margin:64px 0 24px;letter-spacing:-1px;scroll-margin-top:100px}.doc h3{font-size:23px;line-height:1.3;margin:36px 0 16px;letter-spacing:-.5px}.doc p,.doc li{max-width:82ch}.doc li{padding-bottom:10px}.doc ol{padding-left:26px}.doc figure{display:inline-block;vertical-align:top;width:min(100%,390px);margin:12px 16px 24px 0}.doc figure img{display:block;max-width:100%;width:100%;height:auto;border:1px solid #454747;background:#000;image-rendering:auto}.doc figcaption{font:11px/1.65 monospace;color:#aaa;letter-spacing:0;padding:10px 2px 0}.doc figure.sheet{display:block;width:100%;max-width:860px;margin:24px 0}.doc .table-scroll{max-width:100%;overflow-x:auto;margin:22px 0}.doc table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.65;overflow-wrap:anywhere}.doc th,.doc td{border:1px solid #454747;padding:12px;vertical-align:top;text-align:left}.doc th{background:#202222}.doc th:first-child,.doc td:first-child{min-width:110px}.doc code{background:#202222;color:#fff;padding:2px 4px;border:1px solid #454747;font-size:.9em}.doc pre{overflow:auto}
.guide-video{width:100%;display:block;background:#000;border:1px solid #454747;aspect-ratio:16/9}.guide-video-block{margin:28px 0}.guide-links{display:flex;gap:14px 24px;flex-wrap:wrap;margin:22px 0;font:700 11px/1.5 monospace;letter-spacing:.03em}.guide-links a{padding:14px 18px;border:1px solid #555;text-decoration:none}.guide-links a:first-child{background:#eee;color:#111;border-color:#eee}.video-caption{font:12px/1.7 monospace;color:#aaa;margin-top:12px}.manual-footer{max-width:1320px;margin:auto;padding:32px 48px;border-top:1px solid var(--line);font:11px/1.8 monospace;color:#aaa}.manual-footer a{margin-right:18px}.manual-tools{display:flex;gap:18px;margin:0 0 28px;font:11px/1.5 monospace}.manual-tools button{background:transparent;color:#bbb;border:1px solid #555;padding:7px 12px;font:inherit;cursor:pointer}
@media(min-width:901px){.doc figure:not(.sheet){width:calc(50% - 18px)}}
@media(max-width:1100px) and (min-width:761px){.manual-layout aside{top:110px;max-height:calc(100vh - 130px)}html{scroll-padding-top:140px}.doc h2{scroll-margin-top:140px}}
@media(max-width:900px){.manual-shell{padding:26px 24px 60px}.manual-layout{display:block}.manual-layout aside{position:static;max-height:none;margin:0 0 28px;padding:0;border-bottom:1px solid #454747}.toc summary{padding:12px 0}.toc a{padding:9px 12px}.doc h1{font-size:46px}.doc h2{margin-top:48px}.doc figure{max-width:100%;margin-right:0;width:100%}.doc th,.doc td{padding:10px}.doc table{font-size:13px}.manual-footer{padding:28px 24px}.manual-trail{margin-bottom:24px}.manual-tools{margin-bottom:16px}}
@media(max-width:760px){html{scroll-padding-top:200px}.doc h2{scroll-margin-top:200px}.doc h1{font-size:40px}.doc>p:first-of-type{font-size:16px}.doc figure.sheet{margin:20px 0}.guide-links a{width:100%;text-align:center}.manual-trail{font-size:9px}.doc th:first-child,.doc td:first-child{min-width:90px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:#fff!important;color:#111}.jr-site-header,.manual-trail,.manual-layout aside,.manual-tools,.manual-footer,.guide-video-block,.guide-links,.skip{display:none!important}.manual-shell{padding:0;max-width:none}.manual-layout{display:block}.doc h1{font-size:32pt}.doc h2{font-size:20pt;break-after:avoid}.doc h3{break-after:avoid}.doc p,.doc li{font-size:11pt}.doc figure{width:46%;break-inside:avoid}.doc figure.sheet{width:100%}.doc figure.sheet img{max-height:235mm;object-fit:contain}.doc table{font-size:9pt}.doc th{background:#eee}.doc code{background:#eee;color:#111}.doc a,.doc>p:first-of-type{color:#111}.doc .table-scroll{overflow:visible}}
'''

def render(output, offline=False):
    spec=importlib.util.spec_from_file_location('device_manual_converter',RUNTIME/'tools/web_bundle.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    class WebsiteConverter(module.Converter):
        def href(self,target):
            path,mark,anchor=target.partition('#')
            routes={**{name:page for page,name in PAGES.items()},'QUICK_REFERENCE_020_EN.md':'index.html#essential-controls','SYSTEM_MAP_020_EN.md':'index.html#system-structure'}
            if path in routes:return routes[path]+(mark+anchor if mark and '#' not in routes[path] else '')
            return target
        def image(self,target):
            source=(self.source.parent/target).resolve()
            if not source.is_file():raise RuntimeError('Missing guide image: '+target)
            return 'images/'+source.name
    output.mkdir(parents=True,exist_ok=True);(output/'images').mkdir(exist_ok=True)
    (output/'guide-020.css').write_text(CSS)
    for p in (ROOT/'assets/manual').iterdir():
        if p.suffix in ('.png','.svg','.json'):shutil.copy2(p,output/'images'/p.name)
    shutil.copy2(ROOT/'vendor/rhythmer/LICENSE',output/'LICENSE.txt')
    for n in ('platform-navigation.css','platform-navigation.js'):shutil.copy2(WEB_ASSETS/n,output/n)
    assets=output/'assets';assets.mkdir(exist_ok=True)
    for n in ('fg4-youtube.jpg','fg4-youtube.vtt'):
        if (WEB_ASSETS/n).resolve()!=(assets/n).resolve():shutil.copy2(WEB_ASSETS/n,assets/n)
    header=(WEB_ASSETS/'site-header.html').read_text().strip()
    header=header.replace('data-section="manual"','aria-current="page" data-section="manual"')
    manifest={};reverse={v:k for k,v in PAGES.items()}
    reverse.update({'QUICK_REFERENCE_020_EN.md':'index.html#essential-controls','SYSTEM_MAP_020_EN.md':'index.html#system-structure'})
    for page,name in PAGES.items():
        text=(ROOT/'docs'/name).read_text();converter=WebsiteConverter(ROOT/'docs'/name);body=converter.convert(text)
        for doc,target in reverse.items():body=body.replace('/docs/manual/'+doc[:-3],target)
        body=re.sub(r'/img/(?:manual|rhythmer)/([^"<>]+)',r'images/\1',body)
        body=body.replace('images/essential-controls.png','images/essential-controls.svg').replace('images/os-structure.png','images/os-structure.svg')
        # Converter resolves source images under assets/manual, independent of runtime guide copies.
        body=re.sub(r'(?:\.\./)?assets/manual/([^"<>]+)',r'images/\1',body)
        body=re.sub(r'<figure>(<img[^>]*(?:essential-controls|os-structure)[^>]*>)',r'<figure class="sheet">\1',body)
        body=body.replace('loading="lazy">','loading="lazy" decoding="async">')
        def sized_image(match):
            tag=match[0];src=re.search(r'src="([^"]+)"',tag)[1];asset=output/src
            if asset.suffix=='.png':width,height=struct.unpack('>II',asset.read_bytes()[16:24])
            else:
                svg=asset.read_text();width=int(re.search(r'width="(\d+)"',svg)[1]);height=int(re.search(r'height="(\d+)"',svg)[1])
            tag=tag.replace('>',f' width="{width}" height="{height}">',1)
            return '<a href="'+html.escape(src)+'" target="_blank" rel="noopener" title="Open full-size screen">'+tag+'</a>'
        body=re.sub(r'<img\b[^>]*>',sized_image,body)

        body=re.sub(r'(<table\b.*?</table>)',r'<div class="table-scroll" role="region" aria-label="Reference table" tabindex="0">\1</div>',body,flags=re.S)
        # Intro comes before controls and chapters, preserving a single reading flow.
        video='<div class="guide-video-block"><video class="guide-video" controls playsinline preload="none" poster="assets/fg4-youtube.jpg" aria-label="Your first groove with RHYTHMER OS"><source src="'+VIDEO+'" type="video/mp4"><track kind="subtitles" srclang="en" label="English" src="assets/fg4-youtube.vtt"><a href="'+VIDEO+'">Watch the First Groove video</a></video><p class="video-caption">Watch the musical example, then follow the illustrated steps for the current controls.</p></div>'
        if page=='index.html':
            front='<section aria-labelledby="first-groove"><h2 id="first-groove">Start here: Your first groove</h2><p>Build a four-bar groove with <strong>Rhythmer Kit, FMini-1 and FM-106</strong>, then try Acid Engine and Break Engine. Follow the illustrated guide alongside your MPC Sample.</p>'+video+'<div class="guide-links"><a href="quickstart.html">FOLLOW THE FIRST GROOVE GUIDE ↗</a><a href="#essential-controls">ESSENTIAL CONTROLS ↓</a><a href="#system-structure">SYSTEM STRUCTURE ↓</a></div></section>'
            body=body.replace('<h2 id="essential-controls">',front+'<h2 id="essential-controls">',1)
            converter.headings.insert(1,(2,'Start here: Your first groove','first-groove'))
            aliases={'start':'3-start-a-project-and-add-an-instrument','acid-generator':'11-use-acid-gen','break-manipulator':'12-load-a-break-and-return-to-its-controls','break-performance':'brk-perf-what-each-page-does','credits':'credits-and-testing-status','1-read-these-controls-first':'essential-controls','2-choose-the-screen-for-the-task':'system-structure'}
            for alias,target in aliases.items():body=re.sub(r'(<h[23] id="'+re.escape(target)+r'">)',r'<span id="'+alias+r'"></span>\1',body,count=1)
        else:
            body=body.replace('<h2 id="before-you-start">',video+'<div class="guide-links"><a href="index.html#essential-controls">BUTTON COMBINATIONS ↗</a><a href="index.html#system-structure">SYSTEM STRUCTURE ↗</a><a href="index.html">FULL MANUAL ↗</a></div><h2 id="before-you-start">',1)
        title=text.splitlines()[0].lstrip('# ')
        toc=''.join('<a href="#'+html.escape(anchor)+'">'+html.escape(re.sub(r'^([3-9]|1[0-6])\. ', '',label) if page=='index.html' else label)+'</a>' for level,label,anchor in converter.headings if level==2)
        # Numeric chapter anchors stay compatible; visible numbering starts at chapter 1 after the front matter.
        if page=='index.html':
            body=re.sub(r'(<h2 id="[^"]+">)(\d+)\. ',lambda m:m[1]+str(int(m[2])-2)+'. ',body)
        trail='<div class="manual-trail"><a href="https://jazzyrhythmer.github.io/mpc-sample/">RHYTHMER OS</a><span>/</span><a href="index.html">MANUAL</a>'+('<span>/</span><span>YOUR FIRST GROOVE</span>' if page!='index.html' else '')+'</div>'
        footer='<footer class="manual-footer"><p>RHYTHMER OS — by jazzy rhythmer. Based on Melodee by Kerem Kiliç (Ellic Studio) and the credited engine projects. Screen examples use the production UI renderer; displayed project values are examples.</p><a href="https://jazzyrhythmer.github.io/mpc-sample/installer/">Installation</a><a href="https://github.com/jazzyrhythmer/mpc-sample-rhythmer-os">Source &amp; credits</a><a href="LICENSE.txt">Licence</a></footer>'
        js='''document.getElementById('contents').open=matchMedia('(min-width:901px)').matches;const links=[...document.querySelectorAll('.toc a')];if('IntersectionObserver' in window){const observer=new IntersectionObserver(es=>{for(const e of es)if(e.isIntersecting){for(const a of links){if(a.hash==='#'+e.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}}},{rootMargin:'-20% 0px -65% 0px'});document.querySelectorAll('.doc h2[id]').forEach(h=>observer.observe(h));}document.querySelector('[data-print]').addEventListener('click',()=>window.print());'''
        document='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' — MPC Sample</title><meta name="description" content="The illustrated RHYTHMER OS manual: First Groove, button combinations, system structure and step-by-step chapters."><link rel="stylesheet" href="guide-020.css"><link rel="stylesheet" href="platform-navigation.css"><script src="platform-navigation.js" defer></script></head><body><a class="skip" href="#main">Skip to manual</a>'+header+'<main id="main" class="manual-shell">'+trail+'<div class="manual-layout"><aside><div class="manual-tools"><button type="button" data-print>PRINT / SAVE PDF</button></div><details class="toc" id="contents"><summary>ON THIS PAGE</summary>'+toc+'</details></aside><article class="doc">'+body+'</article></div></main>'+footer+'<script>'+js+'</script></body></html>'
        (output/page).write_text(document)
        manifest[page]={'version':'0.2.0','source':name,'source_sha256':hashlib.sha256((ROOT/'docs'/name).read_bytes()).hexdigest(),'sections':len(converter.headings),'publication_performed_by_generator':False}
    for page,target in ALIASES.items():
        # No translated content remains; keep incoming bookmarks useful.
        (output/page).write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url='+target+'"><link rel="canonical" href="https://jazzyrhythmer.github.io/mpc-sample/manual/'+target+'"><title>RHYTHMER OS manual</title></head><body><p><a href="'+target+'">Open the RHYTHMER OS manual</a></p><script>location.replace('+json.dumps(target)+');</script></body></html>')
    (output/'guide-020-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Rendered two illustrated English guides and five legacy-link redirects; publication not performed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--offline',action='store_true');args=p.parse_args();render(args.output_dir,args.offline)
