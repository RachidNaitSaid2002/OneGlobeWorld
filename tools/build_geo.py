"""Build data/geo.json from Natural Earth 50m countries (de facto borders) with the series' map decisions:
- Morocco is one shape with Western Sahara.
- Israel is not in the series: its area becomes part of Palestine, except the Golan Heights, which goes to Syria.
Usage: python3 tools/build_geo.py ne_50m_admin_0_countries.geojson
"""
import json, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0,HERE)
from detect_country import ISO
src=json.load(open(sys.argv[1]))
old={f['iso']:f['n'] for f in json.load(open(os.path.join(ROOT,'data','geo.json')))}
name_by_iso={}
for n,i in ISO.items(): name_by_iso.setdefault(i,n)
data_names={c['n'] for c in json.load(open(os.path.join(ROOT,'data','data.json')))['countries']}

def polys(geom): return geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
def area(r): return sum(r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1] for i in range(len(r)-1))/2
def ccw(r): r=[tuple(p) for p in r]; return r if area(r)>0 else r[::-1]
def union(rings):
    """Union of outer rings that touch along identical vertices (Natural Earth is topologically consistent)."""
    E=[]
    for r in rings:
        r=ccw(r); E+=[(r[i],r[i+1]) for i in range(len(r)-1) if r[i]!=r[i+1]]
    S=set(E); keep=[e for e in E if (e[1],e[0]) not in S]
    nxt={}
    for a,b in keep: nxt.setdefault(a,[]).append(b)
    used=set(); out=[]
    for a,b in keep:
        if (a,b) in used: continue
        ring=[a]; cur=a; nb=b
        while True:
            used.add((cur,nb)); ring.append(nb); cur=nb
            if cur==a: break
            cand=[x for x in nxt.get(cur,[]) if (cur,x) not in used]
            if not cand: break
            nb=cand[0]
        if ring[0]==ring[-1] and len(ring)>3: out.append(ring)
    return out

F={f['properties']['ADMIN']:f for f in src['features']}
special={}
# Morocco + Western Sahara
special['MA']=[[r] for r in union([polys(F['Morocco']['geometry'])[0][0],polys(F['Western Sahara']['geometry'])[0][0]])]
# Israel: split off the Golan Heights along the pre-1967 line (Jordan river / east shore of the Sea of Galilee)
il=[tuple(p) for p in polys(F['Israel']['geometry'])[0][0]]
iN=il.index((35.6272,33.275)) if (35.6272,33.275) in il else min(range(len(il)),key=lambda i:(il[i][0]-35.6272)**2+(il[i][1]-33.275)**2)
iS=min(range(len(il)),key=lambda i:(il[i][0]-35.7345)**2+(il[i][1]-32.7289)**2)
cut=[(35.645,33.20),(35.62,33.10),(35.63,32.98),(35.64,32.89),(35.645,32.80),(35.66,32.70)]  # north -> south
ring=il[:-1]; n=len(ring)
def walk(a,b):
    out=[];i=a
    while True:
        out.append(ring[i])
        if i==b: break
        i=(i+1)%n
    return out
golan=walk(iN,iS)+cut[::-1]; golan.append(golan[0])
rest=walk((iS+1)%n,iN)+cut; rest.append(rest[0])
ps=[P[0] for P in polys(F['Palestine']['geometry'])]
special['PS']=[[r] for r in union([rest]+ps)]
special['SY']=[[r] for r in union([golan,polys(F['Syria']['geometry'])[0][0]])]
ALIAS={'Antigua and Barb.':'Antigua and Barbuda','Marshall Is.':'Marshall Islands','St. Kitts and Nevis':'Saint Kitts and Nevis','Cabo Verde':'Cape Verde','Cayman Is.':'Cayman Islands','N. Cyprus':'Northern Cyprus','St. Vin. and Gren.':'Saint Vincent and the Grenadines','Vatican':'Vatican City'}
skip={'Israel','Western Sahara','Palestine','Syria','Morocco'}
out=[]
def rnd(P): return [[[round(x,3),round(y,3)] for x,y in ring] for ring in P]
for f in src['features']:
    p=f['properties']; ad=p['ADMIN']
    iso=p['ISO_A2_EH'] if p['ISO_A2_EH'] not in ('-99',None) else p['ISO_A2']
    if ad in skip: continue
    nm=ALIAS.get(p['NAME']) or old.get(iso) or (name_by_iso.get(iso) if name_by_iso.get(iso) in data_names else None) or p['NAME']
    o={'n':nm,'iso':iso,'p':[rnd(P) for P in polys(f['geometry'])]}
    if p['TYPE'] in ('Dependency','Indeterminate') or (p['TYPE']=='Country' and p['SOVEREIGNT']!=p['ADMIN'] and nm not in data_names) or (p['TYPE']=='Disputed' and nm not in data_names): o['dep']=1
    out.append(o)
for iso,nm in (('MA','Morocco'),('PS','Palestine'),('SY','Syria')):
    out.append({'n':old.get(iso,nm),'iso':iso,'p':[rnd(P) for P in special[iso]]})
M={}
for f in out:
    if f['n'] in M:
        M[f['n']]['p']+=f['p']; M[f['n']].pop('dep',None) if not f.get('dep') else None
    else: M[f['n']]=f
out=sorted(M.values(),key=lambda f:f['n'])
json.dump(out,open(os.path.join(ROOT,'data','geo.json'),'w'),separators=(',',':'),ensure_ascii=False)
print(len(out),'shapes; MA rings',len(special['MA']),'PS rings',len(special['PS']),'SY rings',len(special['SY']))
