#!/bin/bash

echo "Aguardando PostgreSQL ficar disponível..."

# Aguarda o PostgreSQL ficar disponível usando Python
python << EOF
import os
import time
import psycopg2
from sqlalchemy import create_engine

def wait_for_db():
    db_host = os.getenv("DB_HOST", "postgres")
    db_name = os.getenv("DB_NAME", "bautomation_db")
    db_user = os.getenv("DB_USER", "bautomation_user")
    db_pass = os.getenv("DB_PASS", "admin123")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            conn.close()
            print("PostgreSQL está disponível!")
            return True
        except psycopg2.OperationalError:
            retry_count += 1
            print(f"PostgreSQL não está disponível - tentativa {retry_count}/{max_retries}")
            time.sleep(2)
    
    print("Erro: PostgreSQL não ficou disponível após 30 tentativas")
    return False

wait_for_db()
EOF

echo "Populando tabelas..."

# Executa o script de população das tabelas
python populate_tables.py

echo "Tabelas populadas - iniciando Streamlit..."

# Inicia o Streamlit
exec streamlit run streamlit/main.py --server.port=8501 --server.address=0.0.0.0
