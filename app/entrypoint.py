# Entrypoint para garantir que variáveis do .env sejam carregadas no ambiente do Streamlit
import os
from dotenv import load_dotenv

# Carrega variáveis do .env (se existir)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

import streamlit.web.cli as stcli
import sys

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
    sys.exit(stcli.main())
