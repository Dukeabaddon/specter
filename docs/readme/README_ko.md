<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · **한국어** · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: 셀프 호스팅 Facebook 공개 페이지 모니터링 엔진

### 지속적인 Facebook 공개 페이지 모니터링을 위해 설계된 듀얼 모드 하이브리드 엔진.

**공개 페이지 포스트를 감지하고, 개인 계정 정지 위험 및 SaaS 비용 없이 밀리초 단위로 신속하게 추출합니다.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#specter-작동-원리)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#계정-불필요-아키텍처)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[빠른 시작](#빠른-시작) · [작동 원리](#specter-작동-원리) · [계정 불필요 아키텍처](#계정-불필요-아키텍처) · [CLI 사용법](#cli-명령어-안내)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> 2024년 말 Meta가 `mbasic.facebook.com` 서비스를 영구 중단하면서 기존 오픈소스 Facebook 스크래퍼의 95%가 작동을 멈췄습니다. **specter**는 **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** 기술을 통해 Meta의 최신 Comet React SPA와 Relay SSR 데이터 스트림을 역공학하여 만든 독립적인 오픈소스 모니터링 엔진입니다.

---

## 기존 스크래퍼가 작동하지 않는 이유

- **mbasic 서비스 중단:** 3,300개 이상의 스타를 보유한 오픈소스 파이썬 라이브러리 대부분이 mbasic 기반의 정적 HTML 파싱에 의존하고 있었습니다.
- **Comet React SPA 및 Relay 스트림:** 최신 Facebook은 난독화된 단일 페이지 애플리케이션(SPA) 구조로 전환되어 기존 CSS 셀렉터가 무력화되었습니다.
- **강력한 봇 방어 체계:** 브라우저 없이 보낸 일반 HTTP GET 요청은 즉각 `HTTP 400 Bad Request` 에러 또는 로그인 확인 페이지로 차단됩니다.
- **개인 계정 영구 정지 위험:** 개인 계정 쿠키(`c_user` / `xs`)를 사용해 자동화 요청을 보낼 경우 48시간 이내에 비정상 활동으로 감지되어 계정이 정지됩니다.
- **고비용 클라우드 SaaS:** Apify와 같은 서비스는 단순 주기적 스크래핑에도 매월 $50~$150 이상의 비용이 발생합니다.

---

## specter 작동 원리

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Tier 2 (스텔스 Playwright):** 익명 방문자 신분으로 실행되어 로그인 팝업을 자동으로 닫고, DOM 스크롤 잠금을 해제하며, 공개 방문자 세션 토큰(`datr`)을 획득합니다.
2. **Tier 1 (초고속 HTTP):** 획득한 쿠키를 재사용하여 브라우저 구동 없이 인라인 Relay SSR JSON 페이로드를 **약 500밀리초** 내에 ~25MB 메모리만 사용하여 추출합니다.
3. **자체 치유 사이클:** 쿠키가 만료되면 자동으로 Tier 2 Playwright로 복귀하여 세션 쿠키를 갱신합니다.

---

## 빠른 시작

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 단일 페이지 테스트 스크래핑
```bash
python main.py --page QCGov --limit 5
```

### 주기적 백그라운드 모니터링 실행
```bash
python main.py --page QCGov --monitor --interval 300
```
