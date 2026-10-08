# Dashboard Gudang – Batu Ceper

Dashboard Kepala Gudang PT Bangor Berkembang Bersama.
Sumber: Google Sheets Rincian Pengiriman Pesanan 01 Jan – 30 Sep 2026 (Cabang Batu Ceper).

## Isi
- `index.html` — dashboard single-file + Chart.js CDN. Buka langsung di browser atau via GitHub Pages.
- `data-perbulan.js` — rincian per-bulan (102 SKU × 341 pelanggan × 11 satuan), auto-generated dari CSV Sheets.
- `adj-data.js` — pivot adjustment (akun×bulan, tipe×bulan, tipe×gudang), auto-generated dari sheet Data.
- `rec-data.js` — agregat penerimaan 12 tab bulanan (per bulan, per barang, per vendor, harian), auto-generated dengan parser adaptif.
- Snapshot bawaan: 2.123.551 qty, 12.638 DO, 102 SKU, 341 pelanggan, 237 hari aktif.

## Cara pakai filter bulan
1. Pilih bulan di dropdown (mis. Apr 2026).
2. Opsional: ketik pencarian barang.
3. Klik **Tampilkan** — seluruh KPI, grafik & tabel difilter ke bulan itu.
4. Klik **Reset** untuk kembali ke Semua Bulan.

Klik **Refresh Live** untuk tarik CSV terbaru dari Google Sheets.

## Regenerasi data per-bulan
Jalankan script `gen_data.py` (tidak ikut di-commit) atau hubungi maintainer.
