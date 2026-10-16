<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · **日本語** · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: セルフホスト型 Facebook 公開ページ監視エンジン

### Facebook 公開ページの常時監視を実現する、高耐障害デュアルモードエンジン。

**公開ページの投稿を検知し、アカウント停止リスクや SaaS 費用なしでミリ秒単位で高速抽出。**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#specter-の仕組み)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#アカウント不要設計)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[クイックスタート](#クイックスタート) · [仕組み](#specter-の仕組み) · [アカウント不要設計](#アカウント不要設計) · [CLI ガイド](#cli-リファレンス)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> 2024 年末、Meta は `mbasic.facebook.com` を恒久的に廃止し、従来のオープンソース Facebook スクレイパーの 95% が動作不能になりました。**specter** は、**[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** 手法により Meta の最新 Comet React SPA および Relay SSR データストリームをリバースエンジニアリングして構築された、セルフホスト型の監視エンジンです。

---

## 従来のスクレイパーが停止した理由

- **mbasic の廃止:** 3,000 以上のスターを持つ代表的なライブラリ群を含め、ほぼすべてのスクレイパーが mbasic の静的 HTML に依存していました。
- **Comet React SPA と Relay:** Facebook は最新の動的 React SPA に移行し、従来の CSS セレクターは完全に無効化されました。
- **ボット対策検問:** 通常の HTTP リクエストは `HTTP 400 Bad Request` またはログイン要求モーダルで遮断されます。
- **個人アカウントの凍結:** 個人の Cookie (`c_user` / `xs`) を使用すると、48 時間以内に検知されアカウントが停止されます。
- **高額な SaaS 費用:** Apify などの商用クラウドスクレイパーは月額 $50〜$150 以上の費用が発生します。

---

## specter の仕組み

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (ステルス Playwright):** 匿名ビジターとして実行され、ログイン要求ダイアログを自動消去し、DOM スクロール制限を解除して公開ビジター認証トークン (`datr`) を取得します。
2. **Tier 1 (高速 HTTP クライアント):** 取得した Cookie を再利用し、ブラウザを起動することなくインラインの Relay SSR JSON ペイロードを **約 500 ミリ秒**・メモリ消費約 25MB で直接抽出します。
3. **自動復旧サイクル:** トークンが期限切れになった場合、自動的に Playwright へフォールバックして Cookie を更新します。

---

## クイックスタート

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### ライブテスト実行
```bash
python main.py --page QCGov --limit 5
```

### 常駐監視モードの起動
```bash
python main.py --page QCGov --monitor --interval 300
```
