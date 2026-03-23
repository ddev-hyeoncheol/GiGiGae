from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GiGiGae API"
    debug: bool = True

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:12b"
    ollama_timeout: int = 120

    database_url: str | None = None

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
