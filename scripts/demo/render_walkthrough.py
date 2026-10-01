#!/usr/bin/env python3
"""Draw a fictional Codex-style split-pane demo (no browser or outreach calls).

Run: python3 scripts/demo/render_walkthrough.py. Requires Pillow.
DEMO_FONT / DEMO_BOLD optionally override the macOS/DejaVu fonts.
Encode the pause-capable video from the repository root:
  ffmpeg -y -i assets/walkthrough.gif -movflags +faststart -pix_fmt yuv420p \
    -vf "fps=20" assets/walkthrough.mp4
"""
import json
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H = 1440, 900
FONT = os.environ.get('DEMO_FONT', '/System/Library/Fonts/Supplemental/Arial.ttf')
BOLD = os.environ.get('DEMO_BOLD', '/System/Library/Fonts/Supplemental/Arial Bold.ttf')
if not Path(FONT).exists(): FONT = 'DejaVuSans.ttf'
if not Path(BOLD).exists(): BOLD = 'DejaVuSans-Bold.ttf'
INK, MUTED, GREEN = '#242724', '#717671', '#2f7052'
SCENES = [
    '01  Tell the agent who you want to learn from',
    '02  Lock the ICP, message and sending scope',
    '03  Research the web for hands-on evidence',
    '04  Read the source and qualify the person',
    '05  Verify the person on LinkedIn',
    '06  Personalize the approved invitation',
    '07  Verify the send and update the tracker',
    '08  Learn from replies before the next batch',
]

def font(size=18, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

def render(step, cursor=None, click=False):
    im = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(im)
    def text(x,y,t,size=18,color=INK,bold=False):
        d.text((x,y),t,font=font(size,bold),fill=color)
    def box(x,y,w,h,fill='#f5f6f4',outline=None,r=12):
        d.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=outline)
    def lines(x,y,items,size=19,color=INK,gap=29,bold=False):
        for i,t in enumerate(items): text(x,y+i*gap,t,size,color,bold)
    def button(x,y,w,label,fill=GREEN):
        box(x,y,w,40,fill,r=20); text(x+18,y+10,label,16,'#ffffff',True)
    def chat(y,label,items,user=False):
        x=191 if user else 176
        if user: box(x-12,y-10,444,len(items)*28+48,'#f0f1ee',r=16)
        text(x,y,label,14,MUTED,True)
        lines(x,y+29,items,19,gap=28)
    def browsertitle(title,subtitle):
        text(714,185,title,27,INK,True)
        text(714,229,subtitle,16,MUTED)
    def card(y,title,details):
        box(714,y,650,58+len(details)*29,'#f7f8f6','#e4e7e1')
        text(734,y+17,title,16,GREEN,True)
        lines(734,y+49,details,20)

    # Native-style window chrome, restrained sidebar, task and embedded browser.
    d.rectangle((0,0,W,52),fill='#f7f7f5')
    for i,c in enumerate(['#ee7369','#e7bb56','#72be81']):
        d.ellipse((20+i*21,21,31+i*21,32),fill=c)
    text(113,18,'Codex',16,INK,True)
    text(530,18,'continual-outreach',15,MUTED)
    box(1172,13,248,28,'#e9eee8',r=14)
    text(1186,20,'ILLUSTRATIVE / FICTIONAL DATA',11,GREEN,True)
    d.rectangle((0,52,150,H),fill='#f4f5f2')
    text(18,82,'+  New task',16,INK,True)
    text(18,142,'PROJECTS',11,MUTED,True)
    box(10,170,130,56,'#e5e8e1',r=8)
    lines(19,181,['continual-', 'outreach'],14,INK,20,True)
    text(18,263,'TASKS',11,MUTED,True)
    lines(18,299,['Find support','ops leads'],14,INK,22)
    text(18,811,'Local workspace',11,MUTED)
    text(18,836,'Mock campaign',11,MUTED)
    d.line((666,52,666,844),fill='#dfe2dc',width=1)
    text(176,77,'Find support ops leads',22,INK,True)
    text(176,111,'Interview → evidence → outreach → learn',14,MUTED)
    d.line((151,144,666,144),fill='#e9ebe6')
    text(700,75,'Browser',16,INK,True)
    text(1290,75,'Split view',13,MUTED)
    box(696,108,720,42,'#f2f3f0',r=8)
    url=[
        'Campaign brief · mock workspace', 'Approved campaign · mock workspace',
        'Search · illustrative results', 'harborlight.example / blog / weekly-ticket-review',
        'LinkedIn · fictional profile', 'LinkedIn · fictional invitation',
        'Google Sheets · fictional tracker', 'Campaign audit · fictional outcomes'
    ][step]
    text(711,121,'‹   ›    '+url,15,MUTED)
    box(175,752,467,67,'#fafbf9','#e1e4dd',r=18)
    text(193,770,'Ask a follow-up…',17,'#9a9e97')
    text(193,797,'Local agent  ·  computer use',11,MUTED)
    d.ellipse((601,771,626,796),fill=INK); text(608,772,'↑',18,'#ffffff')
    if step==0:
        chat(178,'YOU',['Find 30 support ops leads for my','help-docs tool. Research their work,','draft personal LinkedIn notes asking','for a 15-minute chat, and track replies','so the next batch gets better.'],True)
        chat(380,'AGENT',['What shows they feel this pain—and','which companies should I focus on?'])
        chat(490,'YOU',['Support ops leads at B2B SaaS firms','who personally review recurring tickets','and update help docs every week.'],True)
        chat(643,'AGENT',['Got it. What should I exclude, and','where should I track the results?'])
        browsertitle('Start with the customer’s goal','Alex · founder of a support knowledge-base tool')
        card(280,'FIND 30 QUALIFIED PEOPLE',['Support operations leads at B2B SaaS firms'])
        card(414,'LOOK FOR REPEATED MANUAL WORK',['Review recurring support tickets','Update help articles every week'])
        card(575,'SUCCESS = A USEFUL CONVERSATION',['Learn how they maintain support knowledge','and where the process takes time'])
    elif step==1:
        chat(178,'YOU',['Exclude vendors and generic leaders.','Ask for a 15-minute learning chat.','Track everything in Google Sheets.'],True)
        chat(332,'AGENT',['I’ll verify hands-on work, personalize','each note, and skip existing or','pending connections. Ready to send?'])
        chat(482,'YOU',['Yes—use the agreed note and limits.'],True)
        chat(586,'AGENT',['Scope saved. Starting browser research.'])
        browsertitle('A clear brief before the browser opens','ICP + message + destination + sending scope')
        card(277,'IDEAL INTERVIEW',['B2B SaaS · hands-on support ops owner','Public evidence of a weekly review routine'])
        card(437,'EXCLUDE',['Vendors selling similar tools','Leadership titles without ownership evidence'])
        card(597,'OUTREACH PLAN',['15-minute learning chat · approved note','Google Sheets tracking · agreed send budget'])
    elif step==2:
        chat(178,'AGENT',['Searching for people describing their','actual ticket and documentation work.'])
        chat(312,'AGENT',['A title is not enough. I’m looking for','a named owner and a repeatable routine.'])
        chat(458,'AGENT',['This company article looks promising.','Opening the original source.'])
        browsertitle('Research the work, not just the title','Illustrative search results')
        box(714,280,650,57,'#ffffff','#cfd5cb',r=25)
        text(734,299,'"support operations" "weekly" "knowledge base"',19)
        text(720,379,'Harborlight Labs  /  Company blog',15,MUTED)
        lines(720,414,['How we review support tickets','and keep our help center current'],25,'#2463a5',33,True)
        lines(720,503,['By Maya Chen · Support Operations Lead','Our weekly routine for turning recurring questions','into better documentation.'],19,MUTED,30)
        button(720,626,185,'Read source article')
    elif step==3:
        chat(178,'AGENT',['Maya names the exact work she does:','weekly ticket reviews and article edits.'])
        chat(313,'AGENT',['Harborlight builds B2B software.','She meets the company and role criteria.'])
        chat(456,'AGENT',['Saved the source and evidence.','Next: verify her LinkedIn identity.'])
        browsertitle('Harborlight Labs / Field notes','Fictional company article')
        lines(714,284,['How we review support tickets','and keep our help center current'],27,INK,36,True)
        text(714,380,'Maya Chen · Support Operations Lead',18,'#2463a5',True)
        box(714,432,650,158,'#eaf2e9',r=12)
        lines(737,456,['“Every Friday, I review recurring support tickets,','update the help articles, and ask our frontline','team what still needs a clearer answer.”'],21,'#305b3c',34)
        text(718,614,'MATCH: named owner + weekly manual work',16,GREEN,True)
        button(716,683,216,'Find LinkedIn profile')
    elif step in (4,5):
        chat(178,'AGENT',['Verified: same name, company and role','as the author of the source article.'])
        chat(312,'AGENT',['No existing connection or pending','invitation. This prospect is eligible.'])
        chat(457,'AGENT',(['Personalizing the approved note around','her weekly ticket-review process.'] if step==5 else ['The note will reference her article,','not a generic compliment.']))
        box(694,170,721,128,'#d9e4dd',r=8)
        d.ellipse((719,253,809,343),fill='#a9bcab',outline='#ffffff',width=4)
        text(738,282,'MC',29,'#35533b',True)
        text(716,367,'Maya Chen',30,INK,True)
        lines(716,417,['Support Operations Lead at Harborlight Labs','B2B SaaS · Support knowledge and enablement'],19,MUTED,31)
        button(716,502,132,'Connect',fill='#0a66c2')
        text(716,589,'Featured work',20,INK,True)
        lines(716,628,['How we review support tickets','and keep our help center current'],22,'#2463a5',31)
        if step==5:
            box(698,226,711,488,'#ffffff','#cbd3c8',r=15)
            text(724,251,'Add a note to your invitation',25,INK,True)
            box(721,312,664,274,'#fafbf9','#d6ddd0')
            lines(741,336,['Hi Maya, I read your article on weekly ticket','reviews and help-doc updates. I’m Alex, building','a support knowledge-base tool. Open to a','15-minute chat about how you developed that','process? Not selling anything—just looking','to learn about your day to day.'],21,INK,36)
            text(725,615,'Personalized from verified source evidence',16,MUTED)
            button(1268,652,112,'Send',fill='#0a66c2')
    elif step==6:
        chat(178,'AGENT',['The invitation now shows Pending.','Saved the exact note and source URL.'])
        chat(312,'AGENT',['Google Sheets row updated and verified.','One send recorded against the budget.'])
        chat(457,'AGENT',['I’ll observe replies before changing','the next batch of prospects.'])
        browsertitle('Outreach tracker','Google Sheets · illustrative campaign export')
        box(714,276,650,47,'#eaf2e9')
        text(733,291,'Verified send · tracker synchronized',18,GREEN,True)
        for x,label in [(727,'Person'),(920,'Evidence'),(1217,'Status')]: text(x,369,label,16,MUTED,True)
        d.line((714,406,1364,406),fill='#dce2d7')
        text(727,431,'Maya Chen',20,INK,True)
        lines(920,429,['Weekly ticket review','+ help-doc updates'],18,INK,29)
        box(1202,423,140,39,'#e9f0f8',r=19); text(1226,434,'Pending',17,'#2463a5')
        card(557,'SAVED FOR THE NEXT AUDIT',['Evidence source · personalized note · sent time','Stable prospect ID · reply and interview outcomes'])
    else:
        chat(178,'AGENT',['Later, after the observation window:','compare useful replies from equally','aged groups—not just acceptances.'])
        chat(339,'AGENT',['Hands-on owners replied more often.','The next batch favors these profiles.'])
        chat(480,'AGENT',['Keep 20% exploration to test adjacent','roles. Resume only within the budget','and after any sending hold expires.'])
        browsertitle('Learn, then select the next batch','Fictional results · equal observation windows')
        for y,label,count,width in [(290,'Weekly review + help-doc owners','4 / 10 useful replies',470),(426,'Help-doc owners; no weekly evidence','1 / 10 useful replies',118)]:
            text(718,y,label,21,INK,True)
            box(718,y+41,590,16,'#e8ece4',r=8)
            box(718,y+41,width,16,'#7eaa83',r=8)
            text(718,y+72,count,17,MUTED)
        card(593,'NEXT BATCH',['80% evidence-guided selection','20% exploration of adjacent profiles'])
    # Permanent chapter strip makes the narrative understandable mid-playback.
    d.rectangle((150,842,W,H),fill='#f6f7f4')
    text(177,858,SCENES[step],20,INK,True)
    text(1131,868,'Mock UI, people and results',13,MUTED)
    for i in range(8):
        d.rectangle((176+i*156,836,321+i*156,840),fill=GREEN if i<=step else '#e4e8e0')
    if cursor:
        x,y=cursor
        if click: d.ellipse((x-19,y-19,x+19,y+19),outline='#61956d',width=3)
        d.polygon([(x,y),(x+3,y+25),(x+10,y+18),(x+17,y+30),(x+22,y+27),(x+15,y+15),(x+25,y+13)],fill=INK,outline='#ffffff')
    return im


def main():
    frames, durations, chapters = [], [], []
    for step,title in enumerate(SCENES):
        start = sum(durations)
        target={2:(814,646),3:(819,701),4:(780,522),5:(1320,670)}.get(step)
        frames.append(render(step)); durations.append(6500 if step in (0,1,5,7) else 5000)
        if target:
            for i in range(1,9):
                ratio=i/8
                frames.append(render(step,(int(1375+(target[0]-1375)*ratio),int(788+(target[1]-788)*ratio))))
                durations.append(70)
            frames.append(render(step,target,True)); durations.append(550)
        chapters.append({'title':title,'start_seconds':start/1000,'duration_seconds':(sum(durations)-start)/1000})
    assets=ROOT/'assets'
    frames[0].save(assets/'walkthrough.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True)
    poster=render(0)
    pd=ImageDraw.Draw(poster)
    pd.rounded_rectangle((1016,744,1364,804),radius=30,fill=GREEN)
    pd.polygon([(1039,760),(1039,787),(1059,774)],fill='#ffffff')
    pd.text((1072,762),'Watch walkthrough · 50 sec',font=font(19,True),fill='#ffffff')
    poster.save(assets/'walkthrough-poster.png')
    (assets/'walkthrough-scenes.json').write_text(json.dumps(chapters,indent=2)+'\n')
    contact=Image.new('RGB',(1440,4*450),'#ffffff')
    for i in range(8): contact.paste(render(i).resize((720,450)),((i%2)*720,(i//2)*450))
    path=Path(tempfile.gettempdir())/'continual-outreach-demo-review.png'
    contact.save(path)
    print(assets/'walkthrough.gif')
    print(path)
    print(f'{len(frames)} frames; {sum(durations)/1000:.2f}s; {(assets/"walkthrough.gif").stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
