# ----------------------------------------------------------------------------------------------- #
# This file contains the models for the conversation data structure.
# ----------------------------------------------------------------------------------------------- #

from typing     import List, Optional
from pydantic   import BaseModel, Field
from datetime   import datetime

# ----------------------------------------------------------------------------------------------- #
# Modèles pour une conversation
# ----------------------------------------------------------------------------------------------- #

class Message(BaseModel):
    role:       str
    content:    str
    timestamp:  datetime = Field(default_factory=datetime.utcnow)

# ----------------------------------------------------------------------------------------------- #
# Modèle pour une conversation
# ----------------------------------------------------------------------------------------------- #

class Conversation(BaseModel):
    session_id: str
    messages:   List[Message] = []
    created_at: datetime      = Field(default_factory=datetime.utcnow)
    updated_at: datetime      = Field(default_factory=datetime.utcnow)