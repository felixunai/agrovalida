# AgroValida — Agent Instructions

## Project Overview
Sistema de controle de vencimento de lotes para defensivos agrícolas, com leitura de NF-e (XML/PDF).

## Stack
- **Backend**: Python 3.11+ / Django 4.2
- **Database**: PostgreSQL
- **Frontend**: Django templates + Bootstrap 5 (CDN)
- **Env**: django-environ (`.env` file, see `.env.example`)

## Setup & Run
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # then edit .env with your DB credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Apps & Structure
| App | Purpose | Key Models |
|-----|---------|-------------|
| `defensivos` | Cadastro de defensivos agrícolas | `Defensivo` (nome, classe, registro MAPA, princípio ativo) |
| `lotes` | Controle de lotes e vencimento | `Lote` (nº lote, validade, quantidade, status calculado) |
| `notas` | Upload e parsing de NF-e | `NotaFiscal`, `ItemNotaFiscal` |
| `dashboard` | Painel, alertas, relatórios | No models — queries across `lotes` and `defensivos` |

## Key Design Decisions
- **Status de vencimento** is a computed property on `Lote` (`status_vencimento`, `dias_para_vencer`), not a DB field. Controlled by `ALERTA_DIAS_VENCIMENTO` setting (default 90 days).
- **NF-e parsing**: XML uses `lxml` with namespace-aware selectors. PDF uses `pdfplumber`. See `notas/services.py`.
- **Deleting a Defensivo** soft-deletes (sets `ativo=False`); deleting a Lote hard-deletes.
- All views require `@login_required`.

## Commands
```bash
python manage.py makemigrations          # after model changes
python manage.py migrate                # apply migrations
python manage.py runserver              # dev server
python manage.py createsuperuser        # admin user
```
No separate lint/typecheck/test commands yet.

## URL Patterns
- `/` — Dashboard (summary, alerts)
- `/defensivos/` — CRUD defensivos
- `/lotes/` — CRUD lotes (filterable by status)
- `/notas/` — NF list, `/notas/upload/` — XML/PDF upload
- `/notas/item/<id>/importar/` — convert NF item into a Lote
- `/relatorio/vencimento/` — filterable report
- `/admin/` — Django admin

## Environment Variables
See `.env.example`. Key ones: `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `SECRET_KEY`.

## Localization
- Language: `pt-br`, Timezone: `America/Sao_Paulo`
- All UI labels and choices are in Portuguese.