# Dockerfile para aplicação Streamlit
FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install python-dotenv

# Copia o código da aplicação
COPY app/ ./

EXPOSE 8501

# Comando direto para executar o Streamlit
CMD ["streamlit", "run", "streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
