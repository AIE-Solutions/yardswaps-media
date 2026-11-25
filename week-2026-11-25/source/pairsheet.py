# pair sheet: opener frame (1.2 s) next to app frames at 45% and 80% of the cut, one row per video
# usage: python3 pairsheet.py out.jpg a.mp4 b.mp4 ...   (continuity gate: the opener item must be the item the app shows)
import sys, subprocess, os, tempfile
from PIL import Image, ImageDraw
out=sys.argv[1]; files=sys.argv[2:]
rows=[]
for f in files:
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode().strip())
    ims=[]
    for t in (1.2, d*0.45, d*0.8):
        tmp=tempfile.mktemp(suffix='.png')
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',f,'-frames:v','1',tmp],check=True)
        ims.append(Image.open(tmp).convert('RGB').resize((270,480))); os.remove(tmp)
    rows.append((os.path.basename(f).replace('yardswaps-','').replace('-9x16.mp4',''),ims))
W=3*270+2*6+260; H=len(rows)*(480+8)
sheet=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(sheet)
for i,(name,ims) in enumerate(rows):
    y=i*488; dr.text((8,y+8),name,fill='black')
    for j,im in enumerate(ims): sheet.paste(im,(260+j*276,y))
sheet.save(out,quality=80); print(out,len(rows))
