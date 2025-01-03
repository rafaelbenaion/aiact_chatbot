# models/chat.py
# ----------------------------------------------------------------------------------------------- #
# Modèles Pydantic pour la validation des données
# ----------------------------------------------------------------------------------------------- #

from typing     import Dict, List, Optional
from pydantic   import BaseModel

# ----------------------------------------------------------------------------------------------- #
# Modèles pour générer un guide de conformité
# ----------------------------------------------------------------------------------------------- #

class AiactRequest(BaseModel):

    project_description: Optional[str]  = "Medical Imaging Diagnostics AI-powered tool for identifying abnormalities (e.g., tumors, fractures) in X-rays, MRIs, and CT scans. Computer vision, deep learning for image recognition, integration with radiology system."
    max_length:          Optional[int]  = 10000

class AiactResponse(BaseModel):

    key_functionalities:    str
    aiact_extract:          str
    compliance_guide:       str
    risk_level:             str
    

# class ChatRequestTP1(BaseModel):
#     """Requête de base pour une conversation sans contexte"""
#     message: str

# class ChatResponse(BaseModel):
#     """Réponse standard du chatbot"""
#     response: str

# class ChatRequestWithContext(BaseModel):
#     """Requête avec contexte de conversation du TP1"""
#     message: str
#     context: Optional[List[Dict[str, str]]] = []

# class ChatRequestTP2(BaseModel):
#     """Requête de base pour une conversation sans contexte"""
#     message: str
#     session_id: str  # Ajouté pour supporter les deux versions

# class ChatMessage(BaseModel):
#     """Structure d'un message individuel dans l'historique"""
#     role: str  # "user" ou "assistant"
#     content: str

# class ChatHistory(BaseModel):
#     """Collection de messages formant une conversation"""
#     messages: List[ChatMessage]