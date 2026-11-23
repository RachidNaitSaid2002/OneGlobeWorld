import json,re,os
g=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'countries_names.json'),encoding='utf-8'))
CANON={}   # alias(lower) -> canonical
ISO={}
def canon(n):
    fix={'United States of America':'United States','Czech Republic':'Czechia','Republic of Serbia':'Serbia','United Republic of Tanzania':'Tanzania','Democratic Republic of the Congo':'DR Congo','Republic of the Congo':'Congo','The Bahamas':'Bahamas','Ivory Coast':"Côte d'Ivoire",'Macedonia':'North Macedonia','eSwatini':'Eswatini','Turkey':'Türkiye','Bosnia and Herzegovina':'Bosnia and Herzegovina','Vatican':'Vatican City','South Korea':'South Korea','North Korea':'North Korea'}
    return fix.get(n,n)
for f in g['features']:
    p=f['properties']; c=canon(p['ADMIN'])
    for k in ('ADMIN','NAME','NAME_LONG'):
        if p.get(k): CANON[p[k].lower()]=c
    if p.get('ISO_A2') and p['ISO_A2']!='-99': ISO[p['ISO_A2']]=c
ISO.update({'FR':'France','NO':'Norway','VA':'Vatican City','SG':'Singapore','MT':'Malta','BH':'Bahrain','MV':'Maldives','CV':'Cape Verde','VC':'Saint Vincent and the Grenadines','HK':'Hong Kong','MU':'Mauritius','KY':'Cayman Islands','AD':'Andorra','MC':'Monaco','LI':'Liechtenstein','SM':'San Marino','TO':'Tonga','BB':'Barbados','KR':'South Korea','KP':'North Korea','TR':'Türkiye','PS':'Palestine','XK':'Kosovo','TW':'Taiwan'})
EXTRA={'usa':'United States','america':'United States','united states':'United States','us of a':'United States','czech':'Czechia','czechia':'Czechia','czeck':'Czechia','czcech':'Czechia','chekia':'Czechia','česko':'Czechia','cesko':'Czechia','češi':'Czechia','uk':'United Kingdom','england':'United Kingdom','englaaaand':'United Kingdom','britain':'United Kingdom','great britain':'United Kingdom','scotland':'United Kingdom','wales':'United Kingdom','northern ireland':'United Kingdom',
'turkey':'Türkiye','turkiye':'Türkiye','türkiye':'Türkiye','türkİye':'Türkiye','turki̇ye':'Türkiye','türki̇ye':'Türkiye','korea':'South Korea','south korea':'South Korea','north korea':'North Korea','philipines':'Philippines','phillipines':'Philippines','philippines':'Philippines','philipinesss':'Philippines','pakistan':'Pakistan','paksitan':'Pakistan','pakistaaaaan':'Pakistan','eygpt':'Egypt','belguim':'Belgium','morroco':'Morocco','morocoo':'Morocco','marocco':'Morocco','maroc':'Morocco','greeece':'Greece','polski':'Poland','polans':'Poland','polsko':'Poland','polska':'Poland','deutschland':'Germany','españa':'Spain','italia':'Italy','românia':'Romania','vatican':'Vatican City','uae':'United Arab Emirates','emirates':'United Arab Emirates','dr congo':'DR Congo','congo':'DR Congo','bosnia':'Bosnia and Herzegovina','macedonia':'North Macedonia','armrnia':'Armenia','mongol':'Mongolia','palestine':'Palestine','hong kong':'Hong Kong','singapore':'Singapore','cape verde':'Cape Verde','saint-vincent':'Saint Vincent and the Grenadines','grenadines':'Saint Vincent and the Grenadines','tonga':'Tonga','malta':'Malta','bahrain':'Bahrain','maldives':'Maldives','cayman':'Cayman Islands','luxembourg':'Luxembourg','luxenbourg':'Luxembourg','nz':'New Zealand','perú':'Peru','méxico':'Mexico','brasil':'Brazil','ivory coast':"Côte d'Ivoire",'singapur':'Singapore','kosovo':'Kosovo','andorra':'Andorra','monaco':'Monaco','liechtenstein':'Liechtenstein','san marino':'San Marino','mauritius':'Mauritius','barbados':'Barbados','taiwan':'Taiwan','georgia':'Georgia','delaware':'United States','texas':'United States','california':'United States'}
CANON.update(EXTRA)
def col(x): return re.sub(r'([a-zà-ÿ])\1+',r'\1',x)
CANON.update({col(k):v for k,v in list(CANON.items()) if col(k) not in CANON})
KEYS=sorted(CANON,key=len,reverse=True)
PAT=re.compile(r'(?<![a-zà-ÿ])('+'|'.join(re.escape(k) for k in KEYS)+r')',re.I)
def norm(s):
    s=s.lower(); s=re.sub(r'([a-zà-ÿ])\1+',r'\1',s)
    return s
def flags(s):
    cps=[ord(c) for c in s];out=[];i=0
    while i<len(cps)-1:
        if 0x1F1E6<=cps[i]<=0x1F1FF and 0x1F1E6<=cps[i+1]<=0x1F1FF: out.append(chr(cps[i]-0x1F1E6+65)+chr(cps[i+1]-0x1F1E6+65));i+=2
        else:i+=1
    return out
def detect(text):
    if not text: return None
    t=norm(str(text))
    t2=re.sub(r'@\S+','',t)
    m=PAT.search(t2)
    if m: return CANON[m.group(1).lower()]
    for raw in (str(text),):
        if '🏴\U000e0067\U000e0062' in raw: return 'United Kingdom'
    f=flags(str(text))
    if f: return ISO.get(f[0])
    return None
