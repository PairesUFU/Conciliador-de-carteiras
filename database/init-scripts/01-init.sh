#!/bin/bash
set -e

# ==============================================================================
# SCRIPT DE INICIALIZAÇÃO DO BANCO DE DADOS POSTGRESQL (DOCKER)
# ==============================================================================
# Este script é executado automaticamente quando o container PostgreSQL 
# é iniciado pela primeira vez. Ele configura o banco de dados e usuário.
# ==============================================================================

echo "🚀 Iniciando configuração do banco de dados PostgreSQL..."

# As variáveis de ambiente já estão definidas pelo Docker Compose:
# - POSTGRES_DB
# - POSTGRES_USER  
# - POSTGRES_PASSWORD

echo "✅ Banco de dados '$POSTGRES_DB' criado com sucesso!"
echo "✅ Usuário '$POSTGRES_USER' criado com sucesso!"
echo "✅ Privilégios concedidos ao usuário '$POSTGRES_USER'!"

echo ""
echo "📊 Informações de Conexão:"
echo "  - Host: localhost (ou nome do container 'postgres')"
echo "  - Porta: 5433 (padrão)"
echo "  - Banco: $POSTGRES_DB"
echo "  - Usuário: $POSTGRES_USER"
echo "  - Senha: [definida via variável de ambiente]"
echo ""
echo "🔗 String de Conexão:"
echo "  postgresql://$POSTGRES_USER:[senha]@localhost:5433/$POSTGRES_DB"
echo ""
echo "✨ Configuração do PostgreSQL concluída!"
