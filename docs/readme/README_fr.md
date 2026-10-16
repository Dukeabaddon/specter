<div align="center">

[English](../../README.md) · [Filipino](README_fil.md) · [简体中文](README_zh.md) · [繁體中文](README_zh-TW.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Español](README_es.md) · **Français** · [Deutsch](README_de.md) · [Русский](README_ru.md) · [Português](README_pt.md) · [Bahasa Indonesia](README_id.md)

# specter: Moteur d'Extraction Auto-Hébergé pour Pages Publiques Facebook

### Moteur hybride bimode conçu pour la surveillance continue et résiliente des pages Facebook publiques.

**Détectez les publications publiques et extrayez-les en quelques millisecondes, sans compte personnel, sans risque de bannissement et sans abonnement SaaS.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Mode%20Hybrid-orange.svg?style=flat-square)](#fonctionnement-de-specter)
[![Zero Credentials](https://img.shields.io/badge/Auth-Zero%20Account%20Required-success.svg?style=flat-square)](#architecture-anti-bannissement)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](../../LICENSE)

<br/>

[Démarrage Rapide](#démarrage-rapide) · [Fonctionnement](#fonctionnement-de-specter) · [Architecture Anti-Bannissement](#architecture-anti-bannissement) · [Guide CLI](#référence-cli)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="../../assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px;" />

</div>

---

> [!IMPORTANT]
> Fin 2024, Meta a définitivement supprimé `mbasic.facebook.com`, rendant inopérants 95% des scrapers open-source historiques. **specter** est un moteur indépendant créé via la méthodologie **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** après rétro-ingénierie de la SPA Comet React et des flux Relay SSR de Meta.

---

## Pourquoi les scrapers classiques échouent

- **Disparition de mbasic:** Les bibliothèques Python historiques s'appuyaient presque exclusivement sur le HTML statique de mbasic.
- **SPA Comet React et Relay:** Facebook a migré l'ensemble de son interface vers une application monopage complexe qui neutralise les sélecteurs CSS conventionnels.
- **Blocages antibot immédiats:** Une simple requête HTTP directe déclenche désormais une erreur `HTTP 400 Bad Request` ou une redirection de connexion.
- **Bannissement des comptes personnels:** Utiliser ses propres cookies de session (`c_user` / `xs`) entraîne une suspension irréversible du compte en moins de 48 heures.
- **Tarifs SaaS exorbitants:** Les solutions cloud comme Apify facturent entre 50$ et 150$/mois pour un suivi régulier de pages.

---

## Fonctionnement de specter

<p align="center">
  <img src="../../assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</p>

1. **Niveau 2 (Playwright Furtif):** S'exécute ponctuellement en tant que visiteur anonyme, supprime la boîte de dialogue de connexion, déverrouille le défilement du DOM et capture les jetons de visiteur public (`datr`).
2. **Niveau 1 (HTTP Rapide):** Réutilise ces jetons pour interroger directement le flux en HTTP et extrait les données Relay SSR en **~500 ms** avec seulement ~25 Mo de mémoire vive.
3. **Boucle d'auto-réparation:** Dès que les jetons expirent, le moteur bascule automatiquement vers Playwright pour actualiser les cookies de façon transparente.

---

## Démarrage Rapide

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Exécution d'un test direct
```bash
python main.py --page QCGov --limit 5
```

### Lancement du service de surveillance
```bash
python main.py --page QCGov --monitor --interval 300
```
