<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · **Español** · [Français](README_fr.md) · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: Motor Autoalojado de Monitoreo para Páginas Públicas de Facebook

### Motor híbrido de modo dual para la monitorización continua y resiliente de páginas públicas de Facebook.

**Detecta publicaciones públicas y extráelas en submilisegundos sin riesgo de baneo, sin cuentas personales y sin pagar costosos servicios SaaS.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#cómo-funciona-specter)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#arquitectura-antibloqueo)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[Inicio Rápido](#inicio-rápido) · [Cómo Funciona](#cómo-funciona-specter) · [Arquitectura Antibloqueo](#arquitectura-antibloqueo) · [Guía CLI](#referencia-cli)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> A finales de 2024, Meta descontinuó de forma permanente `mbasic.facebook.com`, inhabilitando el 95% de los scrapers de código abierto existentes. **specter** es un motor independiente desarrollado mediante la metodología **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** tras analizar a fondo la SPA Comet React de Meta y los flujos Relay SSR.

---

## Por qué fallan los scrapers tradicionales

- **Cierre definitivo de mbasic:** Librerías con miles de estrellas en GitHub dependían por completo de la estructura HTML estática de mbasic.
- **Comet React SPA y Relay:** Facebook procesa ahora todo su tráfico a través de una aplicación de página única ofuscada, dejando obsoletos los selectores CSS clásicos.
- **Muros antibot inmediatos:** Peticiones HTTP estándar devuelven `HTTP 400 Bad Request` o redirigen a ventanas de verificación y login.
- **Riesgo de bloqueo de cuentas personales:** Usar cookies autenticadas personales (`c_user` / `xs`) provoca la suspensión irreversible de la cuenta en menos de 48 horas.
- **Suscripciones SaaS costosas:** Proveedores en la nube como Apify cobran entre 50 y 150 dólares mensuales por tareas básicas programadas.

---

## Cómo Funciona specter

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Nivel 2 (Playwright Sigiloso):** Se ejecuta puntualmente como visitante anónimo, suprime el diálogo emergente de inicio de sesión, desbloquea el scroll del DOM y captura tokens públicos (`datr`).
2. **Nivel 1 (HTTP Ultrarrápido):** Reutiliza dichos tokens para consultar directamente las publicaciones mediante HTTP, extrayendo el JSON Relay SSR en **~500 ms** con apenas ~25MB de memoria RAM.
3. **Autocorrección integrada:** Si los tokens caducan, el sistema vuelve automáticamente a Playwright para renovar la sesión sin intervención humana.

---

## Inicio Rápido

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Prueba de extracción inmediata
```bash
python main.py --page QCGov --limit 5
```

### Ejecutar demonio de monitoreo continuo
```bash
python main.py --page QCGov --monitor --interval 300
```
