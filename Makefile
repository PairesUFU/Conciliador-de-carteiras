# Makefile para Conciliador Database
.PHONY: help start stop restart logs shell status clean backup restore test setup

# Configurações
DOCKER_COMPOSE = docker-compose
MANAGER_SCRIPT = ./docker-manager.sh

# Comando padrão
.DEFAULT_GOAL := help

help: ## Exibe esta ajuda
	@echo "🐾 Conciliador - Comandos Disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup: ## Configuração inicial do projeto
	@echo "🚀 Configurando projeto..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "✅ Arquivo .env criado"; fi
	@chmod +x docker-manager.sh
	@chmod +x test_connection.py
	@echo "✅ Configuração concluída!"

start: ## Inicia os containers
	@$(MANAGER_SCRIPT) start

stop: ## Para os containers
	@$(MANAGER_SCRIPT) stop

restart: ## Reinicia os containers
	@$(MANAGER_SCRIPT) restart

logs: ## Exibe logs dos containers
	@$(MANAGER_SCRIPT) logs

shell: ## Acessa shell do PostgreSQL
	@$(MANAGER_SCRIPT) shell

status: ## Mostra status dos containers
	@$(MANAGER_SCRIPT) status

clean: ## Remove containers e volumes (CUIDADO!)
	@$(MANAGER_SCRIPT) clean

backup: ## Cria backup do banco de dados
	@$(MANAGER_SCRIPT) backup

restore: ## Restaura backup do banco de dados
	@$(MANAGER_SCRIPT) restore

test: ## Testa a conexão com o banco
	@echo "🧪 Testando conexão com o banco..."
	@python3 test_connection.py

install-tools: ## Instala ferramentas necessárias
	@echo "📦 Instalando dependências Python..."
	@pip3 install psycopg2-binary python-dotenv

dev: ## Inicia ambiente de desenvolvimento (com pgAdmin)
	@echo "🛠  Iniciando ambiente de desenvolvimento..."
	@$(DOCKER_COMPOSE) --profile tools up -d
	@echo "✅ Ambiente iniciado!"
	@echo "   PostgreSQL: localhost:5433"
	@echo "   pgAdmin: http://localhost:8080"

down: ## Para todos os containers
	@$(DOCKER_COMPOSE) down

build: ## Reconstrói as imagens
	@$(DOCKER_COMPOSE) build

ps: ## Lista containers em execução
	@$(DOCKER_COMPOSE) ps

top: ## Mostra processos dos containers
	@$(DOCKER_COMPOSE) top
