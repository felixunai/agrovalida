# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgroValida is a Django 4.2 SaaS application for controlling expiration dates of agricultural defensive lots, with NF-e (XML/PDF) invoice reading. Language: Portuguese (pt-br). Timezone: America/Sao_Paulo.

## Stack

- **Backend**: Python 3.11+ / Django 4.2
- **Database**: PostgreSQL
- **Frontend**: Django templates + Bootstrap 5 (CDN)
- **Config**: `django-environ` (`.env` file)

## Static Files

Custom CSS lives in `static/css/agrovalida.css`. Both settings files declare `STATICFILES_DIRS = [BASE_DIR / 'static']`. Templates load it with `{% load static %}` + `<link rel="stylesheet" href="{% static 'css/agrovalida.css' %}">`. The landing page (`landing.html`) does **not** extend `base.html` — it has its own full HTML structure and must link the CSS directly.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then edit with DB credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Common Commands

```bash
python manage.py makemigrations   # after model changes
python manage.py migrate
python manage.py runserver
python manage.py createadmin      # custom command to create admin user
```

No test suite or linter is configured yet.

## Settings Structure

Settings are split into `agrovalida/settings/dev.py` (imported by default) and `agrovalida/settings/production.py`. The legacy `agrovalida/settings.py` also exists. Key setting: `ALERTA_DIAS_VENCIMENTO = 90` (days before expiry to trigger "vencendo" alert).

## URL Routing

- `/` — Landing page (public)
- `/painel/` — Dashboard (authenticated)
- `/produtos/` — Defensivos CRUD
- `/lotes/` — Lotes CRUD
- `/notas/` — NF-e list and upload
- `/accounts/` — Auth + user management

## App Architecture

| App | Purpose | Key Models |
|-----|---------|------------|
| `defensivos` | Agricultural product registry | `Defensivo` (nome_comercial, classe, registro_mapa, fabricante, ativo, cadastrado_por) |
| `lotes` | Lot/batch expiry tracking | `Lote` (defensivo FK, numero_lote, data_validade, quantidade, unidade, cadastrado_por) |
| `notas` | NF-e upload and parsing | `NotaFiscal`, `ItemNotaFiscal` |
| `accounts` | Auth, plans, user management | `UserProfile`, `Plano` |
| `dashboard` | Summary views and reports | No models |

## Key Design Patterns

**Expiry status is computed, not stored.** `Lote.status_vencimento` and `Lote.dias_para_vencer` are `@property` methods comparing `data_validade` against today. Never add a DB field for this.

**Soft-delete for Defensivos, hard-delete for Lotes.** Setting `ativo=False` on a `Defensivo` deactivates it; deleting a `Lote` removes it from the DB.

**Multi-tenant data isolation via `cadastrado_por`.** Every `Defensivo`, `Lote`, and `NotaFiscal` has a `cadastrado_por` FK to `AUTH_USER_MODEL`. Views must filter by `request.user` to scope data per user.

**Plan-based access control** is implemented in three layers:
1. `accounts/middleware.py` — `PlanMiddleware` attaches `request.plan_limits` and `request.is_pro` on every request
2. `accounts/decorators.py` — `@plano_requerido` blocks non-Pro users; `@limite_alcancado(tipo)` enforces per-resource creation limits
3. `accounts/context_processors.py` — exposes plan info to all templates

Plan tiers: **Gratuito** (5 defensivos, 10 lotes, 3 notas, no reports) and **Profissional** (unlimited). Superusers always get Pro access.

**NF-e parsing** lives entirely in `notas/services.py`:
- `parse_nfe_xml()` — uses `lxml` with namespace `http://www.portalfiscal.inf.br/nfe`
- `parse_nfe_pdf_text()` — regex-based extraction from `pdfplumber` text output
- `processar_nota()` — orchestrates file type detection → parsing → `ItemNotaFiscal` creation
- `importar_nota_automatico()` — converts `ItemNotaFiscal` rows into `Defensivo` + `Lote` records, inferring class and unit from description text

**`infAdProd` field** in NF-e XML items contains free-text lot/validity info; `_parse_inf_ad_prod()` extracts it with regex patterns like `Lote: X Val.: DD/MM/YYYY Fab.: DD/MM/YYYY`.
