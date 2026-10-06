#!/usr/bin/env python3
"""Build script untuk repo jadwal-sholat-indonesia.

Menghitung jadwal sholat harian per kota per tahun dengan metode
Kementerian Agama RI, lalu menghasilkan:
  api/   JSON statis (kota, index, jadwal per kota per tahun) — siap diakses via CDN
  data/  CSV jadwal per kota per tahun

Metode (terverifikasi dari materi hisab Kemenag):
  Subuh  = matahari -20° di bawah ufuk (+2 mnt ihtiyat)
  Isya   = matahari -18° di bawah ufuk (+2 mnt ihtiyat)
  Maghrib/Terbit = -1° (maghrib +2 mnt, terbit -2 mnt ihtiyat)
  Dzuhur = transit + 3 mnt ihtiyat
  Ashar  = Syafi'i (bayangan 1x) + 2 mnt ihtiyat
  Imsak  = Subuh - 10 menit
  Detik selalu dibulatkan ke atas menjadi menit (terbit: dibuang).

Sumber parameter: Bimas Islam Kemenag, materi Standar Baku Hisab Rukyat
(kemenag.go.id), kajian sudut fajar Kemenag (langit7.id).
"""
import csv
import json
import math
import os
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")

# --- Parameter metode Kemenag RI ---
FAJR_ANGLE = 20.0      # Subuh
ISHA_ANGLE = 18.0      # Isya
RISESET_ANGLE = 1.0    # Maghrib & Terbit
ASR_FACTOR = 1         # 1 = Syafi'i, 2 = Hanafi
IHTIYAT = {            # menit pengaman (ikhtiyat)
    "dzuhur": 3,
    "ashar": 2,
    "maghrib": 2,
    "isya": 2,
    "subuh": 2,
    "terbit": -2,
}
IMSAK_OFFSET = 10      # imsak = subuh - 10 menit
YEARS = [2026, 2027, 2028]
TZ_OFFSET = {"WIB": 7, "WITA": 8, "WIT": 9}


def julian_day(year, month, day):
    """Julian Day pada tengah hari UTC."""
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return (int(365.25 * (year + 4716)) + int(30.6001 * (month + 1))
            + day + b - 1524.5)


def sun_position(jd):
    """Deklinasi matahari (derajat) dan equation of time (jam)."""
    d = jd - 2451545.0
    g = math.radians(357.529 + 0.98560028 * d)
    q = 280.459 + 0.98564736 * d
    lon = math.radians(q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    e = math.radians(23.439 - 0.00000036 * d)
    ra = math.degrees(math.atan2(math.cos(e) * math.sin(lon), math.cos(lon))) / 15.0
    ra %= 24.0
    decl = math.degrees(math.asin(math.sin(e) * math.sin(lon)))
    eqt = q / 15.0 - ra
    eqt = ((eqt + 12.0) % 24.0) - 12.0
    return decl, eqt


def hour_angle(lat, decl, angle):
    """Sudut jam (jam) untuk ketinggian matahari `angle` (derajat)."""
    cos_h = ((math.sin(math.radians(angle))
              - math.sin(math.radians(lat)) * math.sin(math.radians(decl)))
             / (math.cos(math.radians(lat)) * math.cos(math.radians(decl))))
    cos_h = max(-1.0, min(1.0, cos_h))
    return math.degrees(math.acos(cos_h)) / 15.0


def asr_altitude(lat, decl, factor):
    """Ketinggian matahari saat Ashar (derajat, positif = di atas ufuk)."""
    return math.degrees(math.atan(
        1.0 / (factor + math.tan(math.radians(abs(lat - decl))))))


def day_times(lat, lng, tz, dt):
    """Kembalikan dict waktu sholat (menit sejak 00:00 lokal, float)."""
    jd = julian_day(dt.year, dt.month, dt.day) - tz / 24.0  # JD tengah hari lokal
    decl, eqt = sun_position(jd)
    transit = 12.0 + tz - lng / 15.0 - eqt  # jam lokal

    t = {}
    t["subuh"] = transit - hour_angle(lat, decl, -FAJR_ANGLE)
    t["terbit"] = transit - hour_angle(lat, decl, -RISESET_ANGLE)
    t["dzuhur"] = transit
    t["ashar"] = transit + hour_angle(lat, decl, asr_altitude(lat, decl, ASR_FACTOR))
    t["maghrib"] = transit + hour_angle(lat, decl, -RISESET_ANGLE)
    t["isya"] = transit + hour_angle(lat, decl, -ISHA_ANGLE)
    return {k: v * 60.0 for k, v in t.items()}


def fmt(minutes, ceil=True):
    """Format menit -> 'HH:MM'. Kemenag: detik dibulatkan ke atas (terbit: dibuang)."""
    m = math.ceil(minutes - 1e-9) if ceil else math.floor(minutes + 1e-9)
    return f"{int(m // 60):02d}:{int(m % 60):02d}"


def add_min(hhmm, delta):
    h, m = map(int, hhmm.split(":"))
    total = h * 60 + m + delta
    return f"{total // 60:02d}:{total % 60:02d}"


def build_city(city):
    lat, lng = city["lat"], city["lng"]
    tz = TZ_OFFSET[city["timezone"]]
    out = {}
    for year in YEARS:
        days = []
        d = date(year, 1, 1)
        while d.year == year:
            raw = day_times(lat, lng, tz, d)
            row = {"date": d.isoformat()}
            for key in ("subuh", "terbit", "dzuhur", "ashar", "maghrib", "isya"):
                v = fmt(raw[key] + IHTIYAT[key], ceil=(key != "terbit"))
                row[key] = v
            row["imsak"] = add_min(row["subuh"], -IMSAK_OFFSET)
            # urutan kolom: imsak dulu
            row = {"date": row["date"], "imsak": row["imsak"], "subuh": row["subuh"],
                   "terbit": row["terbit"], "dzuhur": row["dzuhur"],
                   "ashar": row["ashar"], "maghrib": row["maghrib"],
                   "isya": row["isya"]}
            days.append(row)
            d += timedelta(days=1)
        out[year] = days
    return out


def main():
    with open(os.path.join(SRC, "cities.json"), encoding="utf-8") as f:
        cities = json.load(f)

    total_json = 0
    for city in cities:
        code = city["code"]
        data = build_city(city)

        # JSON per tahun
        api_dir = os.path.join(ROOT, "api", "times", code)
        os.makedirs(api_dir, exist_ok=True)
        csv_dir = os.path.join(ROOT, "data", "times")
        os.makedirs(csv_dir, exist_ok=True)
        for year, days in data.items():
            with open(os.path.join(api_dir, f"{year}.json"), "w",
                      encoding="utf-8") as f:
                json.dump(days, f, ensure_ascii=False, separators=(",", ":"))
            total_json += 1
            with open(os.path.join(csv_dir, f"{code}_{year}.csv"), "w",
                      newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date", "imsak", "subuh",
                                                 "terbit", "dzuhur", "ashar",
                                                 "maghrib", "isya"])
                w.writeheader()
                w.writerows(days)

    # api/cities.json
    with open(os.path.join(ROOT, "api", "cities.json"), "w",
              encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=1)

    # api/index.json
    index = {
        "name": "jadwal-sholat-indonesia",
        "description": "Jadwal sholat harian per kota di Indonesia, metode Kemenag RI",
        "method": {
            "name": "Kementerian Agama RI",
            "fajr_angle": FAJR_ANGLE,
            "isha_angle": ISHA_ANGLE,
            "riseset_angle": RISESET_ANGLE,
            "asr": "Syafi'i",
            "ihtiyat_min": IHTIYAT,
            "imsak_offset_min": IMSAK_OFFSET,
        },
        "cities": len(cities),
        "years": YEARS,
        "days_per_city_year": 365,
        "source": "Perhitungan astronomis (hisab) mandiri berparameter Kemenag RI",
        "license": "MIT",
    }
    with open(os.path.join(ROOT, "api", "index.json"), "w",
              encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)

    print(f"kota: {len(cities)}, tahun: {YEARS}")
    print(f"file JSON jadwal: {total_json}, file CSV: {total_json}")
    print("index.json days_per_city_year: 365/366 mengikuti tahun kabisat")


if __name__ == "__main__":
    main()
