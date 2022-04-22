import os

PG_DB_NAME = os.getenv("POSTGRES_DB", "auth")
PG_USER_NAME = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("POSTGRES_PORT", 5432)
PG_HOST = os.getenv("POSTGRES_HOST", "db")

REDIS_HOST = os.getenv("POSTGRES_HOST", "redis")
REDIS_PORT = os.getenv("POSTGRES_PORT", 6379)
