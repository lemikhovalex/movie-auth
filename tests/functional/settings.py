from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    pg_host: str = Field("db", env="POSTGRES_DB")
    pg_user: str = Field("app", env="POSTGRES_USER")
    pg_password: str = Field("app", env="POSTGRES_PASSWORD")
    pg_db: str = "auth"

    api_host: str = Field("auth", env="API_HOST")
    api_port: int = Field(5000, env="API_PORT")

    service_wait_timeout: int = Field(30, env="SERVICE_WAIT_TIMEOUT")  # seconds
    service_wait_interval: int = Field(1, env="SERVICE_WAIT_INTERVAL")  # seconds

    redis_host: str = Field("redis", env="POSTGRES_HOST")
    redis_port: int = Field(6379, env="POSTGRES_PORT")
