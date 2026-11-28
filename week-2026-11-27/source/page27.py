# add the Nov 27 cuts to the review page: CAPS entries keyed <slug>-10s, vids entries at the top
import json,re
P='/tmp/claude-0/-home-claude/765b8cd9-b345-549d-b9fa-6b192160c528/scratchpad/page/index.html'
s=open(P).read()
if 'listed-billy-goat-leaf-vacuum-10s' in s: print('already'); raise SystemExit
pc=open('gen27-pagecaps.txt').read().strip().split('\n'); pe=open('gen27-pageentries.txt').read().strip().split('\n')
pc=[re.sub(r'^"([^"]+)":',lambda m:'"'+m.group(1)+'-10s":',l) for l in pc]
pe=[l.replace('{id:"','{id:"',1) for l in pe]
pe=[re.sub(r'\{id:"([^"]+)"',lambda m:'{id:"'+m.group(1)+'-10s"',l) for l in pe]
s=s.replace('const CAPS={\n','const CAPS={\n'+'\n'.join(pc)+'\n',1)
s=s.replace('const vids=[\n','const vids=[\n'+'\n'.join(pe)+'\n',1)
open(P,'w').write(s); print('page patched',len(pc),len(pe))
