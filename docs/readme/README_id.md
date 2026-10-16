<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · **Bahasa Indonesia**

# specter: Mesin Pemantau Halaman Publik Facebook Mandiri (Self-Hosted)

### Mesin hibrida mode ganda yang tangguh untuk pemantauan berkelanjutan halaman publik Facebook.

**Deteksi postingan publik dan ekstrak konten dalam hitungan milidetik tanpa risiko pemblokiran akun, tanpa akun pribadi, dan tanpa biaya langganan SaaS.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#cara-kerja-specter)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#arsitektur-anti-blokir)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[Mulai Cepat](#mulai-cepat) · [Cara Kerja](#cara-kerja-specter) · [Arsitektur Anti-Blokir](#arsitektur-anti-blokir) · [Panduan CLI](#panduan-cli)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> Pada akhir 2024, Meta secara permanen menghentikan `mbasic.facebook.com`, menyebabkan 95% scraper open-source lama tidak dapat digunakan lagi. **specter** adalah mesin mandiri yang dibangun dengan metodologi **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** setelah merekayasa balik Comet React SPA dan aliran Relay SSR milik Meta.

---

## Mengapa Scraper Tradisional Gagal

- **Penghentian mbasic:** Scraper Python lama sangat bergantung pada HTML statis mbasic yang kini telah dihapus sepenuhnya.
- **Comet React SPA dan Relay:** Facebook memproses semua antarmuka web melalui aplikasi satu halaman dinamis, membuat selektor CSS lama usang.
- **Pencegahan Bot Ketat:** Permintaan HTTP biasa langsung ditolak dengan status `HTTP 400 Bad Request` atau diarahkan ke halaman login.
- **Pemblokiran Akun Pribadi:** Menggunakan cookie autentikasi pribadi (`c_user` / `xs`) memicu sistem keamanan yang membekukan akun dalam 48 jam.
- **Biaya SaaS Mahal:** Layanan scraper awan komersial seperti Apify memungut biaya $50 hingga $150 per bulan untuk pemantauan terjadwal sederhana.

---

## Cara Kerja specter

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (Stealth Playwright):** Berjalan sekali sebagai pengunjung anonim, menutup dialog login yang menghalangi, membuka kunci scroll DOM, dan menyimpan token pengunjung publik (`datr`).
2. **Tier 1 (HTTP Super Cepat):** Menggunakan kembali token tersebut untuk mengambil data via HTTP murni, memproses Relay SSR JSON dalam waktu **~500 ms** dengan konsumsi memori hanya ~25MB.
3. **Pemulihan Otomatis:** Jika token kedaluwarsa, sistem otomatis kembali ke Playwright untuk memperbarui cookie tanpa henti.

---

## Mulai Cepat

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Jalankan Uji Scrape Langsung
```bash
python main.py --page QCGov --limit 5
```

### Jalankan Pemantauan Terus-menerus
```bash
python main.py --page QCGov --monitor --interval 300
```
