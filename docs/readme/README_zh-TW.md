<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · **繁體中文** · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: 自託管 Facebook 公開專頁監控引擎

### 專為持續監控 Facebook 公開專頁打造的高可用雙模式引擎。

**即時偵測公開專頁動態，亞秒級快速提取，無需個人帳號，零封號風險，無需支付昂貴 SaaS 服務費用。**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#specter-工作原理)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#防封禁架構)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[快速開始](#快速開始) · [工作原理](#specter-工作原理) · [防封禁架構](#防封禁架構) · [命令列指南](#cli-命令列指南) · [Python API](#python-api-呼叫)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> 2024 年底，Meta 永久下線了 `mbasic.facebook.com`，導致歷史上 95% 的開源 Facebook 爬蟲全面失效。**specter** 是使用 **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** 技術逆向 Meta 現代 Comet React 單頁應用與 Relay SSR 資料流後構建的獨立自託管監控引擎。

---

## 為什麼傳統爬蟲全部失效？

- **mbasic 永久下線:** 絕大多數開源 Python 爬蟲（例如擁有 3.3k 星標的 `kevinzg/facebook-scraper`、`facebook2rss` 等）完全依賴 mbasic 靜態 HTML。
- **Comet React 單頁架構與 Relay:** 現代 Facebook 全面轉向複雜混淆的 React SPA 架構，傳統 CSS 選擇器已徹底無效。
- **嚴格的請求檢驗:** 普通 HTTP 請求會直接遭遇 `HTTP 400 Bad Request` 或被重定向至強制登入頁面。
- **個人帳號封禁風險:** 使用個人 Cookie (`c_user` / `xs`) 進行自動化請求，往往在 48 小時內觸發風控導致帳號被鎖。
- **商業 SaaS 成本高昂:** Apify 等雲端爬蟲平台的定時任務收費高達每月 $50 至 $150 美元。

---

## specter 工作原理

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (隱身 Playwright 瀏覽器):** 以匿名訪客身分啟動，自動移除阻擋互動的登入彈窗，解除 DOM 滾動限制，並取得公開訪客憑證 (`datr`)。
2. **Tier 1 (極速 HTTP 用戶端):** 重複使用訪客 Cookie，無需啟動瀏覽器即可在 **約 500 毫秒** 內直接解析頁面內嵌的 Relay SSR JSON 資料流，記憶體佔用僅約 25MB。
3. **自我修復閉環:** 當憑證失效或遭遇 Meta 邊緣規則更新時，系統無縫切換回 Playwright 自動刷新 Cookie。

---

## 快速開始

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 即時測試抓取
```bash
python main.py --page QCGov --limit 5
```

### 啟動守護監控服務
```bash
python main.py --page QCGov --monitor --interval 300
```
