from    dotenv                  import load_dotenv
from    fastapi                 import FastAPI
from    fastapi.middleware.cors import CORSMiddleware
from    api.router              import router as api_router
from    services.llm_service    import LLMService
import  uvicorn

load_dotenv()

# ----------------------------------------------------------------------------------------------- #
# Instance de l'application FastAPI
# ----------------------------------------------------------------------------------------------- #

app = FastAPI(
    title       = "Agent conversationnel",
    description = "API pour un agent conversationnel - Smiling AI",
    version     = "1.0",
)

# ----------------------------------------------------------------------------------------------- #
# Middleware pour autoriser les requêtes CORS
# ----------------------------------------------------------------------------------------------- #

app.add_middleware(
    CORSMiddleware,
    allow_origins       = ["*"],
    allow_credentials   = True,
    allow_methods       = ["*"],
    allow_headers       = ["*"],
)

# ----------------------------------------------------------------------------------------------- #
# Instance du service LLM
# ----------------------------------------------------------------------------------------------- #

llm_service = LLMService()

# ----------------------------------------------------------------------------------------------- #
# Inclure les routes
# ----------------------------------------------------------------------------------------------- #

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)