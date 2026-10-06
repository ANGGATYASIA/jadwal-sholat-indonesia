# Jadwal Sholat Indonesia

**API dan dataset jadwal sholat harian per kota di Indonesia, gratis.**
84 kota (38 ibu kota provinsi + kota-kota besar), tahun 2026–2028, metode
Kementerian Agama RI. Berupa JSON statis yang tinggal di-`fetch` lewat CDN —
tanpa install, tanpa API key, tanpa server.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Metode: Kemenag RI](https://img.shields.io/badge/Metode-Kemenag%20RI-green)](#metode-perhitungan)

Terakhir diperbarui: 6 Oktober 2026.

## Pakai langsung tanpa install

```js
const BASE = 'https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api';

// daftar 84 kota (kode, nama, koordinat, zona waktu)
const cities = await (await fetch(`${BASE}/cities.json`)).json();

// jadwal Jakarta 2026 — satu file berisi 365 hari
const times = await (await fetch(`${BASE}/times/jakarta/2026.json`)).json();

// hari ini
const today = new Date().toISOString().slice(0, 10);
const now = times.find(d => d.date === today);
// -> { date: '2026-10-07', imsak: '04:10', subuh: '04:20', terbit: '05:32',
//      dzuhur: '11:44', ashar: '14:46', maghrib: '17:50', isya: '18:58' }
```

Pola URL:

```text
https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api/cities.json
https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api/index.json
https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api/times/{kode_kota}/{tahun}.json
```

Contoh kode lengkap: [`examples/javascript.md`](examples/javascript.md),
[`examples/python.md`](examples/python.md),
[`examples/php-laravel.md`](examples/php-laravel.md). Demo widget siap pakai:
[`demo.html`](demo.html).

Ganti `ANGGATYASIA` dengan username GitHub kamu jika fork repo ini.

## Cakupan data

| Isi | Jumlah |
|---|---|
| Kota | 84 (38 ibu kota provinsi + 46 kota besar) |
| Tahun | 2026, 2027, 2028 (kabisat otomatis 366 hari) |
| Hari per kota per tahun | 365/366 |
| Total file JSON jadwal | 252 |
| Zona waktu | WIB, WITA, WIT mengikuti kota |

Versi CSV untuk impor database ada di `data/times/{kode_kota}_{tahun}.csv`
dengan kolom `date,imsak,subuh,terbit,dzuhur,ashar,maghrib,isya`.

## Metode perhitungan

Dihitung dengan **metode hisab Kementerian Agama RI**: Subuh saat matahari
−20° di bawah ufuk, Isya −18°, Maghrib/Terbit −1°, Ashar mengikuti mazhab
Syafi'i, plus ikhtiyat (Dzuhur +3 menit, lainnya +2 menit, Terbit −2 menit)
dan Imsak 10 menit sebelum Subuh.

Hasilnya divalidasi terhadap jadwal resmi Bimas Islam Kemenag untuk DKI
Jakarta 7 Oktober 2026: 4 dari 7 waktu sama persis menitnya, 3 sisanya
selisih 1–2 menit (perbedaan titik markaz). Detail dan tabel validasi:
[`SUMBER-DATA.md`](SUMBER-DATA.md).

## FAQ

**Apakah jadwal sholat ini akurat?**
Dihitung dengan parameter resmi Kemenag RI dan tervalidasi ±2 menit dari
jadwal Bimas Islam Kemenag. Koordinat memakai titik pusat kota (±0,1°),
yang mengubah hasil dalam orde detik hingga ±1 menit. Untuk kebutuhan
ibadah yang presisi, tetap rujuk
[bimasislam.kemenag.go.id](https://bimasislam.kemenag.go.id).

**Metode apa yang dipakai?**
Metode Kementerian Agama RI: sudut Subuh 20°, sudut Isya 18°, Ashar
Syafi'i, dengan ikhtiyat. Bukan metode MWL, ISNA, atau Mesir.

**Kota apa saja yang tersedia?**
38 ibu kota provinsi plus kota-kota besar seperti Bogor, Depok, Bekasi,
Tangerang, Batam, Balikpapan, dan Manado — total 84 kota. Daftar lengkap
di [`api/cities.json`](api/cities.json).

**Bagaimana cara memakai API-nya?**
Tidak ada API key dan tidak ada server. Fetch file JSON langsung dari CDN
jsDelivr seperti contoh di atas, atau unduh file CSV untuk diimpor ke
database.

**Apakah gratis untuk dipakai komersial?**
Ya. Lisensi MIT — bebas dipakai aplikasi komersial, dimodifikasi, dan
didistribusikan ulang.

**Kotaku tidak ada di daftar, bagaimana?**
Tambahkan satu baris ke [`source/cities.json`](source/cities.json)
(kode, nama, provinsi, lintang, bujur, zona waktu), jalankan
`python3 scripts/build.py`, dan kirim pull request.

**Sampai tahun berapa datanya tersedia?**
2026–2028. Tahun baru ditambahkan tiap akhir tahun via regenerasi script.

## Regenerasi

Seluruh file `api/` dan `data/` dihasilkan oleh
[`scripts/build.py`](scripts/build.py). Untuk menambah kota atau tahun:

```bash
python3 scripts/build.py
```

## Lisensi

MIT — lihat [`LICENSE`](LICENSE).
