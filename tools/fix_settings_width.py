import sys
CSS = """
/* keep settings inside the screen: long voice names must not stretch the panel */
.settings{grid-template-columns:minmax(0,1fr)}
.settings > *{min-width:0}
.settings select{max-width:100%;text-overflow:ellipsis}
.voicerow,.vr,.backup{min-width:0}
.vr select{width:100%;min-width:0}
.app{overflow-x:clip}
"""
for p in sys.argv[1:]:
    s=open(p).read()
    if 'keep settings inside the screen' in s: print('already',p); continue
    i=s.index('</style>'); s=s[:i]+CSS+s[i:]; open(p,'w').write(s); print('patched',p)
