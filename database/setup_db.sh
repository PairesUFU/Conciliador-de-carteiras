#!/bin/bash

# ==============================================================================
# SCRIPT DE CONFIGURAÇÃO DE BANCO DE DADOS POSTGRESQL
# ==============================================================================
# Este script:
# 1. Define variáveis para o novo banco de dados, usuário e senha.
# 2. Executa comandos SQL para criar o banco de dados e o usuário.
# 3. Concede todos os privilégios do novo banco de dados ao novo usuário.
# 4. Exibe as informações de conexão (endpoint, etc.).
# ==============================================================================

# -- Sinta-se à vontade para alterar estas variáveis --
DB_NAME="bautomation_db"
DB_USER="bautomation_user"
DB_PASS="admin123"
DB_HOST="localhost"
DB_PORT="5432"

# -- Não altere a partir daqui, a menos que saiba o que está fazendo --

# Nome do superusuário do PostgreSQL (geralmente 'postgres')
PG_SUPERUSER="postgres"

echo "--------------------------------------------------"
echo "Iniciando a configuração do banco de dados PostgreSQL..."
echo "--------------------------------------------------"

# Executa os comandos SQL usando psql.
# O comando é executado como o superusuário do Postgres.
# Ele irá solicitar a senha do superusuário 'postgres' se necessário.
psql -U $PG_SUPERUSER -c "CREATE DATABASE $DB_NAME;"
psql -U $PG_SUPERUSER -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
psql -U $PG_SUPERUSER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Comando opcional para verificar se o usuário foi criado (lista de usuários)
# psql -U $PG_SUPERUSER -c "\du"

# Comando opcional para verificar se o banco de dados foi criado (lista de bancos)
# psql -U $PG_SUPERUSER -c "\l"


echo ""
echo "--------------------------------------------------"
echo "✅ Configuração concluída com sucesso!"
echo "--------------------------------------------------"
echo ""
echo "Detalhes da Conexão (Endpoint):"
echo "---------------------------------"
echo "Host (Endpoint):   $DB_HOST"
echo "Porta:             $DB_PORT"
echo "Nome do Banco:     $DB_NAME"
echo "Usuário:           $DB_USER"
echo "Senha:             $DB_PASS"
echo "---------------------------------"
echo ""
echo "String de Conexão (exemplo para aplicações):"
echo "postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""