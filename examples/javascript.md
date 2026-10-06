# Contoh JavaScript — jadwal-sholat-indonesia

Ambil jadwal sholat hari ini untuk sebuah kota langsung dari CDN,
tanpa install apa pun.

```js
const BASE = 'https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api';

// daftar kota yang tersedia
const cities = await (await fetch(`${BASE}/cities.json`)).json();
// -> [{ code: 'jakarta', name: 'Jakarta', province: 'DKI Jakarta',
//      lat: -6.21, lng: 106.85, timezone: 'WIB' }, ...]

// jadwal Jakarta tahun 2026 (satu file berisi 365/366 hari)
const times = await (await fetch(`${BASE}/times/jakarta/2026.json`)).json();

// cari hari ini
const today = new Date().toISOString().slice(0, 10);
const now = times.find(d => d.date === today);
console.log(now);
// -> { date: '2026-10-07', imsak: '04:10', subuh: '04:20',
//      terbit: '05:32', dzuhur: '11:44', ashar: '14:46',
//      maghrib: '17:50', isya: '18:58' }

// waktu sholat berikutnya dari jam sekarang
function nextPrayer(day, nowHHMM) {
  const order = ['imsak','subuh','terbit','dzuhur','ashar','maghrib','isya'];
  for (const k of order) {
    if (day[k] > nowHHMM) return { name: k, time: day[k] };
  }
  return null; // sudah lewat isya
}
```

> Ganti `ANGGATYASIA` dengan username GitHub kamu jika fork repo ini.
> Daftar kode kota: lihat [`api/cities.json`](../api/cities.json).
