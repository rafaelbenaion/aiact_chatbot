# AIAct Compliance Chatbot

## Project Overview

AI Act Compliance Chatbot is a tool designed to help startups and AI developers align their projects with the European Union's AI Act regulations. This chatbot provides tailored guidance on legislation compliance, leveraging the latest legal texts and project descriptions provided by users. It evaluates whether an AI project is likely to comply with EU regulations and flags any potential issues related to the use of banned AI applications.

The primary objectives of this chatbot are:
1. **Guidance**: Offering personalized advice based on the AI Act and specific project descriptions.
2. **Compliance Assessment**: Determining whether a project aligns with the requirements of the EU AI Act and identifying potential risks of non-compliance.

---

## Technology Stack

- **FastAPI**: Backend framework for API endpoints and logic.
- **LangChain**: Powers chatbot interactions and vectorization for enhanced AI processing.
- **React**: Provides a dynamic and user-friendly frontend interface.
- **MongoDB**: Manages project data and user interaction history for efficient storage.

---

## API Overview

### Endpoint: `/chat/aiact`

#### Method: `POST`
#### Description:
This endpoint accepts project descriptions and provides detailed guidance on compliance with the AI Act. It also evaluates whether the project adheres to EU regulations.

#### Request Body (JSON):

```json
{
  "project_description": "Medical Imaging Diagnostics AI-powered tool for identifying abnormalities (e.g., tumors, fractures) in X-rays, MRIs, and CT scans. Computer vision, deep learning for image recognition, integration with radiology system.",
  "max_length": 10000
}


## Structure du Projet

```
app/
├── api/                    # Gestion des routes et endpoints de l'API
│   ├── endpoints/          # Endpoints spécifiques par fonctionnalité
│   │   ├── __pycache__/    # Cache Python pour les endpoints
│   │   └── chat.py         # Endpoint pour les fonctionnalités de chat
│   └── router.py           # Router principal regroupant tous les endpoints
├── core/                   # Configuration et éléments centraux de l'application
│   ├── __pycache__/        # Cache Python pour les fichiers de configuration
│   └── config.py           # Fichier de configuration principal
├── models/                 # Modèles de données Pydantic
│   ├── __pycache__/        # Cache Python pour les modèles
│   ├── chat.py             # Modèle pour les requêtes/réponses de chat
│   └── conversation.py     # Modèle pour la gestion des conversations
├── services/               # Services métier
│   ├── __pycache__/        # Cache Python pour les services
│   ├── chain.py            # Gestion des chaînes d'exécution pour LangChain
│   ├── llm_service.py      # Service d'interaction avec le LLM (LangChain)
│   ├── memory.py           # Service pour la gestion de la mémoire contextuelle
│   ├── mongo_search.py     # Service de recherche dans MongoDB
│   └── mongo_service.py    # Service pour les opérations MongoDB
├── tools/                  # Utilitaires et fichiers annexes
│   ├── aiact.pdf           # Document PDF du AI Act
│   ├── mangodb_embeddings.py # Gestion des embeddings pour MongoDB
│   ├── page_embeddings.json  # Embeddings pour les pages du AI Act
│   └── text.py             # Utilitaires pour le traitement de texte
├── main.py                 # Point d'entrée principal de l'application
.env                        # Fichier d'environnement pour les configurations sensibles
.env.template               # Modèle du fichier d'environnement
.gitignore                  # Fichier pour ignorer certains fichiers/dossiers dans Git
README.md                   # Documentation principale du projet

```

## Installation et Configuration

### Prérequis
- Python 3.11+ (ici : https://www.python.org/downloads/release/python-3110/ il faut redémarrer après installation pour avoir le $PATH sur l'OS)
- Visual Studio Code avec l'extension Python
- Une clé OpenAI que je vais vous fournir

### Installation

1. **Cloner le projet**
```bash
git clone <URL_DU_DEPOT>
cd <NOM_DU_PROJET>
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
- Windows :
```bash
.\venv\Scripts\activate
```
- macOS/Linux :
```bash
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Configurer la clé API OpenAI**
Créer un fichier `.env` à la racine du projet :
```
OPENAI_API_KEY=votre-clé-api-openai
```
