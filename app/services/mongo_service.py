from motor.motor_asyncio    import AsyncIOMotorClient
from datetime               import datetime
from typing                 import List, Dict, Optional
from models.conversation    import Conversation, Message
from core.config            import Config

class MongoService:
    def __init__(self):
        self.client         = AsyncIOMotorClient(Config.MONGO_URI)
        self.db             = self.client[Config.MONGO_DB]
        self.conversations  = self.db[Config.COLLECTION_NAME]

    # ------------------------------------------------------------------------------------------- #
    # Sauvegarde un nouveau message dans une conversation
    # ------------------------------------------------------------------------------------------- #

    async def save_message(self, session_id: str, role: str, content: str) -> bool:

        message = Message(role=role, content=content)
        result  = await self.conversations.update_one(
            {"session_id": session_id},
            {
                "$push"         : {"messages": message.model_dump()},
                "$set"          : {"updated_at": datetime.utcnow()},
                "$setOnInsert"  : {"created_at": datetime.utcnow()}
            },
            upsert=True
        )

        return result.modified_count > 0 or result.upserted_id is not None

    # ------------------------------------------------------------------------------------------- #
    # Récupère l'historique d'une conversation
    # ------------------------------------------------------------------------------------------- #
    
    async def get_conversation_history(self, session_id: str) -> List[Dict]:

        conversation = await self.conversations.find_one({"session_id": session_id})
        if conversation:
            return conversation.get("messages", [])
        return []

    # ------------------------------------------------------------------------------------------- #
    # Supprime une conversation
    # ------------------------------------------------------------------------------------------- #

    async def delete_conversation(self, session_id: str) -> bool:

        result = await self.conversations.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    # ------------------------------------------------------------------------------------------- #
    # Récupère tous les IDs de session
    # ------------------------------------------------------------------------------------------- #

    async def get_all_sessions(self) -> List[str]:

        cursor      = self.conversations.find({}, {"session_id": 1})
        sessions    = await cursor.to_list(length=None)

        return [session["session_id"] for session in sessions]