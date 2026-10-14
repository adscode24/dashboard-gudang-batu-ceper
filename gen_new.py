import urllib.request, csv, json, io, re

SHEET = '1T-rBKq7JuPsj6fa4y9u58vVr5fdKcQp0gG6DyEDL_-c'
GIDS = {'adj': '0', 'ontime': '1842167571', 'stock': '224297307',
        'fulfil': '1512613846', 'gmp': '621504746',
        'komplain': '404119534', 'mps': '1949034971'}


def fetch(gid):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET}/export?format=csv&gid={gid}'
    raw = urllib.request.urlopen(url, timeout=180).read().decode('utf-8', errors='replace')
    return list(csv.reader(io.StringIO(raw)))


def num(s):
    s = re.sub(r'[^0-9.\-]', '', s or '')
    try:
        return float(s) if s not in ('', '-', '.', '-.') else 0.0
    except Exception:
        return 0.0


def inum(s):
    s = re.sub(r'[^0-9\-]', '', (s or '').split('.')[0])
    try:
        return int(s) if s not in ('', '-', '--') else 0
    except Exception:
        return 0


OUT = {}

# ---------- 1. ADJUSTMENT (same format as before) ----------
rows = fetch(GIDS['adj'])
hIdx = next((i for i, r in enumerate(rows[:20]) if 'Nomor #' in '|'.join(r)), 8)
akunBulan, tipeBulan, tipeGudang, aGB, tGB = {}, {}, {}, {}, {}
nRec, totBiaya, totQty = 0, 0.0, 0.0


def bump(d, k, biaya, qty):
    e = d.setdefault(k, [0, 0.0, 0.0])
    e[0] += 1
    e[1] += biaya
    e[2] += qty


for r in rows[hIdx + 1:]:
    r = list(r) + [''] * 14
    if not r[1] and not r[2] and not r[3]:
        continue
    qty = num(r[4])
    tipe = (r[6] or '').strip() or '-'
    akun = (r[7] or '').strip() or '-'
    biaya = num(r[8])
    gud = (r[9] or '').strip() or '-'
    bln = (r[11] or '').strip() or '-'
    nRec += 1
    totBiaya += biaya
    totQty += qty
    bump(akunBulan, akun + '||' + bln, biaya, qty)
    bump(tipeBulan, tipe + '||' + bln, biaya, qty)
    bump(tipeGudang, tipe + '||' + gud, biaya, qty)
    bump(aGB, akun + '||' + gud + '||' + bln, biaya, qty)
    bump(tGB, tipe + '||' + gud + '||' + bln, biaya, qty)
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
OUT['adj'] = {'months': [m for m in MONTHS if any(k.split('||')[1] == m for k in akunBulan)],
              'akunBulan': akunBulan, 'tipeBulan': tipeBulan, 'tipeGudang': tipeGudang,
              'akunGudangBulan': aGB, 'tipeGudangBulan': tGB,
              'totals': {'n': nRec, 'biaya': round(totBiaya), 'qty': round(totQty, 2)}}
print('ADJ recs:', nRec, 'months:', OUT['adj']['months'], flush=True)

# ---------- 2. ONTIME ----------
rows = fetch(GIDS['ontime'])
recs = []
for r in rows[1:]:
    r = list(r) + [''] * 12
    tgl = (r[0] or '').strip()
    if not tgl or 'total' in tgl.lower():
        continue
    recs.append({'tgl': tgl, 'outlet': (r[1] or '').strip(), 'ekspedisi': (r[3] or '').strip(),
                 'eta': (r[4] or '').strip(), 'actual': (r[5] or '').strip(),
                 'status': (r[6] or '').strip() or '-', 'komplain': (r[7] or '').strip() or '-'})
OUT['ontime'] = {'recs': recs}
st = {}
for x in recs:
    st[x['status']] = st.get(x['status'], 0) + 1
print('ONTIME recs:', len(recs), 'status:', st, flush=True)

# ---------- 3. STOCK ----------
rows = fetch(GIDS['stock'])
month_label = (rows[0][0] or '').strip()
items = []
daily = [{'so': 0, 'acc': 0, 'sel': 0} for _ in range(31)]
for r in rows[2:]:
    if not (r[0] or '').strip() or (r[0] or '').strip().lower() in ('nama item',):
        if not (r[0] or '').strip():
            continue
    nm = (r[0] or '').strip()
    uom = (r[1] or '').strip()
    so_t = acc_t = sel_t = 0
    days_active = 0
    for d in range(31):
        so = inum(r[2 + d * 3] if len(r) > 2 + d * 3 else '')
        ac = inum(r[3 + d * 3] if len(r) > 3 + d * 3 else '')
        se = inum(r[4 + d * 3] if len(r) > 4 + d * 3 else '')
        if so or ac or se:
            days_active += 1
        so_t += so
        acc_t += ac
        sel_t += se
        daily[d]['so'] += so
        daily[d]['acc'] += ac
        daily[d]['sel'] += abs(se)
    items.append([nm, uom, so_t, acc_t, sel_t, days_active])
OUT['stock'] = {'month': month_label, 'daily': daily, 'items': items}
print('STOCK month:', month_label, 'items:', len(items), flush=True)

# ---------- 4. FULFIL ----------
rows = fetch(GIDS['fulfil'])
item_names = []
ful_daily, ful_item = {}, {}
ful_months = []
cur = None
Monat = {'oktober': 'Oktober', 'september': 'September', 'juli': 'Juli', 'juni': 'Juni',
         'januari': 'Januari', 'februari': 'Februari', 'maret': 'Maret', 'april': 'April',
         'mei': 'Mei', 'agustus': 'Agustus', 'november': 'November', 'desember': 'Desember'}
last_tgl = ''
for i, r in enumerate(rows):
    c1 = (r[1] or '').strip()
    if c1.lower() == 'bulan':
        # header row: item names are in the nearest rows above with col F filled
        for j in range(i - 1, max(-1, i - 5), -1):
            if (rows[j][5] or '').strip() and not (rows[j][1] or '').strip() and not (rows[j][4] or '').strip():
                # ensure it's item-name row (next row should be satuan like Pack/Pcs)
                item_names = [(rows[j][k] or '').strip() for k in range(5, len(rows[j]))]
                break
        cur = '__HDR__'
        last_tgl = ''
        continue
    if cur is None:
        continue
    if cur == '__HDR__':
        # first data row carries month label in col B
        if c1:
            std = Monat.get(c1.lower(), c1)
            cur = std
            if std not in ful_months:
                ful_months.append(std)
        else:
            continue
    if c1:
        std = Monat.get(c1.lower(), c1)
        if std != cur and std in Monat.values():
            cur = std
            if std not in ful_months:
                ful_months.append(std)
    typ = (r[4] or '').strip().upper()
    if typ not in ('SO', 'DO', 'FISIK'):
        continue
    tgl = (r[2] or '').strip() or (r[3] or '').strip() or last_tgl
    if not tgl:
        continue
    last_tgl = tgl
    tot = 0.0
    for j in range(5, len(r)):
        q = num(r[j])
        if q:
            tot += q
            inm = item_names[j - 5] if j - 5 < len(item_names) else ''
            if inm:
                k = cur + '||' + inm + '||' + typ
                e = ful_item.setdefault(k, [0.0, 0])
                e[0] += q
                e[1] += 1
    ful_daily[cur + '||' + tgl + '||' + typ] = ful_daily.get(cur + '||' + tgl + '||' + typ, 0.0) + tot
OUT['fulfil'] = {'months': ful_months, 'items': item_names,
                 'daily': {k: round(v) for k, v in ful_daily.items()},
                 'itemMonth': {k: [round(v[0]), v[1]] for k, v in ful_item.items()}}
print('FULFIL months:', ful_months, 'items:', len(item_names), 'dailyKeys:', len(ful_daily), flush=True)

# ---------- 5. GMP ----------
rows = fetch(GIDS['gmp'])
hi = next((i for i, r in enumerate(rows) if 'Bulan' in r), 5)
whs = [(r or '').strip() for r in rows[hi][2:] if (r or '').strip() and (r or '').strip().lower() != 'average']
gmp_months, gmp_vals = [], {}
for r in rows[hi + 1:]:
    m = (r[1] or '').strip()
    if not m or m.lower().startswith('average'):
        continue
    if not any((r[j] or '').strip() for j in range(2, len(r))):
        continue
    gmp_months.append(m)
    for j, w in enumerate(whs):
        v = (r[2 + j] or '').strip().replace('.', '').replace(',', '.')
        try:
            gmp_vals[m + '||' + w] = float(v) if v else None
        except Exception:
            gmp_vals[m + '||' + w] = None
OUT['gmp'] = {'months': gmp_months, 'whs': whs, 'vals': gmp_vals}
print('GMP months:', gmp_months, 'whs:', whs, flush=True)

# ---------- 6. KOMPLAIN ----------
rows = fetch(GIDS['komplain'])
hi = next((i for i, r in enumerate(rows) if 'No' in r and 'Kasus' in '|'.join(r)), 1)
krecs = []
last_head = [''] * 6
for r in rows[hi + 1:]:
    r = list(r) + [''] * 18
    item = (r[6] or '').strip()
    if not item:
        continue
    head = [(r[i] or '').strip() for i in (1, 2, 3, 4, 5)]
    if head[0]:
        last_head = head
    else:
        head = last_head
    krecs.append(head + [(r[i] or '').strip() for i in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)])
OUT['komplain'] = {'recs': krecs}
print('KOMPLAIN recs:', len(krecs), flush=True)

# ---------- 7. MPS ----------
rows = fetch(GIDS['mps'])
sections = []
cur = None
for r in rows:
    c0 = (r[0] or '').strip()
    if c0.lower() in ('inbound', 'outbound'):
        cur = {'type': c0, 'dates': {}}
        sections.append(cur)
        continue
    if cur is None:
        continue
    d = (r[1] or '').strip()
    met = (r[2] or '').strip()
    if not d or d.lower() == 'keterangan' or met not in ('Jam Kerja', 'Jmlh Crew', 'Gramasi', 'Productivity'):
        continue
    e = cur['dates'].setdefault(d, {})
    e[met] = num(r[3])
for s in sections:
    s['dates'] = [{'d': d, 'jam': v.get('Jam Kerja', 0), 'crew': v.get('Jmlh Crew', 0),
                   'gramasi': v.get('Gramasi', 0), 'prod': v.get('Productivity', 0)}
                  for d, v in s['dates'].items()]
OUT['mps'] = {'sections': [{'type': s['type'], 'dates': s['dates']} for s in sections]}
print('MPS sections:', [(s['type'], len(s['dates'])) for s in sections], flush=True)

js = '// auto-generated new warehouse dashboard data\nconst NEWDATA=' + json.dumps(OUT, separators=(',', ':'), ensure_ascii=False) + ';\n'
with open('new-data.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('wrote new-data.js bytes:', len(js), flush=True)
