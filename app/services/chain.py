from langchain.chains                   import LLMChain, SequentialChain, TransformChain
from langchain.prompts                  import PromptTemplate
from langchain_openai                   import ChatOpenAI
from langchain_core.messages            import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts             import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history        import BaseChatMessageHistory
from langchain_core.runnables.history   import RunnableWithMessageHistory
from services.memory                    import InMemoryHistory
from services.mongo_service             import MongoService
from services.mongo_search              import search_and_combine_text
from typing                             import List, Dict, Optional
from langchain_openai                   import ChatOpenAI
from langchain_core.messages            import SystemMessage, HumanMessage, AIMessage
from typing                             import Any, List, Dict, Optional
from pymongo                            import MongoClient

# ----------------------------------------------------------------------------------------------- #
# Service pour generer un guide de conformité utilisant chaines de traitement
# ----------------------------------------------------------------------------------------------- #
# Un premier prompt est utilisé pour résumer les fonctionnalités clés du projet
# RAG avec Atlas Search est utilisé pour recupérer les informations pertinentes de l'AI Act
# Ces informations sont ensuite utilisées pour générer un guide de conformité
# Ce guide est ensuite utilisé pour déterminer le niveau de risque du projet
# ----------------------------------------------------------------------------------------------- #

class AiactService:
    def __init__(self, llm):
        self.llm = llm
        
        # --------------------------------------------------------------------------------------- #
        # Création des chaines de traitement
        # --------------------------------------------------------------------------------------- #

        # --------------------------------------------------------------------------------------- #
        # Première étape : résumé des fonctionnalités clés du projet
        # --------------------------------------------------------------------------------------- #

        self.first_stage_prompt = PromptTemplate(
            template="""You are an AI Act specialist, formed in european law and regulations. You have been asked to summarize the important points of this project that uses AI technology. You need to provide a concise list with all the key functionalities that makes use of AI in this project, that may fall under the new AI regulation laws.  :
            
            {project_description}
            
            Résumé détaillé :""",
            input_variables=["project_description"]
        )
        self.first_stage_chain = LLMChain(
            llm=self.llm,
            prompt=self.first_stage_prompt,
            output_key="key_functionalities"
        )

        # --------------------------------------------------------------------------------------- #
        # Deuxième étape : recherche et combinaison des informations pertinentes de l'AI Act
        # --------------------------------------------------------------------------------------- #
        # Utilisation de RAG avec Atlas Search pour rechercher et combiner les informations 
        # --------------------------------------------------------------------------------------- # 

        self.transform_chain = TransformChain(
            input_variables=["key_functionalities"],
            output_variables=["aiact_extract"], 
            transform=lambda inputs: {
                "aiact_extract": search_and_combine_text(inputs["key_functionalities"])
            }
        )

        # --------------------------------------------------------------------------------------- #
        # Troisième étape : génération d'un guide de conformité
        # --------------------------------------------------------------------------------------- #
        # Utilisation des informations extraites de l'AI Act pour générer un guide de conformité
        # --------------------------------------------------------------------------------------- #

        self.second_stage_prompt = PromptTemplate(
            template="""Using the provided extract from the AI Act legislation and the outlined project key AI functionalities, your task is to create a concise compliance guide. This guide should detail the necessary steps to align with the requirements of the AI Act.

            Context:
            Project Key AI Functionalities:
            {key_functionalities}

            AI Act Legislation Extract:
            {aiact_extract}

            Compliance Requirements:""",
            input_variables=["key_functionalities", "aiact_extract"]
        )
        self.second_stage_chain = LLMChain(
            llm=self.llm,
            prompt=self.second_stage_prompt,
            output_key="compliance_guide"
        )
        
        # --------------------------------------------------------------------------------------- #
        # Quatrième étape : détermination du niveau de risque du projet
        # --------------------------------------------------------------------------------------- #
        # Utilisation du guide de conformité pour déterminer le niveau de risque du projet
        # --------------------------------------------------------------------------------------- #

        self.last_stage_prompt = PromptTemplate(
            template="""Based on the regulations needed you must categorize this project in one of the four different risk levels of the AI Act : unacceptable, high, limited, and minimal risk. :
            
            {compliance_guide}
            
            Phrase de synthèse :""",
            input_variables=["compliance_guide"]
        )
        self.last_stage_chain = LLMChain(
            llm=self.llm,
            prompt=self.last_stage_prompt,
            output_key="risk_level"
        )
        
        # --------------------------------------------------------------------------------------- #
        # Chaîne séquentielle complète
        # --------------------------------------------------------------------------------------- #
        # La chaîne séquentielle complète prend en entrée la description du projet
        # et produit les résultats finaux
        # --------------------------------------------------------------------------------------- #

        self.compliance_guide_chain = SequentialChain(
            chains=[
                self.first_stage_chain,     # Produces "key_functionalities"
                self.transform_chain,       # Takes "key_functionalities", outputs "aiact_extract"
                self.second_stage_chain,    # Consumes "key_functionalities" and "aiact_extract", outputs "compliance_guide"
                self.last_stage_chain       # Consumes "compliance_guide", outputs "risk_level"
            ],
            input_variables    = ["project_description"],
            output_variables   = ["key_functionalities","aiact_extract", "compliance_guide", "risk_level"]
        )
    
    # ------------------------------------------------------------------------------------------- #
    # Génère un guide de conformité AI Act
    # ------------------------------------------------------------------------------------------- #
    
    async def generate_compliance_guide(self, project_description: str) -> Dict[str, Any]:
        try:
            result = await self.compliance_guide_chain.acall({"project_description": project_description})
            return {
                "key_functionalities":  result["key_functionalities"],
                "aiact_extract":        result["aiact_extract"],
                "compliance_guide":     result["compliance_guide"],
                "risk_level":           result["risk_level"]
            }
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération du résumé : {str(e)}")
