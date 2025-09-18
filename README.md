# Backstage API (FastAPI + MongoDB)

API para gerenciar **teatros** e **performances** (espetáculos) com sessões por teatro.  
Stack: FastAPI, MongoDB (motor), Pydantic v2.

## Sumário
- [Requisitos](#requisitos)
- [Rodar rápido](#rodar-rápido)
- [Configuração](#configuração)
- [Seeds](#seeds)
- [Como iniciar a API](#como-iniciar-a-api)
- [Endpoints](#endpoints)
- [Modelos de dados](#modelos-de-dados)
- [Consultas comuns](#consultas-comuns)
- [Troubleshooting](#troubleshooting)
- [Scripts úteis](#scripts-úteis)

---

## Requisitos
- Python 3.11+ (recomendado)
- MongoDB:
  - **Docker Desktop** (Windows/macOS) **ou**
  - **MongoDB Community** instalado localmente

## Rodar rápido

### Windows (PowerShell)
```powershell
# clonar o repositório e entrar na pasta do projeto
.\scripts\setup.ps1             # instala deps e roda o seed
uv run -m uvicorn app.main:app --reload
# docs: http://127.0.0.1:8000/docs

## Configuração

### 1) Variáveis de ambiente

Crie um arquivo `.env` (ou copie do exemplo):

```bash
# macOS/Linux
cp .env.example .env
# Windows (PowerShell)
copy .env.example .env

### 2) MongoDB via Docker
Tenha o Docker Desktop rodando (Windows/macOS) e a engine WSL2 habilitada no Windows.

Suba o container:
docker run -d --name theaters-mongo -p 27017:27017 mongo:7

Teste a conexão com MONGODB_URI=mongodb://localhost:27017.

### 3)Seed do banco
Popule a base com os teatros do arquivo seeds/theaters.json (Extended JSON).

$env:MONGODB_URI="mongodb://localhost:27017"
$env:MONGODB_DB="theatersdb"
python .\seeds\seed.py