# Contoh Python — jadwal-sholat-indonesia

```python
import json
import urllib.request
from datetime import date

BASE = 'https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api'

def get_json(path):
    with urllib.request.urlopen(f'{BASE}/{path}') as r:
        return json.load(r)

# jadwal Jakarta tahun berjalan
year = date.today().year
times = get_json(f'times/jakarta/{year}.json')

today = date.today().isoformat()
now = next(d for d in times if d['date'] == today)
print(f"Jadwal sholat Jakarta, {today}:")
for k in ('imsak', 'subuh', 'terbit', 'dzuhur', 'ashar', 'maghrib', 'isya'):
    print(f'  {k:8s} {now[k]}')

# atau baca dari CSV lokal setelah clone
import csv
with open('data/times/jakarta_2026.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
print('baris CSV:', len(rows))
```

> Ganti `ANGGATYASIA` dengan username GitHub kamu jika fork repo ini.
