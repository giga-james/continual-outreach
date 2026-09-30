#!/usr/bin/env python3
"""Render the fictional README walkthrough. Optional dependency: Pillow.

Run from any directory: python3 scripts/demo/render_walkthrough.py
Set DEMO_FONT and DEMO_BOLD to override the default macOS/DejaVu fonts.
This draws mock interfaces only; it never opens a browser or contacts anyone.
"""
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H = 1100, 700
BG = '#0f172a'
FONT = os.environ.get('DEMO_FONT', '/System/Library/Fonts/Supplemental/Arial.ttf')
BOLD = os.environ.get('DEMO_BOLD', '/System/Library/Fonts/Supplemental/Arial Bold.ttf')
if not Path(FONT).exists(): FONT = 'DejaVuSans.ttf'
if not Path(BOLD).exists(): BOLD = 'DejaVuSans-Bold.ttf'

def font(size=16, bold=False): return ImageFont.truetype(BOLD if bold else FONT, size)

def render(step, cursor=None, click=False):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    def text(x,y,t,size=16,color='#cbd5e1',bold=False):
        d.text((x,y),t,font=font(size,bold),fill=color)
    def box(x,y,w,h,fill='#1e293b',outline=None,r=12):
        d.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=outline)
    def lines(x,y,items,size=16,color='#cbd5e1',gap=25):
        for i,t in enumerate(items): text(x,y+i*gap,t,size,color)
    def button(x,y,w,label,fill='#0a66c2'):
        w = max(w, int(d.textlength(label, font=font(14, True))) + 32)
        box(x,y,w,36,fill,r=18); text(x+16,y+9,label,14,'#ffffff',True)
    def bubble(y,label,items,user=False):
        box(38,y,314,42+len(items)*24,'#30305a' if user else '#1e293b')
        text(52,y+12,label,12,'#c4b5fd' if user else '#93c5fd',True)
        lines(52,y+36,items,14,gap=24)
    names=['Interview the founder','Set qualification + messaging','Research the web','Read the evidence','Verify the LinkedIn profile','Prepare the approved note','Verify + export the result','Learn before the next batch']
    text(28,23,'CONTINUAL OUTREACH',15,'#a5b4fc',True)
    text(28,52,names[step],27,'#f8fafc',True)
    box(845,22,225,28,'#302c46',r=14); text(860,29,'MOCK DEMO · FICTIONAL DATA',11,'#e9d5ff',True)
    text(28,97,'Your agent',14,'#94a3b8',True)
    box(378,99,695,537,'#ffffff')
    box(378,99,695,45,'#e2e8f0')
    for i,c in enumerate(['#f87171','#fbbf24','#4ade80']): d.ellipse((392+i*17,115,401+i*17,124),fill=c)
    url=['Campaign workspace','Campaign workspace','Web research · illustrative browser','harborlight.example/blog/knowledge-base · fictional','linkedin.com/in/maya-chen-demo · mock','LinkedIn · mock connection dialog','Campaign tracker · mock export','Campaign audit · illustrative outcomes'][step]
    text(459,114,url,13,'#475569')
    if step==0:
        bubble(130,'AGENT',['What are you building, and','whose work should improve?'])
        bubble(246,'YOU',['A tool that helps support teams','turn recurring issues into','clear internal documentation.'],True)
        bubble(386,'AGENT',['Who owns that work today?'])
        bubble(478,'YOU',['Support ops leads who maintain','the knowledge base themselves.'],True)
        text(415,176,'Campaign interview',24,'#0f172a',True)
        for y,title,detail in [(241,'Product','Support documentation assistant'),(328,'Champion','Hands-on support operations lead'),(415,'Evidence','Owns the process, not just the title')]:
            box(413,y,622,70,'#f1f5f9'); text(431,y+12,title,14,'#64748b',True); text(431,y+37,detail,18,'#0f172a')
    elif step==1:
        bubble(130,'AGENT',['I’ll look for people who describe','maintaining a knowledge base.','Exclude vendors selling this.'])
        bubble(270,'YOU',['Yes. Use that profile and note.','Send within our agreed limits.'],True)
        bubble(387,'AGENT',['Saved. I’ll open my browser','and verify each person’s work.'])
        text(415,176,'Ready to research',24,'#0f172a',True)
        lines(421,239,['ICP and exclusions saved','Message and call to action agreed','Sending scope and limits recorded','Tracker destination checked'],18,'#334155',48)
        button(418,464,205,'Start browser research')
    elif step==2:
        bubble(130,'AGENT',['Computer use is ready.','Searching for public evidence','of knowledge-base ownership.'])
        bubble(270,'AGENT',['Found a company article.','I’ll read it before qualifying','the author.'])
        text(415,177,'Find hands-on practitioners',24,'#0f172a',True)
        box(414,228,622,45,'#f1f5f9'); text(431,243,'support operations knowledge base workflow',17,'#334155')
        text(419,316,'How we rebuilt our support knowledge base',21,'#0a66c2',True)
        lines(419,355,['Harborlight Labs · Company blog · Fictional example','By Maya Chen, Support Operations Lead','A practical account of maintaining articles and reviewing','recurring support issues with the frontline team.'],16,'#475569',29)
        button(419,511,163,'Read source article')
    elif step==3:
        bubble(130,'AGENT',['Reading the original article,','not just the search snippet.','Who actually owns the work?'])
        bubble(270,'AGENT',['Maya explains her weekly','review routine. Strong signal:','she runs the process herself.'])
        text(418,174,'HARBORLIGHT LABS / FIELD NOTES',13,'#64748b',True)
        lines(418,212,['How we rebuilt our','support knowledge base'],28,'#0f172a',36)
        text(418,300,'Maya Chen · Support Operations Lead',16,'#0a66c2',True)
        box(414,349,622,116,'#eef2ff')
        lines(431,367,['“Every Friday, I review recurring support tickets,','update the articles, and ask the team to flag','anything that still needs a clearer answer.”'],18,'#3730a3',29)
        text(418,480,'Evidence saved: named owner + repeated manual work',15,'#475569')
        button(419,535,179,'View author on LinkedIn')
    elif step in (4,5):
        bubble(130,'AGENT',['Maya describes owning the','weekly article review process.','Evidence matches the ICP.'])
        bubble(270,'AGENT',['Profile verified. No existing','connection or pending request.','Checking the approved note.'])
        box(398,158,655,102,'#dae6ef'); d.ellipse((423,212,505,294),fill='#a5b4fc'); text(443,237,'MC',25,'#312e81',True)
        text(420,313,'Maya Chen',26,'#0f172a',True)
        lines(420,355,['Support Operations Lead at Harborlight Labs','Owns support knowledge and article review workflows'],16,'#475569',27)
        button(420,426,118,'Connect')
        text(420,489,'Featured work',18,'#0f172a',True)
        text(420,522,'How we rebuilt our support knowledge base',18,'#0a66c2')
        if step==5:
            box(407,222,636,349,'#ffffff','#cbd5e1')
            text(434,248,'Add a note to your invitation',23,'#0f172a',True)
            box(433,297,582,191,'#f8fafc','#cbd5e1')
            lines(449,313,['Hi Maya, I came across your article on rebuilding','Harborlight’s support knowledge base. I’m Alex,','building tools for support teams. Open to a 15-minute','chat about your process? Not selling anything—','just hoping to learn about your day to day.'],17,'#334155',30)
            button(912,510,102,'Send')
    elif step==6:
        bubble(130,'AGENT',['Invitation verified as pending.','Recorded the exact note and','confirmed the tracker update.'])
        bubble(270,'AGENT',['One verified send.','Next: observe responses before','adjusting candidate selection.'])
        text(415,177,'Outreach tracker',24,'#0f172a',True)
        box(415,234,620,47,'#dcfce7'); text(432,250,'Sent state verified · export synchronized',17,'#166534')
        for x,t in [(424,'Prospect'),(647,'Qualification'),(873,'Status')]: text(x,319,t,15,'#64748b',True)
        d.line((417,350,1033,350),fill='#e2e8f0',width=2)
        text(424,372,'Maya Chen',17,'#0f172a',True); text(647,372,'Verified owner',16,'#334155'); text(873,372,'Pending',16,'#0a66c2')
        lines(425,449,['Source and message saved with a stable prospect ID.','Existing connections and pending requests are skipped.'],16,'#475569',30)
    else:
        bubble(130,'AGENT',['After the observation window,','compare useful replies across','equally aged profile groups.'])
        bubble(270,'AGENT',['Favor stronger-fit profiles,','keep an exploration share,','and prepare the next batch.'])
        text(415,177,'Later: audit and tune',24,'#0f172a',True)
        text(420,224,'Illustrative mature cohort · not real campaign results',14,'#64748b')
        for y,label,v in [(281,'Hands-on process owners',.65),(352,'Broad leadership titles',.25)]:
            text(420,y,label,17,'#334155',True); box(420,y+29,480,14,'#e2e8f0',r=7); box(420,y+29,int(480*v),14,'#818cf8',r=7)
        text(420,429,'Useful replies per observed cohort',14,'#64748b')
        box(415,478,620,99,'#eef2ff'); lines(434,496,['Next batch: evidence-guided selection + exploration','Respect sending holds and the agreed cadence.'],17,'#3730a3',32)
    for i in range(8): box(28+i*131,661,121,5,'#818cf8' if i<=step else '#334155',r=2)
    text(29,677,'Illustrative UI only. All people, companies and outcomes are fictional. No live outreach.',11,'#94a3b8')
    if cursor:
        x,y=cursor
        if click: d.ellipse((x-17,y-17,x+17,y+17),outline='#a78bfa',width=3)
        d.polygon([(x,y),(x+3,y+25),(x+10,y+18),(x+17,y+30),(x+22,y+27),(x+15,y+15),(x+25,y+13)],fill='#0f172a',outline='#ffffff')
    return im

frames=[]; durations=[]
for step in range(8):
    target={1:(535,482),2:(500,528),3:(500,552),4:(478,443),5:(965,528)}.get(step)
    frames.append(render(step)); durations.append(4800 if step in (0,3,5,7) else 3600)
    if target:
        for i in range(1,9):
            ratio=i/8
            frames.append(render(step,(int(1035+(target[0]-1035)*ratio),int(607+(target[1]-607)*ratio))))
            durations.append(65)
        frames.append(render(step,target,True)); durations.append(550)
frames[0].save(ROOT/'assets/walkthrough.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True)
# Contact sheet makes all narrative states easy to review without playing the GIF.
contact=Image.new('RGB',(1100,4*350),'#0f172a')
for i in range(8): contact.paste(render(i).resize((550,350)),((i%2)*550,(i//2)*350))
contact.save(Path(tempfile.gettempdir())/'continual-outreach-demo-review.png')
print(ROOT/'assets/walkthrough.gif')
print(f'{len(frames)} frames; {sum(durations)/1000:.1f}s; {(ROOT/"assets/walkthrough.gif").stat().st_size:,} bytes')
