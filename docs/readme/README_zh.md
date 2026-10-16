<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · **简体中文** · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: 自托管 Facebook 公开主页采集与监控引擎

### 专为持续监控 Facebook 公开主页打造的现代化双模式采集器。

**快速提取公开帖子内容。无需账号登录，毫秒级响应，告别封禁与昂贵的 SaaS 服务。**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/架构-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#核心架构)
[![免账号](https://img.shields.io/badge/认证-完全免登录-success.svg?style=flat-square)](#防封禁机制)
[![License: MIT](https://img.shields.io/badge/许可证-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

[快速开始](#快速开始) · [工作原理](#工作原理) · [防封禁架构](#防封禁架构) · [命令行指南](#命令行指南)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> 2024 年末，Meta 永久关闭了 `mbasic.facebook.com`，导致 GitHub 上 95% 的传统开源采集器失效。**specter** 是使用 **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** 逆向工程 Meta 现代化 Comet React SPA 与 Relay SSR 数据流构建的全新自托管解决方案。

---

## 为什么传统采集器全部失效？

- **mbasic 永久下线:** 绝大部分 Python 库依赖该入口获取静态 HTML。
- **Comet React 单页应用:** Facebook 全面转为动态 Relay 数据流渲染。
- **严格的反爬质检:** 裸 HTTP GET 请求直接返回 `HTTP 400 Bad Request` 或强制定向至登录拦截页。
- **个人账号易被封禁:** 一旦使用个人 Cookie (`c_user` / `xs`)，48 小时内极易触发风控导致账号冻结。

---

## specter 的双模式工作原理

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (隐身 Playwright 浏览器):** 以匿名访客身份运行，自动清除遮罩登录弹窗，解除 DOM 滚动限制，并捕获公共访客凭证 (`datr`)。
2. **Tier 1 (极速 HTTP 客户端):** 复用访客 Cookie，无需启动浏览器即可在 **~500 毫秒** 内直接提取页面内嵌的 Relay SSR JSON 数据，仅消耗约 25MB 内存。
3. **自我修复闭环:** 当凭证过期或被拦截时，系统无缝回退至 Playwright 重新刷新 Cookie。

---

## 快速开始

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

抓取任意公开主页（例如 Quezon City Government）：
```bash
python3 main.py --page QCGov --limit 3
```
