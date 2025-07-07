#!/usr/bin/env python3
"""
Script de teste para conexão com o banco PostgreSQL dockerizado
"""

import os
import sys
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 não está instalado. Instale com: pip install psycopg2-binary")
    sys.exit(1)

# Carregar variáveis do arquivo .env se existir
def load_env():
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_connection():
    """Testa a conexão com o banco de dados"""
    
    # Carregar .env primeiro
    load_env()
    
    # Configurações de conexão (ou pega do .env)
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5433')),
        'database': os.getenv('DB_NAME', 'bautomation_db'),
        'user': os.getenv('DB_USER', 'bautomation_user'),
        'password': os.getenv('DB_PASS', 'admin123')
    }
    
    try:
        print("🔄 Testando conexão com PostgreSQL...")
        print(f"   Host: {config['host']}:{config['port']}")
        print(f"   Database: {config['database']}")
        print(f"   User: {config['user']}")
        
        # Conecta ao banco
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Testa uma query simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("✅ Conexão bem-sucedida!")
        print(f"   Versão do PostgreSQL: {version}")
        
        # Testa criação de tabela (opcional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insere um registro de teste
        cursor.execute(
            "INSERT INTO test_connection (message) VALUES (%s);",
            ("Teste de conexão realizado com sucesso!",)
        )
        
        # Confirma as mudanças
        conn.commit()
        
        # Consulta os dados
        cursor.execute("SELECT COUNT(*) FROM test_connection;")
        count = cursor.fetchone()[0]
        
        print(f"✅ Tabela de teste criada/atualizada. Total de registros: {count}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Todos os testes passaram! O banco está funcionando corretamente.")
        
    except psycopg2.Error as e:
        print(f"❌ Erro de conexão: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
