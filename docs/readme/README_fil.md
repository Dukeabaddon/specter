<div align="center">

[English](../../README.md) · **Filipino** · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: Self-Hosted Facebook Public Page Scraper

### Mabilis at matatag na dual-mode engine para sa tuloy-tuloy na pag-monitor ng mga pampublikong Facebook page.

**Tingnan ang pinakabagong post. Kunin ang datos sa loob ng kalahating segundo nang walang ban, walang bayad sa SaaS, at hindi kailangan ng personal na Facebook account.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Arkitektura-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#arkitektura)
[![Walang Account](https://img.shields.io/badge/Auth-Hindi%20Kailangan%20ng%20Account-success.svg?style=flat-square)](#anti-ban)
[![License: MIT](https://img.shields.io/badge/Lisensya-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

[Mabilisang Pagsisimula](#mabilisang-pagsisimula) · [Paano Gumagana](#paano-gumagana-ang-specter) · [Anti-Ban Arkitektura](#anti-ban-arkitektura) · [CLI Reference](#cli-reference)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> Noong huling bahagi ng 2024, tuluyang tinanggal ng Meta ang `mbasic.facebook.com`. Dahil dito, halos lahat ng lumang open-source scrapers sa GitHub ay nasira. Ang **specter** ay binuo gamit ang **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** upang ma-reverse engineer ang modernong Comet React SPA at Relay SSR data stream ng Meta.

---

## Bakit Sira ang Ibang Scrapers?

- **Pagsasara ng mbasic:** Lahat ng lumang Python scrapers ay nakadepende sa mbasic HTML.
- **Comet React SPA:** Puro dynamic JavaScript at Relay streams na ang ginagamit ng Facebook ngayon.
- **Anti-Bot Checkpoints:** Kapag gumamit ka ng ordinaryong HTTP GET, agad kang haharangin ng `HTTP 400 Bad Request` o login checkpoint.
- **Nababang Personal Accounts:** Kapag ginamit mo ang sarili mong cookies (`c_user` / `xs`), mabilis na madi-disable ang iyong personal na account.

Ang **specter** ay libre, self-hosted, at dinisenyo para gumana nang walang personal na account.

---

## Paano Gumagana ang specter?

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

Gumagamit ang specter ng **Dual-Mode Symbiotic Pipeline**:

1. **Tier 2 (Stealth Playwright):** Tumatakbo nang minsan lang bilang anonymous visitor. Tinatanggal nito ang "Mag-log in" popup, ini-unlock ang scrolling, at kinukuha ang public visitor session tokens (`datr`).
2. **Tier 1 (Mabilis na HTTP):** Ginagamit ang visitor tokens para kumuha ng feed gamit ang purong HTTP. Binabasa nito ang server-rendered Relay SSR JSON payloads sa loob ng **~500 milliseconds** gamit lamang ang ~25MB ng RAM.
3. **Awtomatikong Pag-recover:** Kapag nagbago ang tokens ng Meta, kusa itong babalik sa Playwright para mag-refresh ng cookies.

---

## Mabilisang Pagsisimula

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

Subukan sa Quezon City Government page:
```bash
python3 main.py --page QCGov --limit 3
```

---

## Anti-Ban Arkitektura

- **Walang Login:** 100% anonymous public session. Hindi kailanman manganganib ang iyong account.
- **Magaan sa Resource:** Hindi nagpapatakbo ng mabigat na browser 24/7.
- **SQLite Deduplication:** May kasamang SHA-256 fingerprinting para maiwasan ang paulit-ulit na alerts.
