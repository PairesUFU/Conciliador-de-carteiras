# 🚀 Quick Start Guide

## Para Iniciantes (Apenas 3 passos!)

```bash
# 1. Configuração inicial
make setup

# 2. Iniciar o banco de dados
make start

# 3. Testar a conexão
make test
```

## Comandos Essenciais

```bash
make start    # ▶️  Iniciar banco
make stop     # ⏹️  Parar banco  
make logs     # 📋 Ver logs
make shell    # 🐘 Acessar PostgreSQL
make test     # 🧪 Testar conexão
```

## Informações de Conexão

- **Host:** localhost
- **Porta:** 5433
- **Banco:** bautomation_db
- **Usuário:** bautomation_user
- **Senha:** admin123

**String de Conexão:**
```
postgresql://bautomation_user:admin123@localhost:5433/bautomation_db
```

## Precisa de Ajuda?

```bash
make help                # Ver todos os comandos
./docker-manager.sh help # Ver script gerenciador
```
