#!/bin/bash

# ==============================================================================
# SCRIPT DE GERENCIAMENTO DO DOCKER - POKEDEX DATABASE
# ==============================================================================
# Este script facilita o gerenciamento do ambiente Docker
# ==============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir ajuda
show_help() {
    echo -e "${BLUE}🐳 Pokedex Database Docker Manager${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start     - Inicia os containers"
    echo "  stop      - Para os containers"
    echo "  restart   - Reinicia os containers"
    echo "  logs      - Exibe os logs dos containers"
    echo "  shell     - Acessa o shell do PostgreSQL"
    echo "  status    - Mostra o status dos containers"
    echo "  clean     - Remove containers e volumes (CUIDADO!)"
    echo "  backup    - Cria backup do banco de dados"
    echo "  restore   - Restaura backup do banco de dados"
    echo "  help      - Exibe esta ajuda"
    echo ""
}

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker não está rodando. Por favor, inicie o Docker primeiro.${NC}"
        exit 1
    fi
}

# Função para verificar se o arquivo .env existe
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  Arquivo .env não encontrado. Criando a partir do .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Arquivo .env criado. Ajuste as configurações se necessário.${NC}"
    fi
}

# Função para iniciar containers
start_containers() {
    echo -e "${BLUE}🚀 Iniciando containers...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Containers iniciados com sucesso!${NC}"
    show_connection_info
}

# Função para parar containers
stop_containers() {
    echo -e "${YELLOW}🛑 Parando containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Containers parados com sucesso!${NC}"
}

# Função para reiniciar containers
restart_containers() {
    echo -e "${BLUE}🔄 Reiniciando containers...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ Containers reiniciados com sucesso!${NC}"
}

# Função para exibir logs
show_logs() {
    echo -e "${BLUE}📋 Exibindo logs dos containers...${NC}"
    docker-compose logs -f
}

# Função para acessar shell do PostgreSQL
postgres_shell() {
    echo -e "${BLUE}🐘 Acessando shell do PostgreSQL...${NC}"
    docker-compose exec postgres psql -U ${DB_USER:-bautomation_user} -d ${DB_NAME:-bautomation_db}
}

# Função para mostrar status
show_status() {
    echo -e "${BLUE}📊 Status dos containers:${NC}"
    docker-compose ps
}

# Função para limpar tudo
clean_all() {
    echo -e "${RED}⚠️  ATENÇÃO: Isso irá remover todos os containers e volumes (dados serão perdidos)!${NC}"
    read -p "Tem certeza? (digite 'yes' para confirmar): " confirm
    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}🧹 Limpando containers e volumes...${NC}"
        docker-compose down -v --remove-orphans
        docker-compose rm -f
        echo -e "${GREEN}✅ Limpeza concluída!${NC}"
    else
        echo -e "${BLUE}ℹ️  Operação cancelada.${NC}"
    fi
}

# Função para criar backup
create_backup() {
    echo -e "${BLUE}💾 Criando backup do banco de dados...${NC}"
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec postgres pg_dump -U ${DB_USER:-bautomation_user} ${DB_NAME:-bautomation_db} > $BACKUP_FILE
    echo -e "${GREEN}✅ Backup criado: $BACKUP_FILE${NC}"
}

# Função para restaurar backup
restore_backup() {
    echo -e "${BLUE}📥 Restaurando backup do banco de dados...${NC}"
    read -p "Digite o nome do arquivo de backup: " backup_file
    if [ -f "$backup_file" ]; then
        docker-compose exec -T postgres psql -U ${DB_USER:-bautomation_user} ${DB_NAME:-bautomation_db} < $backup_file
        echo -e "${GREEN}✅ Backup restaurado com sucesso!${NC}"
    else
        echo -e "${RED}❌ Arquivo de backup não encontrado: $backup_file${NC}"
    fi
}

# Função para exibir informações de conexão
show_connection_info() {
    echo ""
    echo -e "${GREEN}🔗 Informações de Conexão:${NC}"
    echo -e "${BLUE}────────────────────────────────${NC}"
    echo "Host: localhost"
    echo "Porta: ${DB_PORT:-5433}"
    echo "Banco: ${DB_NAME:-bautomation_db}"
    echo "Usuário: ${DB_USER:-bautomation_user}"
    echo "Senha: ${DB_PASS:-admin123}"
    echo ""
    echo -e "${BLUE}String de Conexão:${NC}"
    echo "postgresql://${DB_USER:-bautomation_user}:${DB_PASS:-admin123}@localhost:${DB_PORT:-5433}/${DB_NAME:-bautomation_db}"
    echo ""
    echo -e "${BLUE}pgAdmin (se habilitado):${NC}"
    echo "URL: http://localhost:${PGADMIN_PORT:-8080}"
    echo "Email: ${PGADMIN_EMAIL:-admin@pokedex.com}"
    echo "Senha: ${PGADMIN_PASSWORD:-admin123}"
    echo ""
}

# Função principal
main() {
    case $1 in
        start)
            check_docker
            check_env
            start_containers
            ;;
        stop)
            check_docker
            stop_containers
            ;;
        restart)
            check_docker
            restart_containers
            ;;
        logs)
            check_docker
            show_logs
            ;;
        shell)
            check_docker
            postgres_shell
            ;;
        status)
            check_docker
            show_status
            ;;
        clean)
            check_docker
            clean_all
            ;;
        backup)
            check_docker
            create_backup
            ;;
        restore)
            check_docker
            restore_backup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            if [ -z "$1" ]; then
                show_help
            else
                echo -e "${RED}❌ Comando desconhecido: $1${NC}"
                echo ""
                show_help
                exit 1
            fi
            ;;
    esac
}

# Executar função principal com todos os argumentos
main "$@"
