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
            template            = """You are an AI Act specialist, formed in european law and regulations. You have been asked to summarize the important points of this project that uses AI technology. You need to provide a concise list with all the key functionalities that makes use of AI in this project, that may fall under the new AI regulation laws.  :
            
            {project_description}
            
            Résumé détaillé :""",
            input_variables = ["project_description"]
        )
        self.first_stage_chain = LLMChain(
            llm                = self.llm,
            prompt             = self.first_stage_prompt,
            output_key         = "key_functionalities"
        )

        # --------------------------------------------------------------------------------------- #
        # Quatrième étape : détermination du niveau de risque du projet
        # --------------------------------------------------------------------------------------- #
        # Utilisation du guide de conformité pour déterminer le niveau de risque du projet
        # --------------------------------------------------------------------------------------- #

        self.last_stage_prompt = PromptTemplate(
            template="""Your are a legal expert in European Law. Based on the Key AI Functionalities of a AI project described, you must categorize this project in one of the four different risk levels of the AI Act : unacceptable, high, limited, or minimal risk. 

            Legislation on AI Act risk levels:

            The AI Act classifies AI according to its risk: 1) Unacceptable risk is prohibited (e.g. social scoring systems and manipulative AI). 2) High-risk AI systems, which are high regulated. 3) Limited risk AI systems, subject to lighter transparency obligations: developers and deployers must ensure that end-users are aware that they are interacting with AI (chatbots and deepfakes). 4) Minimal risk, is unregulated (including the majority of AI applications currently available on the EU single market, such as AI enabled video games and spam filters).

            1) Prohibited AI systems (Chapter II, Art. 5) : The following types of AI system are Prohibited according to the AI Act. AI systems: deploying subliminal, manipulative, or deceptive techniques to distort behaviour and impair informed decision-making, causing significant harm. exploiting vulnerabilities related to age, disability, or socio-economic circumstances to distort behaviour, causing significant harm. biometric categorisation systems inferring sensitive attributes (race, political opinions, trade union membership, religious or philosophical beliefs, sex life, or sexual orientation), except labelling or filtering of lawfully acquired biometric datasets or when law enforcement categorises biometric data. social scoring, i.e., evaluating or classifying individuals or groups based on social behaviour or personal traits, causing detrimental or unfavourable treatment of those people. assessing the risk of an individual committing criminal offenses solely based on profiling or personality traits, except when used to augment human assessments based on objective, verifiable facts directly linked to criminal activity. compiling facial recognition databases by untargeted scraping of facial images from the internet or CCTV footage. inferring emotions in workplaces or educational institutions, except for medical or safety reasons. real-time remote biometric identification (RBI) in publicly accessible spaces for law enforcement, except when: searching for missing persons, abduction victims, and people who have been human trafficked or sexually exploited; preventing substantial and imminent threat to life, or foreseeable terrorist attack; or identifying suspects in serious crimes (e.g., murder, rape, armed robbery, narcotic and illegal weapons trafficking, organised crime, and environmental crime, etc.).

            2) High risk AI systems (Chapter III) : Some AI systems are considered High risk under the AI Act. Providers of those systems will be subject to additional requirements. Classification rules for high-risk AI systems (Art. 6) High risk AI systems are those: used as a safety component or a product covered by EU laws in Annex I AND required to undergo a third-party conformity assessment under those Annex I laws; OR those under Annex III use cases (below), except if: the AI system performs a narrow procedural task; improves the result of a previously completed human activity; detects decision-making patterns or deviations from prior decision-making patterns and is not meant to replace or influence the previously completed human assessment without proper human review; or performs a preparatory task to an assessment relevant for the purpose of the use cases listed in Annex III. AI systems are always considered high-risk if it profiles individuals, i.e. automated processing of personal data to assess various aspects of a person s life, such as work performance, economic situation, health, preferences, interests, reliability, behaviour, location or movement. Providers whose AI system falls under the use cases in Annex III but believes it is not high-risk must document such an assessment before placing it on the market or putting it into service.

            3) Limited risk AI systems : Limited risk refers to the risks associated with lack of transparency in AI usage. The AI Act introduces specific transparency obligations to ensure that humans are informed when necessary, fostering trust. For instance, when using AI systems such as chatbots, humans should be made aware that they are interacting with a machine so they can take an informed decision to continue or step back. Providers also have to ensure that AI-generated content is identifiable. Besides, AI-generated text published with the purpose to inform the public on matters of public interest must be labelled as artificially generated. This also applies to audio and video content constituting deep fakes.

            4) Minimal risk AI systems : The AI Act allows the free use of minimal-risk AI. This includes applications such as AI-enabled video games or spam filters. The vast majority of AI systems currently used in the EU fall into this category.
             
            Project Key AI Functionalities:

            {key_functionalities}
            
            Answer, which risk category would this project be classified to :""",
            input_variables = ["key_functionalities"]
        )
        self.last_stage_chain = LLMChain(
            llm               = self.llm,
            prompt            = self.last_stage_prompt,
            output_key        = "risk_level"
        )

        # --------------------------------------------------------------------------------------- #
        # Deuxième étape : recherche et combinaison des informations pertinentes de l'AI Act
        # --------------------------------------------------------------------------------------- #
        # Utilisation de RAG avec Atlas Search pour rechercher et combiner les informations 
        # --------------------------------------------------------------------------------------- # 

        self.transform_chain = TransformChain(
            input_variables  = ["key_functionalities"],
            output_variables = ["aiact_extract"], 
            transform        = lambda inputs: {
                "aiact_extract": search_and_combine_text(inputs["key_functionalities"])
            }
        )

        # --------------------------------------------------------------------------------------- #
        # Troisième étape : génération d'un guide de conformité
        # --------------------------------------------------------------------------------------- #
        # Utilisation des informations extraites de l'AI Act pour générer un guide de conformité
        # --------------------------------------------------------------------------------------- #

        self.second_stage_prompt = PromptTemplate(
            template             = """Using the provided extract from the AI Act legislation and the outlined project key AI functionalities, your task is to create a concise compliance guide. This guide should detail the necessary steps to align with the requirements of the AI Act.

            Context:

            Project Key AI Functionalities:
            {key_functionalities}

            AI Act Legislation Extract:
            {aiact_extract}

            Compliance Requirements:""",
            input_variables=["key_functionalities", "aiact_extract"]
        )
        self.second_stage_chain = LLMChain(
            llm                 = self.llm,
            prompt              = self.second_stage_prompt,
            output_key          = "compliance_guide"
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
                self.last_stage_chain,      # Consumes "compliance_guide", outputs "risk_level"
                self.transform_chain,       # Takes "key_functionalities", outputs "aiact_extract"
                self.second_stage_chain     # Consumes "key_functionalities" and "aiact_extract", outputs "compliance_guide"
            ],
            input_variables  = ["project_description"],
            output_variables = ["key_functionalities", "risk_level", "aiact_extract", "compliance_guide"]
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
