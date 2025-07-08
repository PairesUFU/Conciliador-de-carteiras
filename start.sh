#!/bin/bash

echo "🚀 Iniciando Sistema Conciliador..."
echo "📊 Este projeto irá:"
echo "   - Iniciar PostgreSQL"
echo "   - Popular banco com dados de funds.csv"
echo "   - Iniciar Streamlit com seleção de fundos"
echo ""
echo "🌐 URLs disponíveis:"
echo "   - Streamlit: http://localhost:8501"
echo "   - PgAdmin: http://localhost:8080"
echo ""

# Para e remove containers existentes
echo "🧹 Limpando containers existentes..."
docker-compose down

# Constrói e inicia os serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up --build

echo "✅ Sistema iniciado com sucesso!"
