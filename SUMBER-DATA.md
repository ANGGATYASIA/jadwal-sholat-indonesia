# Sumber & Metode Data

## Metode perhitungan

Seluruh jadwal di repo ini dihitung dengan **metode hisab Kementerian Agama
RI** (Bimas Islam), bukan dari scraping situs jadwal. Parameter yang dipakai:

| Waktu | Kriteria | Ikhtiyat |
|---|---|---|
| Subuh | Matahari −20° di bawah ufuk | +2 menit |
| Terbit | Matahari −1° | −2 menit |
| Dzuhur | Transit (kulminasi) | +3 menit |
| Ashar | Syafi'i (panjang bayangan = 1× tinggi benda + bayangan saat dzuhur) | +2 menit |
| Maghrib | Matahari −1° | +2 menit |
| Isya | Matahari −18° di bawah ufuk | +2 menit |
| Imsak | Subuh − 10 menit | — |

Detik hasil perhitungan selalu dibulatkan ke atas menjadi menit penuh
(kecuali Terbit yang dibuang), sesuai standar baku hisab rukyat Kemenag.

Perhitungan astronomis (deklinasi matahari, equation of time, sudut jam)
diimplementasikan di [`scripts/build.py`](scripts/build.py) dan dapat
diaudit siapa saja.

## Validasi

Hasil perhitungan divalidasi terhadap **jadwal resmi Bimas Islam Kemenag**
untuk DKI Jakarta, Rabu 7 Oktober 2026:

| Waktu | Repo ini | Kemenag | Selisih |
|---|---|---|---|
| Imsak | 04:10 | 04:10 | 0 |
| Subuh | 04:20 | 04:20 | 0 |
| Terbit | 05:32 | 05:34 | 2 mnt |
| Dzuhur | 11:44 | 11:43 | 1 mnt |
| Ashar | 14:46 | 14:46 | 0 |
| Maghrib | 17:50 | 17:49 | 1 mnt |
| Isya | 18:58 | 18:58 | 0 |

Selisih ±2 menit berasal dari perbedaan titik markaz dan sumber data
efemeris. Untuk kebutuhan ibadah yang presisi, tetap rujuk jadwal resmi
Kemenag di [bimasislam.kemenag.go.id](https://bimasislam.kemenag.go.id).

## Koordinat kota

Lintang/bujur tiap kota adalah titik pusat kota (±0,1°). Pergeseran
beberapa kilometer mengubah jadwal dalam orde detik hingga ±1 menit —
tidak signifikan untuk penggunaan umum (aplikasi, widget, reminder).

## Cakupan

- Kota: ibu kota 38 provinsi + kota-kota besar Indonesia (lihat
  [`api/cities.json`](api/cities.json) dan [`source/cities.json`](source/cities.json))
- Tahun: 2026–2028. Tahun kabisat otomatis berisi 366 hari.
- Zona waktu: WIB (UTC+7), WITA (UTC+8), WIT (UTC+9) mengikuti kota.

## Regenerasi & kontribusi

Tambah kota baru dengan menambah satu baris ke `source/cities.json`
(format: `code`, `name`, `province`, `lat`, `lng`, `timezone`), lalu:

```bash
python3 scripts/build.py
```

Koreksi koordinat atau parameter sangat diterima via pull request.
Sertakan sumbernya (mis. koordinat dari OpenStreetMap, parameter dari
dokumen Kemenag).
