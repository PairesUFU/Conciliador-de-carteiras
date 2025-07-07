# Dockerfile para aplicação Streamlit
FROM python:3.11-slim

WORKDIR /app


# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install python-dotenv

# Copia o código da aplicação
COPY app/ ./app/

WORKDIR /app

EXPOSE 8501

# Entrypoint para garantir variáveis de ambiente do .env
CMD ["python", "app/entrypoint.py"]
