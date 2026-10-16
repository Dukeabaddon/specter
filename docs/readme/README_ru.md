<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · **Русский** · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: Автономный движок мониторинга публичных страниц Facebook

### Отказоустойчивый двухрежимный гибридный движок для непрерывного отслеживания публичных страниц Facebook.

**Мгновенно извлекайте публикации из открытых страниц за доли секунды — без риска блокировки аккаунтов, без необходимости входа и без платных SaaS-сервисов.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#принцип-работы-specter)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#архитектура-защиты-от-блокировок)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[Быстрый старт](#быстрый-старт) · [Принцип работы](#принцип-работы-specter) · [Защита от блокировок](#архитектура-защиты-от-блокировок) · [Справочник CLI](#руководство-по-cli)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> В конце 2024 года Meta окончательно отключила интерфейс `mbasic.facebook.com`, что привело к отказу 95% существующих скраперов с открытым исходным кодом. **specter** — независимый автономный инструмент, созданный по методологии **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** для прямого анализа современной архитектуры Comet React SPA и потоков Relay SSR.

---

## Почему традиционные скраперы перестали работать

- **Отключение mbasic:** Большинство открытых библиотек на Python полагались на простой статичный HTML базовой мобильной версии.
- **Comet React SPA и Relay:** Современный Facebook полностью перешел на сложное динамическое SPA, сделав классические CSS-селекторы неприменимыми.
- **Системы защиты от ботов:** Стандартные HTTP GET запросы мгновенно блокируются с кодом `HTTP 400 Bad Request` или перенаправляются на форму входа.
- **Блокировка личных аккаунтов:** Использование персональных сессионных cookie (`c_user` / `xs`) в течение 48 часов приводит к полной блокировке профиля.
- **Дорогие облачные платформы:** Сервисы вроде Apify требуют от 50 до 150 долларов в месяц за выполнение регулярных задач сбора данных.

---

## Принцип работы specter

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (Stealth Playwright):** Запускается однократно в качестве анонимного гостя, удаляет модальное окно авторизации, разблокирует прокрутку DOM и сохраняет гостевые токены (`datr`).
2. **Tier 1 (Сверхбыстрый HTTP):** Повторно использует гостевые cookie для мгновенного сбора постов через чистый HTTP, парся Relay SSR JSON всего за **~500 мс** при потреблении около 25 МБ ОЗУ.
3. **Автономное самовосстановление:** При истечении срока действия токенов система автоматически переключается на Playwright для обновления cookie-файлов.

---

## Быстрый старт

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Тестовый сбор страницы
```bash
python main.py --page QCGov --limit 5
```

### Запуск постоянного мониторинга
```bash
python main.py --page QCGov --monitor --interval 300
```
