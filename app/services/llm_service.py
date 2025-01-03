# services/llm_service.py
# ----------------------------------------------------------------------------------------------- #
# Service principal gérant les interactions avec le modèle de langage
# ----------------------------------------------------------------------------------------------- #

from langchain_openai                   import ChatOpenAI
from langchain_core.messages            import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts             import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history        import BaseChatMessageHistory
from langchain_core.runnables.history   import RunnableWithMessageHistory
from services.memory                    import InMemoryHistory
from services.mongo_service             import MongoService
from typing                             import List, Dict, Optional
from langchain_openai                   import ChatOpenAI
from langchain_core.messages            import SystemMessage, HumanMessage, AIMessage
from services.mongo_service             import MongoService
from services.chain                     import AiactService
from typing                             import Any, List, Dict, Optional
import os

class LLMService:
    def __init__(self):
        
        # --------------------------------------------------------------------------------------- #
        # Instanciation du LLM (ChatOpenAI par exemple)
        # --------------------------------------------------------------------------------------- #

        self.llm = ChatOpenAI(
            api_key     = os.environ.get("OPENAI_API_KEY"), 
            temperature = 0.7,
            max_tokens  = 1500,
        )

        self.mongo_service      = MongoService()
        self.aiact_service      = AiactService(self.llm)
    
    # ------------------------------------------------------------------------------------------- #
    # Génère une réponse et sauvegarde dans MongoDB
    # ------------------------------------------------------------------------------------------- #

    async def generate_response(self,
                                message:    str,
                                session_id: Optional[str] = None) -> str:

        # --------------------------------------------------------------------------------------- #
        # Récupération de l'historique depuis MongoDB
        # --------------------------------------------------------------------------------------- #

        history = await self.mongo_service.get_conversation_history(session_id)

        # --------------------------------------------------------------------------------------- #
        # Conversion de l'historique en messages LangChain
        # --------------------------------------------------------------------------------------- #

        messages = [SystemMessage(content="Vous êtes un assistant utile et concis.")]
        for msg in history:

            if msg["role"]      == "user":
                messages.append(HumanMessage(content=msg["content"]))

            elif msg["role"]    == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # --------------------------------------------------------------------------------------- #
        # Ajout du nouveau message
        # --------------------------------------------------------------------------------------- #

        messages.append(HumanMessage(content=message))

        # --------------------------------------------------------------------------------------- #
        # Génération de la réponse à partir de self.llm
        # --------------------------------------------------------------------------------------- #

        response        = await self.llm.agenerate([messages])
        response_text   = response.generations[0][0].text

        # --------------------------------------------------------------------------------------- #
        # Sauvegarde des messages dans MongoDB
        # --------------------------------------------------------------------------------------- #

        await self.mongo_service.save_message(session_id, "user", message)
        await self.mongo_service.save_message(session_id, "assistant", response_text)

        return response_text

    # ------------------------------------------------------------------------------------------- #
    # Récupère l'historique depuis MongoDB
    # ------------------------------------------------------------------------------------------- #

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:

        return await self.mongo_service.get_conversation_history(session_id)
    
    # ------------------------------------------------------------------------------------------- #
    # Génère un guide de conformité AI Act
    # ------------------------------------------------------------------------------------------- #

    async def generate_compliance_guide(self, project_description: str) -> Dict[str, Any]:
        return await self.aiact_service.generate_compliance_guide(project_description)
