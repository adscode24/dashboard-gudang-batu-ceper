# Dashboard Gudang – Batu Ceper

Dashboard Kepala Gudang PT Bangor Berkembang Bersama.
Sumber: Google Sheets Rincian Pengiriman Pesanan 01 Jan – 30 Sep 2026 (Cabang Batu Ceper).

## Isi
- `index.html` — dashboard single-file (Chart.js CDN). Buka langsung di browser atau via GitHub Pages.
- Snapshot bawaan: 2.123.551 qty, 12.638 DO, 102 SKU, 341 pelanggan, 237 hari aktif.
- Klik **Refresh Live** untuk tarik CSV terbaru dari Google Sheets.

## Jalankan lokal
```powershell
cd dashboard-gudang-batu-ceper
python -m http.server 8000
# buka http://localhost:8000
```

## Deploy Pages
Repo ini siap untuk GitHub Pages (branch `main`, root `/`).
