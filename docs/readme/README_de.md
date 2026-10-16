<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · **Deutsch** · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: Self-Hosted Monitoring-Engine für öffentliche Facebook-Seiten

### Eine widerstandsfähige Dual-Mode-Engine zur kontinuierlichen Überwachung öffentlicher Facebook-Seiten.

**Erkennt neue Beiträge auf öffentlichen Seiten und extrahiert sie in Sekundenbruchteilen – ohne Account-Sperren, ohne persönliche Zugangsdaten und ohne teure SaaS-Kosten.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#wie-specter-funktioniert)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#anti-ban-architektur)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[Schnellstart](#schnellstart) · [Funktionsweise](#wie-specter-funktioniert) · [Anti-Ban-Architektur](#anti-ban-architektur) · [CLI-Referenz](#cli-befehlsreferenz)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> Ende 2024 hat Meta `mbasic.facebook.com` endgültig eingestellt. Dadurch wurden rund 95% aller bisherigen Open-Source-Scraper unbrauchbar. **specter** ist eine unabhängige Lösung, die mit der **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** Methode entwickelt wurde, um Metas moderne Comet React SPA und Relay SSR-Datenströme zuverlässig zu verarbeiten.

---

## Warum herkömmliche Scraper fehlschlagen

- **Abschaltung von mbasic:** Bisherige Python-Scraper verließen sich vollständig auf das einfache, statische HTML der mobilen Basisversion.
- **Comet React SPA und Relay:** Facebook nutzt nun eine hochgradig verschleierte Single-Page-Anwendung, wodurch statische CSS-Selektoren nutzlos geworden sind.
- **Sofortige Bot-Blockaden:** Unveränderte HTTP-Anfragen werden mit `HTTP 400 Bad Request` abgewiesen oder auf Anmeldeseiten umgeleitet.
- **Sperrung persönlicher Konten:** Das Einbinden privater Cookies (`c_user` / `xs`) führt innerhalb von 48 Stunden zur Deaktivierung des Benutzerkontos.
- **Hohe SaaS-Gebühren:** Cloud-Dienste wie Apify verlangen 50 bis 150 Dollar pro Monat für automatisierte Überwachungsaufgaben.

---

## Wie specter funktioniert

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (Stealth Playwright):** Läuft einmalig als anonymer Besucher, schließt störende Login-Popups, entsperrt das Scrollen im DOM und sichert öffentliche Besucher-Cookies (`datr`).
2. **Tier 1 (Fast HTTP):** Verwendet diese Sitzungsdaten wieder, um Daten per reinem HTTP in **~500 ms** und mit nur ca. 25 MB RAM direkt aus dem Relay SSR JSON-Stream zu laden.
3. **Selbstheilender Zyklus:** Bei ungültig gewordenen Tokens schaltet die Engine automatisch auf Playwright zurück, um neue Cookies zu beschaffen.

---

## Schnellstart

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Einzelabfrage testen
```bash
python main.py --page QCGov --limit 5
```

### Dauerhafte Überwachung starten
```bash
python main.py --page QCGov --monitor --interval 300
```
