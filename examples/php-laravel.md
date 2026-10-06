# Contoh Laravel — jadwal-sholat-indonesia

Seeder yang mengimpor satu tahun jadwal sebuah kota ke database.

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class JadwalSholatSeeder extends Seeder
{
    public function run(): void
    {
        $base = 'https://cdn.jsdelivr.net/gh/ANGGATYASIA/jadwal-sholat-indonesia@main/api';
        $city = 'jakarta';
        $year = now()->year;

        $times = Http::get("{$base}/times/{$city}/{$year}.json")->json();

        $rows = array_map(fn ($d) => [
            'city_code' => $city,
            'date'      => $d['date'],
            'imsak'     => $d['imsak'],
            'subuh'     => $d['subuh'],
            'terbit'    => $d['terbit'],
            'dzuhur'    => $d['dzuhur'],
            'ashar'     => $d['ashar'],
            'maghrib'   => $d['maghrib'],
            'isya'      => $d['isya'],
        ], $times);

        DB::table('jadwal_sholat')->upsert(
            $rows, ['city_code', 'date'], // unique key
            ['imsak','subuh','terbit','dzuhur','ashar','maghrib','isya']
        );
    }
}
```

Migrasi tabel yang cocok:

```php
Schema::create('jadwal_sholat', function (Blueprint $table) {
    $table->string('city_code', 32);
    $table->date('date');
    $table->char('imsak', 5);
    $table->char('subuh', 5);
    $table->char('terbit', 5);
    $table->char('dzuhur', 5);
    $table->char('ashar', 5);
    $table->char('maghrib', 5);
    $table->char('isya', 5);
    $table->primary(['city_code', 'date']);
});
```

> Ganti `ANGGATYASIA` dengan username GitHub kamu jika fork repo ini.
> Daftar kode kota: lihat [`api/cities.json`](../api/cities.json).
