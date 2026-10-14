# Dashboard Warehouse Nasional

Dashboard monitoring gudang PT Bangor Berkembang Bersama.
Sumber: 1 Google Sheets → 1 sheet = 1 tab.

- `index.html` — dashboard (Chart.js CDN). Buka langsung di browser atau via GitHub Pages.
- `new-data.js` — snapshot agregat 7 sheet, auto-generated via `gen_new.py`.
- `gen_new.py` — generator snapshot (fetch CSV tiap sheet → agregat → `new-data.js`).

## Tab
1. 🧾 Adjustment — akun & tipe penyesuaian per bulan/gudang (filter bulan, gudang, metrik)
2. 🚚 Ontime Delivery — % tepat waktu, keterlambatan, per ekspedisi (filter bulan, status)
3. 🎯 Stock Akurasi — SO vs Accurate harian & per item (cari item)
4. 📦 Fullfilment MWH — SO vs DO vs Fisik per bulan & item (filter bulan)
5. 🏅 GMP — skor per warehouse per bulan + heatmap (filter warehouse)
6. 📢 Komplain — status, CoA, value (filter status)
7. ⚙️ MPS — man power & productivity Inbound/Outbound (filter section)

Setiap tab punya tombol **Tampilkan** (terapkan filter), **Reset**, dan **Refresh Data** (tarik live dari Sheets).
