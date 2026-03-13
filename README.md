# Backstage API

> **Stack:** FastAPI · MongoDB (motor/async) · SQLite via SQLAlchemy (async) · Pydantic v2

Painel de gerenciamento de **teatros**, **performances** e **sessões** com suporte a upload de mídia e mapa geoespacial.

---

## Sumário

- [Visão geral da arquitetura](#visão-geral-da-arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação rápida](#instalação-rápida)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Banco de dados](#banco-de-dados)
- [Seed](#seed)
- [Rodando a API](#rodando-a-api)
- [Endpoints](#endpoints)
- [Modelos de dados](#modelos-de-dados)
- [Upload de mídia](#upload-de-mídia)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Troubleshooting](#troubleshooting)

---

## Visão geral da arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (app/)                        │
│                                                         │
│  /theaters  →  TheatersRepo  →  SQLite (SQLAlchemy)     │
│  /performances → PerformancesRepo → MongoDB             │
│  /sessions  →  SessionsRepo  →  MongoDB                 │
│  /media     →  static/uploads/<category>/               │
│  /utils/address → geocoding / CEP lookup                │
└─────────────────────────────────────────────────────────┘
```

> **Decisão de design:** Teatros usam SQLite (dado estruturado, relacional, estável).
> Performances e Sessões usam MongoDB (schema flexível, evolui frequentemente).

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|---|---|
| Python | 3.11+ |
| MongoDB | 7+ (local ou Docker) |
| uv *(opcional, recomendado)* | qualquer |

---

## Instalação rápida

### Windows (PowerShell)

```powershell
# Com Docker (sobe o MongoDB automaticamente)
.\scripts\setup.ps1 -Docker

# Sem Docker (MongoDB já rodando localmente)
.\scripts\setup.ps1
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m seeds.seed
```

---

## Variáveis de ambiente

Copie `.env.example` e ajuste:

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017` | URI de conexão do MongoDB |
| `MONGODB_DB` | `theatersdb` | Nome do banco MongoDB |
| `DATABASE_URL` | `sqlite+aiosqlite:///./backstage.db` | URI do banco SQL (teatros) |
| `APP_HOST` | `127.0.0.1` | Host do servidor |
| `APP_PORT` | `8000` | Porta do servidor |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Origens permitidas (separadas por vírgula) |

---

## Banco de dados

### MongoDB (Performances + Sessões)

Suba via Docker:

```bash
docker run -d --name theaters-mongo -p 27017:27017 mongo:7
```

Ou use uma instância local / Atlas. Configure `MONGODB_URI` no `.env`.

### SQLite (Teatros)

Criado automaticamente no startup em `./backstage.db`. Nenhuma configuração adicional necessária em desenvolvimento.

Para usar PostgreSQL em produção, basta trocar `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

---

## Seed

Popula o banco de teatros a partir de `seeds/theaters.json`:

```bash
python -m seeds.seed
```

> ⚠️ O seed **limpa** a tabela de teatros antes de reinserir. Não rode em produção com dados reais.

---

## Rodando a API

```bash
# Com uv (recomendado)
uv run -m uvicorn app.main:app --reload

# Com uvicorn direto
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentação interativa: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Endpoints

### Teatros (`/theaters`) — SQL

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/theaters` | Lista todos os teatros (`?limit=&skip=`) |
| `GET` | `/theaters/{id}` | Detalhe de um teatro |
| `POST` | `/theaters` | Cria um teatro |
| `PATCH` | `/theaters/{id}` | Atualiza parcialmente |
| `DELETE` | `/theaters/{id}` | Remove um teatro |

### Performances (`/performances`) — MongoDB

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/performances` | Lista com filtros (`?q=&season=&classification=&skip=&limit=`) |
| `GET` | `/performances/{id}` | Detalhe |
| `POST` | `/performances` | Cria uma performance |
| `PATCH` | `/performances/{id}` | Atualiza parcialmente |
| `DELETE` | `/performances/{id}` | Remove |

### Sessões (`/sessions`) — MongoDB

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/sessions` | Lista com filtros (`?performance_id=&theater_id=&from=&to=`) |
| `POST` | `/sessions/rule` | Cria sessões por recorrência semanal |
| `POST` | `/sessions/manual` | Cria sessões manualmente (lista de datetimes) |
| `DELETE` | `/sessions/{id}` | Remove uma sessão |

### Mídia (`/media`)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/media/upload` | Upload de imagem; retorna path relativo |

### Utils

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/utils/address/cep/{cep}` | Lookup de CEP (ViaCEP) |

---

## Modelos de dados

### Theater (SQL)

```
id           INTEGER PK autoincrement
name         TEXT NOT NULL
slug         TEXT UNIQUE
street       TEXT
number       TEXT
neighborhood TEXT
city         TEXT
state        TEXT
postal_code  TEXT
country      TEXT
lng          REAL
lat          REAL
website      TEXT
instagram    TEXT
phone        TEXT
photo_base64 TEXT
```

### Performance (MongoDB)

```json
{
  "_id":              "ObjectId",
  "name":             "string",
  "synopsis":         "string",
  "tags":             ["string"],
  "classification":   "Livre | 10 | 12 | 14 | 16 | 18",
  "season":           2025,
  "duration_minutes": 90,
  "dramaturgy":       ["string"],
  "direction":        ["string"],
  "cast":             ["string"],
  "crew":             [{ "role": "string", "people": ["string"] }],
  "ticket_links":     [{ "theater_id": "str", "theater_name": "str", "url": "str | null" }],
  "banner_url":       "string | null",
  "created_at":       "datetime",
  "updated_at":       "datetime"
}
```

### Session (MongoDB)

```json
{
  "_id":            "ObjectId",
  "performance_id": "ObjectId (str)",
  "theater_id":     "integer (FK → Theater.id)",
  "datetime":       "datetime (UTC)",
  "created_at":     "datetime",
  "updated_at":     "datetime"
}
```

---

## Upload de mídia

Arquivos são salvos em `static/uploads/<category>/`. O endpoint retorna o path relativo:

```json
{ "url": "/static/uploads/banners/nome-do-arquivo.webp" }
```

O diretório `static/` é montado como arquivos estáticos em `/static`.

---

## Estrutura de pastas

```
.
├── app/
│   ├── core/
│   │   ├── config.py          # Leitura centralizada de env vars (pydantic-settings)
│   │   └── settings.py        # Alias legado (deprecar)
│   ├── db/
│   │   ├── mongo.py           # Conexão MongoDB (motor)
│   │   └── sql.py             # Engine SQLAlchemy async + sessão
│   ├── models/
│   │   └── theater.py         # Modelo ORM SQLAlchemy
│   ├── repositories/
│   │   ├── theaters_repo.py   # CRUD teatros (SQL)
│   │   ├── performances_repo.py # CRUD performances (Mongo)
│   │   └── sessions_repo.py   # CRUD sessões (Mongo)
│   ├── routes/
│   │   ├── theaters.py
│   │   ├── performances.py
│   │   ├── sessions.py
│   │   ├── media.py
│   │   └── utils_address.py
│   ├── schemas/
│   │   ├── theaters.py
│   │   ├── performances.py
│   │   └── common.py
│   └── main.py                # Entry point + lifespan + CORS
├── seeds/
│   ├── seed.py
│   └── theaters.json
├── static/
│   └── uploads/               # Gerado automaticamente no startup
├── scripts/
│   └── setup.ps1
├── .env.example
├── requirements.txt
└── README.md
```

---

## Troubleshooting

| Problema | Causa provável | Solução |
|---|---|---|
| `Connection refused` no MongoDB | Serviço não iniciado | `docker start theaters-mongo` ou iniciar serviço local |
| `CORS error` no browser | Origem não listada | Adicionar origem em `CORS_ORIGINS` no `.env` |
| `422 Unprocessable Entity` | Payload inválido | Consultar `/docs` para schema esperado |
| Sessões não aparecem | `performance_id` inválido | Verificar se é um ObjectId válido (24 hex chars) |
| Tabela SQL não criada | Startup não executado | Garantir que `lifespan` está registrado em `main.py` |

---

## Changelog

| Versão | Mudança |
|---|---|
| 0.6.0 | Teatros migrados para SQLite/SQLAlchemy; MongoDB mantido para performances e sessões |
| 0.5.x | Sessões extraídas de embedded documents para coleção independente |
| 0.4.x | Adicionados `ticket_links`, `duration_minutes` e `crew` nas performances |
| 0.3.x | Upload de mídia (`/media/upload`) + static files |
