"""Make a JS snippet that turns the HEAD version of the Pine script (stored in localStorage claude_pb_v6) into the working copy, sending only changed text."""
import json, subprocess, difflib, sys
p = 'strategies/pine/MNQ_PLAYBOOK.pine'
base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
old = subprocess.run(['git', 'show', base + ':' + p], capture_output=True, text=True).stdout
new = open(p).read()
ops = [(i1, i2, new[j1:j2]) for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes() if t != 'equal']
h = 0
for c in new: h = (h * 31 + ord(c)) % 1000000007
js = "(()=>{let s=localStorage.getItem('claude_pb_v6');const ops=" + json.dumps(ops, ensure_ascii=False) + ";for(let k=ops.length-1;k>=0;k--){const [a,b,t]=ops[k];s=s.slice(0,a)+t+s.slice(b);}let h=0;for(const c of s)h=(h*31+c.codePointAt(0))%1000000007;if(h===" + str(h) + ")localStorage.setItem('claude_pb_v6',s);return [h," + str(h) + ",s.length];})()"
print(js)
