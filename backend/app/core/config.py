from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    # App General
    APP_NAME: str = "Plataforma de Emergencias Vehiculares"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    APP_HOST: str = "localhost"

    # Base de datos (Decompuesta para mayor limpieza en .env)
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "emergencias_vehiculares"

    @property
    def DATABASE_URL(self) -> str:
        # Retorna la URL de conexión construida dinámicamente
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT
    SECRET_KEY: str = "cambia_esto"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas (desarrollo)

    # IA (OpenRouter)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL_NAME: str = "meta-llama/llama-3-8b-instruct"
    
    # Transcripción (Whisper Local)
    WHISPER_MODEL_SIZE: str = "tiny"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Configuración de Pydantic v2
    # Buscamos el .env en la raiz del proyecto (4 niveles arriba)
    _base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    model_config = SettingsConfigDict(
        env_file=os.path.join(_base_dir, ".env"),
        env_file_encoding="utf-8",
        extra="ignore" # IGNORAR variables extra para evitar crashes
    )


settings = Settings()
