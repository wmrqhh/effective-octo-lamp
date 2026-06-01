from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, os, subprocess, wave, struct
import imageio_ffmpeg

W,H=1280,720
OUT_DIR='generated'
os.makedirs(OUT_DIR, exist_ok=True)
VIDEO=os.path.join(OUT_DIR,'shenshu_suxing_fantasy_short.mp4')
AUDIO=os.path.join(OUT_DIR,'shenshu_suxing_score.wav')
POSTER=os.path.join(OUT_DIR,'poster.png')
FONT='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
FONT_REG='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
if not os.path.exists(FONT): FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not os.path.exists(FONT_REG): FONT_REG=FONT
font_title=ImageFont.truetype(FONT, 58)
font_mid=ImageFont.truetype(FONT, 40)
font_small=ImageFont.truetype(FONT_REG, 30)
random.seed(11)

def radial(c1,c2,c3,center):
    import numpy as np
    y,x=np.mgrid[0:H,0:W]
    cx,cy=center[0]*W,center[1]*H
    r=np.sqrt((x-cx)**2+(y-cy)**2)/900
    r=np.clip(r,0,1)
    arr=(np.array(c1)*(1-r[...,None])+np.array(c2)*r[...,None])
    glow=np.exp(-((x-cx)**2+(y-cy)**2)/(2*(150**2)))
    arr=np.clip(arr+np.array(c3)*glow[...,None],0,255).astype('uint8')
    return Image.fromarray(arr,'RGB')

def add_text(img, text, y, font=font_mid):
    d=ImageDraw.Draw(img)
    lines=text.split('\n')
    heights=[d.textbbox((0,0),l,font=font,stroke_width=3)[3] for l in lines]
    yy=y-(sum(heights)+10*(len(lines)-1))/2
    for line,h in zip(lines,heights):
        box=d.textbbox((0,0),line,font=font,stroke_width=3)
        x=(W-(box[2]-box[0]))/2
        d.text((x,yy),line,font=font,fill=(255,244,220),stroke_width=3,stroke_fill=(28,15,54))
        yy+=h+10

def bars(img):
    d=ImageDraw.Draw(img,'RGBA')
    d.rectangle([0,0,W,42],fill=(0,0,0,190)); d.rectangle([0,H-42,W,H],fill=(0,0,0,190))
    return img

def scene_tree(path, bright=False, text=''):
    img=radial((39,30,78),(229,194,222),(80,60,130),(0.50,0.58)); d=ImageDraw.Draw(img,'RGBA')
    # top purple canopy
    for i in range(95):
        rr=random.Random(i); x=rr.randint(-90,W+90); y=rr.randint(-80,190); rx=rr.randint(70,220); ry=rr.randint(25,85)
        d.ellipse([x-rx,y-ry,x+rx,y+ry],fill=(55+rr.randint(0,35),34,105+rr.randint(0,55),115))
    # beams
    for bx in [160,375,910]:
        d.polygon([(bx-55,0),(bx+18,0),(bx+375,H),(bx+245,H)],fill=(255,222,235,55 if bright else 30))
    # islands
    for i,(x,y,s) in enumerate([(70,520,1),(1120,565,1.5),(995,430,.8),(345,585,.8)]):
        pts=[(x-130*s,y),(x+130*s,y-35*s),(x+90*s,y+50*s),(x-40*s,y+75*s)]
        d.polygon(pts,fill=(58,50,72,200)); d.line(pts+[pts[0]],fill=(155,115,155,120),width=3)
    # tree
    cx=640
    d.polygon([(cx-70,590),(cx-88,425),(cx-55,275),(cx-25,150),(cx+8,75),(cx+48,160),(cx+78,320),(cx+74,592)],fill=(83,65,70,245))
    for off,col,w in [(-44,(185,150,175,150),9),(-12,(42,32,48,190),8),(28,(220,196,220,130),8),(58,(45,34,53,155),7)]:
        pts=[(cx+off+math.sin(yy*.035+off)*18,yy) for yy in range(115,600,28)]
        d.line(pts,fill=col,width=w)
    for ang in [-2.7,-2.2,-1.05,-.35,.25,.8]:
        d.line([(cx,260+ang*18),(cx+math.cos(ang)*265,260+ang*18+math.sin(ang)*155)],fill=(55,43,53,190),width=13)
    # core glow
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(layer)
    for r in range(220 if bright else 135,8,-12):
        gd.ellipse([cx-r,385-r,cx+r,385+r],fill=(134,210,255,int((90 if bright else 60)*(r/(220 if bright else 135))**2)))
    img.alpha_composite(layer) if img.mode=='RGBA' else None
    img=Image.alpha_composite(img.convert('RGBA'),layer).convert('RGB'); d=ImageDraw.Draw(img,'RGBA')
    d.ellipse([cx-38,347,cx+38,423],fill=(35,45,100,240),outline=(220,240,255,220),width=4)
    d.ellipse([cx-13,372,cx+13,398],fill=(195,235,255,245))
    if bright:
        for r in [120,225,335]: d.ellipse([cx-r,385-r*.55,cx+r,385+r*.55],outline=(248,230,170,75),width=4)
    for i in range(90):
        rr=random.Random(400+i); x=rr.randint(0,W); y=rr.randint(0,H)
        col=(255,225,250,rr.randint(55,155)) if i%5 else (83,165,50,170)
        d.ellipse([x,y,x+rr.randint(2,7),y+rr.randint(2,7)],fill=col)
    if text: add_text(img,text,610)
    bars(img).save(path,quality=95)

def scene_dragon(path):
    img=radial((20,30,72),(12,14,35),(50,95,170),(.58,.47)); d=ImageDraw.Draw(img,'RGBA')
    # speed tunnel
    for i in range(60):
        a=2*math.pi*i/60; rr=random.Random(i)
        x=640+math.cos(a)*rr.randint(160,900); y=360+math.sin(a)*rr.randint(90,500)
        d.line([(640,360),(x,y)],fill=(130,175,255,50),width=rr.randint(1,5))
    # left heroine silhouette
    d.ellipse([125,160,275,315],fill=(12,14,22,220)); d.polygon([(180,280),(305,275),(365,590),(100,592)],fill=(19,20,32,210))
    d.polygon([(105,330),(-25,505),(140,470)],fill=(245,250,255,120)); d.line([(270,235),(400,305),(505,385)],fill=(25,23,22,230),width=16)
    # dragon glow/body
    cx,cy=820,360
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(layer)
    for r in range(230,10,-14): gd.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(70,210,255,int(65*(r/230)**2)))
    img=Image.alpha_composite(img.convert('RGBA'),layer).convert('RGB'); d=ImageDraw.Draw(img,'RGBA')
    d.polygon([(cx-55,cy+15),(cx-255,cy-105),(cx-150,cy+88)],fill=(105,157,178,155),outline=(205,245,255,220))
    d.polygon([(cx+45,cy+15),(cx+275,cy-125),(cx+155,cy+100)],fill=(95,145,170,155),outline=(205,245,255,220))
    d.ellipse([cx-60,cy-44,cx+60,cy+45],fill=(155,205,220,225),outline=(225,255,255,220),width=4)
    d.polygon([(cx+50,cy-10),(cx+175,cy+25),(cx+55,cy+35)],fill=(128,185,205,215))
    d.polygon([(cx-16,cy-55),(cx+2,cy-112),(cx+18,cy-55)],fill=(170,235,245,210))
    d.ellipse([cx-20,cy-11,cx-3,cy+7],fill=(0,255,245,245)); d.ellipse([cx+3,cy-11,cx+20,cy+7],fill=(0,255,245,245))
    d.arc([cx-200,cy-135,cx+200,cy+135],0,360,fill=(210,245,255,125),width=5)
    add_text(img,'守门的晶龙，\n听见了核心的心跳。',610)
    bars(img.filter(ImageFilter.GaussianBlur(.35))).save(path,quality=95)

def scene_guardians(path, title=False):
    img=radial((220,175,188),(86,65,115),(145,75,210),(.35,.28)); d=ImageDraw.Draw(img,'RGBA')
    d.line([(0,150),(210,170),(350,105)],fill=(103,45,170,120),width=46)
    d.line([(0,210),(245,185),(390,225)],fill=(45,120,190,90),width=28)
    for i in range(40):
        rr=random.Random(i); x=rr.randint(0,W); y=rr.randint(45,H-45); d.ellipse([x,y,x+5,y+5],fill=(255,225,255,115))
    for i in range(16):
        rr=random.Random(i+90); x=rr.randint(0,W); y=rr.randint(80,H-80); d.ellipse([x,y,x+20,y+10],fill=(83,165,50,160))
    def person(cx,cy,hair):
        d.ellipse([cx-45,cy-135,cx+45,cy-45],fill=(246,202,176,255),outline=(255,240,220,180),width=2)
        if hair=='orange':
            col=(232,118,35,245); d.pieslice([cx-72,cy-158,cx+68,cy-24],180,360,fill=col)
            for k in range(3): d.ellipse([cx+35+k*42,cy-25+k*18,cx+88+k*42,cy+28+k*18],fill=col)
            dress=(238,235,244,245)
        else:
            col=(30,25,28,245); d.pieslice([cx-65,cy-160,cx+65,cy-20],180,360,fill=col); d.rectangle([cx-55,cy-100,cx+55,cy-30],fill=col); dress=(38,34,38,250)
        d.polygon([(cx-70,cy-20),(cx+70,cy-20),(cx+100,cy+165),(cx-95,cy+165)],fill=dress)
        d.ellipse([cx-18,cy-88,cx-7,cy-77],fill=(55,45,45,255)); d.ellipse([cx+7,cy-88,cx+18,cy-77],fill=(55,45,45,255))
    person(430,420,'orange'); person(780,410,'black')
    if title:
        add_text(img,'神树苏醒',330,font_title)
        add_text(img,'下一站，雾境之外',405,font_small)
    else:
        add_text(img,'她们终于明白：\n门，已经打开了。',612)
    bars(img).save(path,quality=95)

def make_audio():
    sr=44100; dur=20; n=int(sr*dur)
    data=[]
    for i in range(n):
        t=i/sr; env=min(1,t/3)*min(1,(dur-t)/2)
        beat=0
        if t>4:
            ph=(t-4)%0.5; beat=math.exp(-ph*20)*.36
        swell=math.sin(2*math.pi*(55+15*math.sin(t*.22))*t)*.18
        pad=math.sin(2*math.pi*220*t)*.035+math.sin(2*math.pi*330*t)*.025
        climax=math.sin(2*math.pi*110*t)*.10*max(0,math.sin((t-8)/6*math.pi)) if 8<t<14 else 0
        s=(swell+pad+beat+climax)*.45*env
        data.append(max(-1,min(1,s)))
    with wave.open(AUDIO,'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        for s in data: wf.writeframes(struct.pack('<h',int(s*32767)))

def run():
    p1=os.path.join(OUT_DIR,'01_tree.jpg'); p2=os.path.join(OUT_DIR,'02_dragon.jpg'); p3=os.path.join(OUT_DIR,'03_awakening.jpg'); p4=os.path.join(OUT_DIR,'04_guardians.jpg'); p5=os.path.join(OUT_DIR,'05_title.jpg')
    scene_tree(p1,False,'传说，神树醒来之日，\n天空会坠入梦境。')
    scene_dragon(p2)
    scene_tree(p3,True,'但它不是毁灭，\n而是在选择新的守望者。')
    scene_guardians(p4,False)
    scene_guardians(p5,True)
    Image.open(p4).save(POSTER)
    make_audio()
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    # each still gets a slow Ken Burns zoom/pan; xfade creates flash/smooth transitions.
    filt="""
[0:v]zoompan=z='min(zoom+0.0018,1.12)':d=96:s=1280x720:fps=24,format=yuv420p[v0];
[1:v]zoompan=z='1.12-0.0012*on':x='iw/2-(iw/zoom/2)+sin(on/7)*20':y='ih/2-(ih/zoom/2)':d=96:s=1280x720:fps=24,format=yuv420p[v1];
[2:v]zoompan=z='1.04+0.0022*on':d=120:s=1280x720:fps=24,format=yuv420p[v2];
[3:v]zoompan=z='1.03+0.0014*on':x='iw/2-(iw/zoom/2)+on/3':d=96:s=1280x720:fps=24,format=yuv420p[v3];
[4:v]zoompan=z='1.06':d=72:s=1280x720:fps=24,format=yuv420p[v4];
[v0][v1]xfade=transition=radial:duration=0.55:offset=3.45[x1];
[x1][v2]xfade=transition=wipetl:duration=0.65:offset=6.90[x2];
[x2][v3]xfade=transition=wipeleft:duration=0.8:offset=11.25[x3];
[x3][v4]xfade=transition=fadeblack:duration=0.75:offset=14.70[v]
""".replace('\n','')
    cmd=[ff,'-y','-loop','1','-i',p1,'-loop','1','-i',p2,'-loop','1','-i',p3,'-loop','1','-i',p4,'-loop','1','-i',p5,'-i',AUDIO,'-filter_complex',filt,'-map','[v]','-map','5:a','-t','18','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',VIDEO]
    subprocess.run(cmd,check=True)
    print(VIDEO)
if __name__=='__main__': run()
