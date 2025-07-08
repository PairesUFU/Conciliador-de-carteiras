# Dockerfile para aplicação Streamlit
FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install python-dotenv

# Copia o código da aplicação
COPY app/ ./
COPY populate_tables.py ./
COPY funds.csv ./

EXPOSE 8501

# Script de inicialização que popula o banco e inicia o Streamlit
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

CMD ["./docker-entrypoint.sh"]
