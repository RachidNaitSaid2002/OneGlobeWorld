"""Rebuild data/data.json from the series ranking.

Usage (from the project folder):
    python3 tools/update_data.py ../ranking.csv "Sweden:6,Poland:5,..." "after Day 7 (votes from Day 1-6 reels)"

- ranking.csv: the master ranking (columns: rank,country,day1..dayN,total,status).
  Its "status" column ("risen Day N") is used when the second argument is left out.
- Israel is never listed (series rule).
"""
import csv, json, sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from detect_country import ISO

rank_csv = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'ranking.csv')
label = sys.argv[3] if len(sys.argv) > 3 else ''
rows = list(csv.DictReader(open(rank_csv, encoding='utf-8')))
daycols = [k for k in rows[0] if re.fullmatch(r'day\d+', k)]
risen = {}
if len(sys.argv) > 2 and sys.argv[2]:
    for part in sys.argv[2].split(','):
        n, d = part.rsplit(':', 1); risen[n.strip()] = int(d)
else:
    for r in rows:
        m = re.search(r'risen Day (\d+)', r.get('status', ''))
        if m: risen[r['country']] = int(m.group(1))
geo = json.load(open(os.path.join(ROOT, 'data', 'geo.json'), encoding='utf-8'))
iso_by = {v: k for k, v in ISO.items()}
iso_geo = {f['n']: f['iso'] for f in geo}
dep = {f['n'] for f in geo if f.get('dep')}
by = {r['country']: r for r in rows}
names = set(iso_geo) | set(by)
out = []
for n in sorted(names):
    if n in ('Israel', 'Antarctica', 'Fr. S. Antarctic Lands', 'Falkland Islands', 'Greenland', 'Puerto Rico', 'New Caledonia', 'N. Cyprus', 'Somaliland') and n not in by:
        continue
    if n == 'Israel' or (n in dep and n not in by):
        continue
    r = by.get(n)
    days = [int(r[k]) for k in daycols] if r else [0] * len(daycols)
    out.append({'n': n, 'iso': iso_geo.get(n) or iso_by.get(n, ''), 'd': days, 't': sum(days), 'up': risen.get(n, 0), 'map': n in iso_geo})
json.dump({'updated': label or f'after Day {max(risen.values(), default=1)}', 'restored': len(risen), 'countries': out},
          open(os.path.join(ROOT, 'data', 'data.json'), 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
print(f'{len(out)} countries, {len(risen)} restored -> data/data.json')
