#!/usr/bin/env python3
"""Extract only the official cover wordmark's vector geometry; requires pypdf.

Input: official MPC Sample User Guide v1.0. Output: a white-on-black SVG.
The device mark retains inMusic's rights; it is not original RHYTHMER artwork.
"""
from pathlib import Path
import sys
from pypdf import PdfReader
from pypdf.generic import ContentStream


def extract(source, target):
    reader=PdfReader(source)
    ctm=(1,0,0,1,0,0);color=(0,0,0);stroke=(0,0,0);width=1;stack=[];path=[];points=[];groups=[];current=(0,0)
    def xy(x,y):
        a,b,c,d,e,f=ctm
        return a*float(x)+c*float(y)+e,b*float(x)+d*float(y)+f
    def point(p):return f'{p[0]:.4f},{-p[1]:.4f}'
    for args,op in ContentStream(reader.pages[0].get_contents(),reader).operations:
        if op==b'q':stack.append((ctm,color,stroke,width))
        elif op==b'Q':ctm,color,stroke,width=stack.pop()
        elif op==b'cm':
            a,b,c,d,e,f=ctm;A,B,C,D,E,F=map(float,args)
            ctm=(a*A+c*B,b*A+d*B,a*C+c*D,b*C+d*D,a*E+c*F+e,b*E+d*F+f)
        elif op==b'rg':color=tuple(map(float,args))
        elif op==b'g':color=(float(args[0]),)*3
        elif op==b'RG':stroke=tuple(map(float,args))
        elif op==b'G':stroke=(float(args[0]),)*3
        elif op==b'w':width=float(args[0])
        elif op in (b'm',b'l'):
            current=xy(*args);points.append(current);path.append(('M' if op==b'm' else 'L')+point(current))
        elif op==b'c':
            ps=[xy(*args[i:i+2]) for i in (0,2,4)];points+=ps
            path.append('C'+' '.join(map(point,ps)));current=ps[-1]
        elif op in (b'y',b'v'):
            a=xy(*args[:2]);b=xy(*args[2:]);ps=[a,b,b] if op==b'y' else [current,a,b]
            points+=ps;path.append('C'+' '.join(map(point,ps)));current=b
        elif op==b'h':path.append('Z')
        elif op==b're':
            x,y,w,h=map(float,args);ps=[xy(x,y),xy(x+w,y),xy(x+w,y+h),xy(x,y+h)]
            points+=ps;path.append('M'+point(ps[0])+' L'+' L'.join(map(point,ps[1:]))+'Z')
        elif op in (b'f',b'f*',b'B',b'B*',b'b',b'b*',b'S',b's',b'n'):
            if points and op!=b'n':
                box=(min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points))
                if box[0]>190 and box[2]<560 and box[1]>700 and box[3]<750:
                    def ink(c):return '#ffffff' if c[0]>.5 and c[1]<.25 and c[2]<.4 else '#000000'
                    fill='none' if op in (b'S',b's') else ink(color)
                    edge=ink(stroke) if op in (b'S',b's',b'B',b'B*',b'b',b'b*') else 'none'
                    commands=[]
                    for command in path:
                        if fill!='none' and command.startswith('M') and commands and commands[-1]!='Z':commands.append('Z')
                        commands.append(command)
                    if (fill!='none' or op==b's') and commands[-1]!='Z':commands.append('Z')
                    d=' '.join(commands)
                    groups.append((box,d,'evenodd' if b'*' in op else 'nonzero',fill,edge,width))
            path=[];points=[]
    assert groups and len(groups)<60,'Unexpected guide layout; inspect the official cover'
    x0=min(g[0][0] for g in groups);y0=min(g[0][1] for g in groups)
    x1=max(g[0][2] for g in groups);y1=max(g[0][3] for g in groups)
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="%g %g %g %g"><title>MPC Sample</title>'%(x0,-y1,x1-x0,y1-y0)
    svg+=''.join('<path fill="'+c+'" stroke="'+s+'" stroke-width="'+str(w)+'" fill-rule="'+r+'" d="'+d+'"/>' for b,d,r,c,s,w in groups)
    Path(target).write_text(svg+'</svg>\n')
    print(len(groups),'official vector groups extracted')


if __name__=='__main__':extract(sys.argv[1],sys.argv[2])
