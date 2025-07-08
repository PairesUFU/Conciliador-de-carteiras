import os
import pandas as pd
from sqlalchemy import create_engine, text
import random
import time

POSTGRES_HOST = os.getenv("DB_HOST", "postgres")
POSTGRES_DB = os.getenv("DB_NAME", "bautomation_db")
POSTGRES_USER = os.getenv("DB_USER", "bautomation_user")
POSTGRES_PASSWORD = os.getenv("DB_PASS", "admin123")
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)

print(f"🔗 Conectando ao banco: {DATABASE_URL}")


def wait_for_database():
    """Aguarda o banco de dados ficar disponível"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("✅ Banco de dados está disponível!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"⏳ Aguardando banco de dados... tentativa {retry_count}/{max_retries} - {e}")
            time.sleep(2)
    
    raise Exception("❌ Não foi possível conectar ao banco de dados após 30 tentativas")


def get_engine():
    return create_engine(DATABASE_URL)


def create_table(engine, table_name: str, table_definition: str):
    check_table_query = f"""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = '{table_name}'
    );
    """

    with engine.begin() as connection:
        result = connection.execute(text(check_table_query))
        table_exists = result.scalar()

        if not table_exists:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS public.{table_name} (
               {table_definition}
            );
            """
            connection.execute(text(create_table_query))
            print(f"Table '{table_name}' created successfully.")
            return False
        else:
            print(f"Table '{table_name}' already exists.")
            return True


def create_funds_table_if_not_exists(engine):
    table_definition = """
        id SERIAL PRIMARY KEY,
        name text NOT NULL,
        slug text NULL,
        government_id text NULL,
        is_active boolean NOT NULL DEFAULT true,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    """
    return create_table(engine, table_name="funds", table_definition=table_definition)


def create_fund_quotas_table_if_not_exists(engine):
    table_definition = """
        id SERIAL PRIMARY KEY,
        fund_id INTEGER NOT NULL REFERENCES public.funds(id),
        type TEXT NOT NULL,
        quota_name TEXT NOT NULL,
        wallet_external_id TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    """
    return create_table(
        engine, table_name="fund_quotas", table_definition=table_definition
    )


def insert_fund(engine, id: int, name: str, slug: str, government_id: str, is_active: bool):
    insert_query = """
    INSERT INTO public.funds (id, name, slug, government_id, is_active)
    VALUES (:id, :name, :slug, :government_id, :is_active)
    """
    with engine.begin() as connection:
        connection.execute(
            text(insert_query),
            {
                "id": id,
                "name": name,
                "slug": slug,
                "government_id": government_id,
                "is_active": is_active,
            },
        )


def insert_fund_quota(engine, id: int, fund_id: int, type: str, quota_name: str, wallet_external_id: str):
    insert_query = """
    INSERT INTO public.fund_quotas (id, fund_id, type, quota_name, wallet_external_id)
    VALUES (:id, :fund_id, :type, :quota_name, :wallet_external_id)
    """
    with engine.begin() as connection:
        connection.execute(
            text(insert_query),
            {
                "id": id,
                "fund_id": fund_id,
                "type": type,
                "quota_name": quota_name,
                "wallet_external_id": wallet_external_id,
            },
        )


def load_funds_from_csv(engine, csv_path: str):
    """
    Carrega dados de funds de um arquivo CSV.
    CSV deve ter colunas: id, name, slug, government_id, is_active
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"Carregando {len(df)} funds do arquivo {csv_path}")
        
        for _, row in df.iterrows():
            insert_fund(
                engine,
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
                government_id=row['government_id'],
                is_active=row['is_active']
            )
        print(f"Dados de funds inseridos com sucesso!")
        
    except Exception as e:
        print(f"Erro ao carregar funds do CSV: {e}")


def load_fund_quotas_from_csv(engine, csv_path: str):
    """
    Carrega dados de fund_quotas de um arquivo CSV.
    CSV deve ter colunas: id, fund_id, type, quota_name, wallet_external_id
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"Carregando {len(df)} fund_quotas do arquivo {csv_path}")
        
        for _, row in df.iterrows():
            insert_fund_quota(
                engine,
                id=row['id'],
                fund_id=row['fund_id'],
                type=row['type'],
                quota_name=row['quota_name'],
                wallet_external_id=row['wallet_external_id']
            )
        print(f"Dados de fund_quotas inseridos com sucesso!")
        
    except Exception as e:
        print(f"Erro ao carregar fund_quotas do CSV: {e}")


def populate_tables(engine, funds_csv_path: str | None = None, fund_quotas_csv_path: str | None = None):
    create_funds_table_if_not_exists(engine)
    create_fund_quotas_table_if_not_exists(engine)
    
    if funds_csv_path and os.path.exists(funds_csv_path):
        load_funds_from_csv(engine, funds_csv_path)
    
    if fund_quotas_csv_path and os.path.exists(fund_quotas_csv_path):
        load_fund_quotas_from_csv(engine, fund_quotas_csv_path)


if __name__ == "__main__":
    print("🚀 Iniciando população do banco de dados...")
    
    # Aguarda o banco ficar disponível
    wait_for_database()
    
    engine = get_engine()
    
    funds_csv_path = "funds.csv"  # Arquivo na mesma pasta do script
    
    # Verifica se o arquivo funds.csv existe
    print(f"📁 Verificando arquivo: {funds_csv_path}")
    if os.path.exists(funds_csv_path):
        print(f"✅ Arquivo {funds_csv_path} encontrado!")
        populate_tables(engine, funds_csv_path, None)
        print("✅ Dados de funds carregados com sucesso!")
    else:
        print(f"⚠️ Arquivo {funds_csv_path} não encontrado. Criando apenas as tabelas...")
        # Vamos listar o que tem no diretório para debug
        print(f"📋 Conteúdo do diretório /app/:")
        for item in os.listdir("/app/"):
            print(f"  - {item}")
        populate_tables(engine, None, None)
    
    print("🎉 População do banco de dados concluída!")
