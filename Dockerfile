# Dockerfile para aplicação Streamlit
FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação (que agora inclui o funds.csv)
COPY app/ /app/

EXPOSE 8501

CMD ["sh", "-c", "echo 'Aguardando PostgreSQL...' && sleep 10 && python /app/populate_tables.py && streamlit run /app/streamlit/main.py --server.port=8501 --server.address=0.0.0.0"]
