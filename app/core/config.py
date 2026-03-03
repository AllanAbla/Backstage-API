"""
app/core/config.py
Centraliza toda leitura de variáveis de ambiente.
Crie app/core/__init__.py vazio se não existir.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # CORS — separe múltiplas origens por vírgula no .env
    # Ex: CORS_ORIGINS="http://localhost:5173,https://backstage.meudominio.com"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "theatersdb"

    # SQL (SQLite por padrão para dev local)
    database_url: str = "sqlite+aiosqlite:///./backstage.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()