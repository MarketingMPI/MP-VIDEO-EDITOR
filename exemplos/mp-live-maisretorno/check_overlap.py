import re
def cs(ts):
    h,m,r=ts.split(":"); s,c=r.split(".")
    return int(h)*3600+int(m)*60+int(s)+int(c)/100
rows=[]
for l in open("out/A.ass",encoding="utf-8"):
    if l.startswith("Dialogue"):
        p=l.split(",",9)
        rows.append((cs(p[1]),cs(p[2]),p[9].strip()))
for T in [3.2,25.5,43.5]:
    act=[(a,b,t) for a,b,t in rows if a<=T<b]
    print(f"t={T}:", act)
EOF_MARK=1
