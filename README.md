# attentions_sight - attentions.ai assignment
- multiagentic research assistent

# installed packages
- fastapi
- streamlit
- uvicorn
- langchain
- langchain-groq
- dotenv
- pypdf2

# how to setup?
- `git clone <repo>`
- `cd <repo>`
- `pip install virtualenv` (if you don't already have virtualenv installed)
- `virtualenv venv` to create your new environment
- `source venv/bin/activate` to enter the virtual environment(automatic if use direnv with envrc)
- `pip install -r requirements.txt` to install the requirements in the current environment

# how to run?
- setup "GROK_API_KEY" in .env or terminal environment
- start server - `uvicorn backend.main:app --reload`
- start frontend - `streamlit run frontend/main.py`
