# 🐾 Pokedex Database

Sistema de banco de dados PostgreSQL containerizado para projetos Pokedex.

## 📋 Índice

- [Requisitos](#requisitos)
- [Instalação com Docker](#instalação-com-docker)
- [Uso](#uso)
- [Configuração](#configuração)
- [Comandos Úteis](#comandos-úteis)
- [Backup e Restore](#backup-e-restore)
- [Instalação Manual](#instalação-manual)

## 🛠 Requisitos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Instalação com Docker

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd Pokedex-Repair
```

### 2. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# (opcional - os valores padrão funcionam perfeitamente)
```

### 3. Inicie o banco de dados

```bash
# Usando o script gerenciador (recomendado)
./docker-manager.sh start

# OU usando docker-compose diretamente
docker-compose up -d
```

## 🎯 Uso

### Comandos Rápidos

```bash
# Iniciar containers
./docker-manager.sh start

# Parar containers
./docker-manager.sh stop

# Ver logs
./docker-manager.sh logs

# Acessar shell do PostgreSQL
./docker-manager.sh shell

# Ver status dos containers
./docker-manager.sh status
```

### Informações de Conexão

Após iniciar os containers, use estas informações para conectar:

- **Host:** localhost
- **Porta:** 5433 (ou 5432 se não houver conflito)
- **Banco:** bautomation_db
- **Usuário:** bautomation_user
- **Senha:** admin123

**String de Conexão:**
```
postgresql://bautomation_user:admin123@localhost:5433/bautomation_db
```

### pgAdmin (Opcional)

Para habilitar o pgAdmin (interface web para administração):

```bash
# Inicia com pgAdmin incluído
docker-compose --profile tools up -d
```

Acesse: http://localhost:8080
- **Email:** admin@pokedex.com
- **Senha:** admin123

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Configurações do Banco de Dados
DB_NAME=bautomation_db
DB_USER=bautomation_user
DB_PASS=admin123
DB_HOST=localhost
DB_PORT=5433

# Configurações do pgAdmin (opcional)
PGADMIN_EMAIL=admin@pokedex.com
PGADMIN_PASSWORD=admin123
PGADMIN_PORT=8080
```

### Scripts de Inicialização

Coloque scripts SQL ou shell em `database/init-scripts/` para serem executados automaticamente na primeira inicialização:

- `01-init.sh` - Script de inicialização básica
- `02-schema.sql` - Exemplo de schema SQL

## 📋 Comandos Úteis

### Script Gerenciador

```bash
./docker-manager.sh help     # Exibe ajuda
./docker-manager.sh start    # Inicia containers
./docker-manager.sh stop     # Para containers
./docker-manager.sh restart  # Reinicia containers
./docker-manager.sh logs     # Exibe logs
./docker-manager.sh shell    # Acessa shell do PostgreSQL
./docker-manager.sh status   # Mostra status
./docker-manager.sh clean    # Remove tudo (CUIDADO!)
./docker-manager.sh backup   # Cria backup
./docker-manager.sh restore  # Restaura backup
```

### Docker Compose Direto

```bash
# Iniciar
docker-compose up -d

# Parar
docker-compose down

# Ver logs
docker-compose logs -f

# Acessar PostgreSQL
docker-compose exec postgres psql -U bautomation_user -d bautomation_db
```

## 💾 Backup e Restore

### Criar Backup

```bash
# Usando o script gerenciador
./docker-manager.sh backup

# OU manualmente
docker-compose exec postgres pg_dump -U bautomation_user bautomation_db > backup.sql
```

### Restaurar Backup

```bash
# Usando o script gerenciador
./docker-manager.sh restore

# OU manualmente
docker-compose exec -T postgres psql -U bautomation_user bautomation_db < backup.sql
```

## 🛠 Instalação Manual

Se preferir instalar PostgreSQL localmente sem Docker:

```bash
# Torne o script executável
chmod +x database/setup_db.sh

# Execute o script
./database/setup_db.sh
```

**Nota:** Você precisará ter PostgreSQL instalado localmente.

## 📁 Estrutura do Projeto

```
Pokedex-Repair/
├── database/
│   ├── init-scripts/
│   │   ├── 01-init.sh      # Script de inicialização
│   │   └── 02-schema.sql   # Schema SQL opcional
│   └── setup_db.sh         # Setup manual (sem Docker)
├── docker-compose.yml      # Configuração Docker Compose
├── docker-manager.sh       # Script gerenciador
├── .env.example           # Exemplo de variáveis
├── .env                   # Suas variáveis (não commitado)
└── README.md              # Esta documentação
```

## 🔧 Troubleshooting

### Container não inicia
```bash
# Verifique os logs
./docker-manager.sh logs

# Verifique se a porta está ocupada
lsof -i :5433
```

### Porta 5432 já está em uso
Se você já tem PostgreSQL instalado localmente, a porta 5432 pode estar ocupada:

```bash
# Opção 1: Parar PostgreSQL local temporariamente
brew services stop postgresql

# Opção 2: Usar porta diferente (recomendado)
# Edite o arquivo .env e mude DB_PORT=5432 para DB_PORT=5433
```

### Problemas de permissão
```bash
# Recrie os volumes
./docker-manager.sh clean
./docker-manager.sh start
```

### Reset completo
```bash
# Remove tudo e reinicia
./docker-manager.sh clean
./docker-manager.sh start
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

Como pode testar:
# 1. Clonar o repositório
git clone <seu-repositorio>
cd Pokedex-Repair

# 2. Configuração automática (uma única vez)
make setup

# 3. Iniciar o banco de dados
make start

# 4. Testar se está funcionando
make test