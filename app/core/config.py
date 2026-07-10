"""Configuration centralisée de l'application, chargée depuis les variables d'environnement."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de configuration de JobPilot AI."""

    france_travail_client_id: str
    france_travail_client_secret: str
    openrouteservice_api_key: str
    jooble_api_key: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()