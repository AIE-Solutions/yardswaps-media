# Phone bezel + shadow + walkthrough captions for the v2 app section (1080x1920)
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
D=os.path.dirname(os.path.abspath(__file__))
W,H=1080,1920
SW,SH=744,1473          # screen size (393x778 aspect)
BZ=22                   # bezel
X0=(W-SW)//2; Y0=330    # screen top-left
R_IN,R_OUT=86,106
ow,oh=SW+2*BZ,SH+2*BZ
# bezel with screen hole
bz=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(bz)
d.rounded_rectangle((X0-BZ,Y0-BZ,X0-BZ+ow,Y0-BZ+oh),radius=R_OUT,fill=(18,20,24,255))
d.rounded_rectangle((X0-BZ+3,Y0-BZ+3,X0-BZ+ow-3,Y0-BZ+oh-3),radius=R_OUT-3,outline=(60,64,72,255),width=2)
hole=Image.new("L",(W,H),0); ImageDraw.Draw(hole).rounded_rectangle((X0,Y0,X0+SW,Y0+SH),radius=R_IN,fill=255)
a=bz.getchannel("A"); a=Image.composite(Image.new("L",(W,H),0),a,hole); bz.putalpha(a)
bz.save(os.path.join(D,"bezel.png"))
# background with soft shadow
bg=Image.new("RGB",(W,H),(246,246,248)); sh=Image.new("L",(W,H),0)
ImageDraw.Draw(sh).rounded_rectangle((X0-BZ+10,Y0-BZ+40,X0-BZ+ow-10,Y0-BZ+oh+30),radius=R_OUT,fill=70)
sh=sh.filter(ImageFilter.GaussianBlur(40))
bg=Image.composite(Image.new("RGB",(W,H),(26,51,83)),bg,sh); bg.save(os.path.join(D,"appbg.png"))
F=ImageFont.truetype(os.path.join(D,"fonts/SpaceGrotesk_700Bold.ttf"),66)
caps={"w1":("Snap the washer.","Hose and all."),"w2":("The app writes","the listing."),"w3":("Set a price.","Post it free.")}
for k,(l1,l2) in caps.items():
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for i,(t,c) in enumerate([(l1,(26,51,83,255)),(l2,(37,99,235,255))]):
        w=d.textlength(t,font=F); d.text(((W-w)/2,92+i*84),t,font=F,fill=c)
    im.save(os.path.join(D,k+".png"))
print("screen",X0,Y0,SW,SH)
