from langchain.chains                   import LLMChain, TransformChain
from langchain.prompts                  import PromptTemplate
from langchain_openai                   import ChatOpenAI
from langchain_core.messages            import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts             import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history        import BaseChatMessageHistory
from langchain_core.runnables.history   import RunnableWithMessageHistory
from services.memory                    import InMemoryHistory
from services.mongo_service             import MongoService
from services.mongo_search              import search_and_combine_text
from typing                             import List, Dict, Optional, Any
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
        # Première étape : résumé des fonctionnalités clés du projet
        # --------------------------------------------------------------------------------------- #
        self.first_stage_prompt = PromptTemplate(
            template="""You are an AI Act specialist, formed in european law and regulations. You have been asked to summarize 
            the important points of this project that uses AI technology. You need to provide a concise list with all the key 
            functionalities that makes use of AI in this project, that may fall under the new AI regulation laws. 
            
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
        # Détermination du niveau de risque du projet
        # --------------------------------------------------------------------------------------- #
        self.last_stage_prompt = PromptTemplate(
            template="""Your are a legal expert in European Law. Based on the Key AI Functionalities of a AI project described, 
            you must categorize this project in one of the four different risk levels of the AI Act : unacceptable, high, 
            limited, or minimal risk. 

            Legislation on AI Act risk levels:

            The AI Act classifies AI according to its risk: 
            1) Unacceptable risk is prohibited (e.g. social scoring systems and manipulative AI). 
            2) High-risk AI systems, which are highly regulated. 
            3) Limited risk AI systems, subject to lighter transparency obligations. 
            4) Minimal risk AI systems, which are unregulated.

            1) Prohibited AI systems (Chapter II, Art. 5): ...
            ... (rest of your text) ...
            
            Project Key AI Functionalities:
            {key_functionalities}

            Answer, which risk category would this project be classified to :""",
            input_variables=["key_functionalities"]
        )
        self.last_stage_chain = LLMChain(
            llm=self.llm,
            prompt=self.last_stage_prompt,
            output_key="risk_level"
        )

        # --------------------------------------------------------------------------------------- #
        # RAG avec Atlas Search pour récupérer et combiner les informations
        # --------------------------------------------------------------------------------------- #
        self.transform_chain = TransformChain(
            input_variables=["key_functionalities"],
            output_variables=["aiact_extract"], 
            transform=lambda inputs: {
                "aiact_extract": search_and_combine_text(inputs["key_functionalities"])
            }
        )

        # --------------------------------------------------------------------------------------- #
        # Génération d'un guide de conformité
        # --------------------------------------------------------------------------------------- #
        self.second_stage_prompt = PromptTemplate(
            template="""Using the provided extract from the AI Act legislation and the outlined project key AI functionalities, 
            your task is to create a concise compliance guide. This guide should detail the necessary steps to align with 
            the requirements of the AI Act.

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
        # (Optional) We don't strictly need this big chain anymore, but you can keep it if you like.
        # We're going to manually orchestrate instead of using SequentialChain to handle the skip logic.
        # --------------------------------------------------------------------------------------- #
        # self.compliance_guide_chain = SequentialChain(
        #     chains=[
        #         self.first_stage_chain,
        #         self.last_stage_chain,
        #         self.transform_chain,
        #         self.second_stage_chain
        #     ],
        #     input_variables=["project_description"],
        #     output_variables=["key_functionalities", "risk_level", "aiact_extract", "compliance_guide"]
        # )

    # ------------------------------------------------------------------------------------------- #
    # Génère un guide de conformité AI Act
    # ------------------------------------------------------------------------------------------- #
    async def generate_compliance_guide(self, project_description: str) -> Dict[str, Any]:
        """
        Orchestrates each step. We will skip the RAG + compliance guide if the risk level is 'Prohibited' or 'Unacceptable'.
        """
        try:
            # 1) Summarize the project's AI functionalities
            first_result = await self.first_stage_chain.acall({"project_description": project_description})
            key_functionalities = first_result["key_functionalities"]

            # 2) Determine the risk level
            second_result = await self.last_stage_chain.acall({"key_functionalities": key_functionalities})
            risk_level = second_result["risk_level"]

            # Check if risk level is "Prohibited" or "Unacceptable"
            lower_risk = risk_level.strip().lower()
            if "prohibited" in lower_risk or "unacceptable" in lower_risk:
                # Short-circuit: no further steps
                return {
                    "key_functionalities": key_functionalities,
                    "risk_level": risk_level,
                    "aiact_extract": "",
                    "compliance_guide": ""
                }

            # 3) If not prohibited, do RAG (search + combine)
            transform_output = self.transform_chain.run({"key_functionalities": key_functionalities})
            aiact_extract = transform_output["aiact_extract"]

            # 4) Generate compliance guide
            guide_result = await self.second_stage_chain.acall({
                "key_functionalities": key_functionalities,
                "aiact_extract": aiact_extract
            })
            compliance_guide = guide_result["compliance_guide"]

            return {
                "key_functionalities": key_functionalities,
                "risk_level": risk_level,
                "aiact_extract": aiact_extract,
                "compliance_guide": compliance_guide
            }
        except Exception as e:
            raise ValueError(f"Erreur lors de la génération du résumé : {str(e)}")