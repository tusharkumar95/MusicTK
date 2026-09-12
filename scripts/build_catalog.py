import json, os, re, urllib.parse, urllib.request

BASE='https://archive.org'
OUT='catalog.json'
TARGET=120
SEARCHES=[
    'mediatype:audio AND subject:music AND licenseurl:*creativecommons.org*',
    'mediatype:audio AND subject:music AND rights:"public domain"',
]


def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'musicTK/1.0'})
    with urllib.request.urlopen(req,timeout=20) as r:
        return json.load(r)


def clean(v):
    if isinstance(v,list):
        return ', '.join(str(x) for x in v)
    return str(v or '').strip()


def playable(files):
    good=[]
    for f in files or []:
        name=clean(f.get('name'))
        low=name.lower()
        if f.get('private') or f.get('source') not in (None,'original'):
            continue
        if not re.search(r'\.(mp3|m4a|ogg|oga|wav|flac)$',low):
            continue
        try: size=int(f.get('size') or 0)
        except ValueError: size=0
        if size and size>35_000_000:
            continue
        good.append(f)
    good.sort(key=lambda x: (not x.get('name','').lower().endswith('.mp3'), len(x.get('name',''))))
    return good[0] if good else None

items=[]
seen=set()
for query in SEARCHES:
    params=urllib.parse.urlencode({'q':query,'fl[]':['identifier','title','creator','licenseurl','rights','subject'],'rows':250,'page':1,'output':'json'},doseq=True)
    data=get_json(f'{BASE}/advancedsearch.php?{params}')
    for doc in data.get('response',{}).get('docs',[]):
        ident=clean(doc.get('identifier'))
        if not ident or ident in seen: continue
        seen.add(ident)
        try:
            md=get_json(f'{BASE}/metadata/{urllib.parse.quote(ident,safe="")}')
        except Exception:
            continue
        meta=md.get('metadata',{})
        license_url=clean(meta.get('licenseurl') or doc.get('licenseurl'))
        rights=clean(meta.get('rights') or doc.get('rights'))
        allowed=('creativecommons.org/licenses/by/' in license_url.lower() or
                 'creativecommons.org/licenses/by-sa/' in license_url.lower() or
                 'creativecommons.org/publicdomain/' in license_url.lower() or
                 'public domain' in rights.lower())
        if not allowed: continue
        f=playable(md.get('files'))
        if not f: continue
        creator=clean(meta.get('creator') or doc.get('creator') or 'Unknown artist')
        title=clean(meta.get('title') or doc.get('title') or ident)
        if len(title)>140: title=title[:137]+'...'
        ext=os.path.splitext(f['name'])[1].lower()
        mime={'.mp3':'audio/mpeg','.m4a':'audio/mp4','.ogg':'audio/ogg','.oga':'audio/ogg','.wav':'audio/wav','.flac':'audio/flac'}.get(ext,'audio/mpeg')
        if 'publicdomain' in license_url.lower() or 'public domain' in rights.lower(): label='Public Domain'
        elif 'by-sa' in license_url.lower(): label='CC BY-SA'
        else: label='CC BY'
        items.append({'id':ident+'::'+f['name'],'title':title,'artist':creator,'url':f'{BASE}/download/{urllib.parse.quote(ident,safe="")}/{urllib.parse.quote(f["name"],safe="")}', 'mime':mime,'license':label,'source':'Internet Archive'})
        if len(items)>=TARGET: break
    if len(items)>=TARGET: break

with open(OUT,'w',encoding='utf-8') as out:
    json.dump(items, out, ensure_ascii=False, indent=2)
print(f'Wrote {len(items)} tracks to {OUT}')
if len(items)<50:
    raise SystemExit('Catalog contains fewer than 50 tracks')
