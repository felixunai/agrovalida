---
name: AgroValida project context
description: Stack, purpose, key decisions, and recent work on the AgroValida SaaS
type: project
---

AgroValida is a Django 4.2 SaaS for controlling expiry dates of agricultural defensive lots, with NF-e XML/PDF import.

**Why:** Built for agronomists/producers who lose track of lot expiry dates. Multi-tenant (per-user data via `cadastrado_por`). Two plans: Gratuito (free, limited) and Profissional.

**Recent work (2026-04-13):**
- Created `static/css/agrovalida.css` — full CSS overhaul with CSS variables, Inter font, polished navbar/cards/tables/badges
- Added `STATICFILES_DIRS = [BASE_DIR / 'static']` to both settings files
- Redesigned `landing.html` (standalone page, doesn't extend base.html) — new hero, features, how-it-works, pricing, CTA sections
- Improved `base.html` — active nav link highlighting, plan chip, footer with `{% now "Y" %}`
- Improved `notas/services.py` PDF parsing — added `_extract_pdf_data()` for single-pass text+tables, `_parse_nfe_pdf_tables()` as primary strategy using pdfplumber table extraction, text-based as fallback; `_parse_data()` now handles MM/YYYY format

**How to apply:** When touching UI, use CSS variables from `agrovalida.css` (--av-green-700, --av-shadow, etc.). When touching PDF parsing, prefer table-based extraction first — text extraction is the fallback.
