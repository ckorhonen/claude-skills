"""Configuration for agent_memory package."""

import os

DB_URL = os.environ.get("AGNO_DB_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")
EMBEDDING_MODEL = os.environ.get("AGNO_EMBEDDING_MODEL", "text-embedding-3-small")
