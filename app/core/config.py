from dotenv import load_dotenv
import os

# Charge le fichier .env
load_dotenv()


class Settings:
    FRANCE_TRAVAIL_CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
    FRANCE_TRAVAIL_CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")


settings = Settings()