import os

PG_DB_NAME = os.getenv("POSTGRES_DB", "moviesauth")
PG_USER_NAME = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("POSTGRES_PORT", 5432)
