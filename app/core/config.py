# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     mongodb_uri: str = MONGODB_URI
#     database_name: str = "chatbot"
#     collection_name: str ="conversations"

#     class Config:
#         env_file = ".env"

# settings = Settings()

# ----------------------------------------------------------------------------------------------- #
# Configuration de l'application
# ----------------------------------------------------------------------------------------------- #

import  logging
import  os
from    dotenv import load_dotenv

# ----------------------------------------------------------------------------------------------- #
# Charger les variables d'environnement depuis le fichier .env
# ----------------------------------------------------------------------------------------------- #

load_dotenv()

# ----------------------------------------------------------------------------------------------- #
# Configuration de la journalisation
# ----------------------------------------------------------------------------------------------- #

class Config:
    MONGO_URI       = os.getenv("MONGO_URI", os.getenv("MONGODB_URI"))  # URI de connex par défaut
    MONGO_DB        = os.getenv("MONGO_DB", "chatbot")                  # Nom de base par défaut
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "conversations")     # Nom de base par défaut