"""
Configuración de la aplicación usando Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.
    Lee variables de entorno o usa valores por defecto.
    """

    # Información de la aplicación
    app_name: str = "Professional Hubs - Conflict API"
    api_version: str = "v1"
    debug: bool = False

    # Base de datos PostgreSQL
    database_url: str = "postgresql://user:password@localhost:5432/conflicts_db"

    # Configuración de fuzzy matching para conflictos
    fuzzy_threshold: int = 70  # Mínimo 70% de similitud para considerar coincidencia
    fuzzy_high_confidence: int = 90  # >= 90% es confianza alta

    # CORS - Orígenes permitidos (separados por coma)
    cors_origins: str = "*"

    # Timezone para Puerto Rico
    timezone: str = "America/Puerto_Rico"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte string de orígenes CORS a lista."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instancia singleton de configuración.
    Usa cache para evitar recrear en cada llamada.
    """
    return Settings()
