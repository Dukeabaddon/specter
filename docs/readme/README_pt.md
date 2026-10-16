<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · **Português** · [Bahasa Indonesia](README_id.md)

# specter: Motor Auto-Hospedado de Monitoramento de Páginas Públicas do Facebook

### Motor híbrido de modo duplo projetado para monitoramento contínuo e resiliente de páginas públicas do Facebook.

**Detecte publicações públicas e extraia conteúdo em milissegundos sem risco de banimento, sem credenciais pessoais e sem custos de serviços SaaS.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#como-o-specter-funciona)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#arquitetura-anti-banimento)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[Início Rápido](#início-rápido) · [Como Funciona](#como-o-specter-funciona) · [Arquitetura Anti-Banimento](#arquitetura-anti-banimento) · [Guia CLI](#referência-cli)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> No final de 2024, a Meta desativou permanentemente o `mbasic.facebook.com`, quebrando 95% dos scrapers open-source existentes. O **specter** é uma solução independente desenvolvida com a metodologia **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** após engenharia reversa da SPA Comet React e dos fluxos Relay SSR da Meta.

---

## Por que scrapers tradicionais falham

- **Fim do mbasic:** As bibliotecas Python históricas dependiam inteiramente do HTML simples e estático da versão móvel básica.
- **Comet React SPA e Relay:** O Facebook agora roteia as páginas por uma aplicação de página única altamente ofuscada, inutilizando seletores CSS clássicos.
- **Bloqueios de bot instantâneos:** Requisições HTTP puras retornam `HTTP 400 Bad Request` ou são direcionadas para barreiras de login.
- **Suspensão de contas pessoais:** Fornecer cookies de contas privadas (`c_user` / `xs`) ativa sistemas de segurança que banem a conta em menos de 48 horas.
- **Cobranças de SaaS elevadas:** Plataformas como a Apify cobram entre US$ 50 e US$ 150 por mês para tarefas simples e periódicas de coleta.

---

## Como o specter Funciona

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Nível 2 (Playwright Furtivo):** Executa brevemente como visitante anônimo, remove o diálogo de bloqueio de login, libera a rolagem do DOM e captura os tokens públicos de visitante (`datr`).
2. **Nível 1 (HTTP Ultrarrápido):** Reutiliza esses tokens para buscar o feed diretamente via HTTP, analisando os dados do Relay SSR em **~500 ms** com apenas ~25MB de memória RAM.
3. **Ciclo de auto-recuperação:** Se os tokens expirarem, o sistema retorna automaticamente ao Playwright para renovar a sessão de forma transparente.

---

## Início Rápido

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Teste de coleta imediata
```bash
python main.py --page QCGov --limit 5
```

### Executar monitoramento contínuo
```bash
python main.py --page QCGov --monitor --interval 300
```
