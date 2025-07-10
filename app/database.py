import os
import pandas as pd
import json  
from sqlalchemy import create_engine, text
import streamlit as st
from typing import Optional

def get_database_url():
    """Constrói a URL do banco de dados usando variáveis de ambiente"""
    db_host = os.getenv("DB_HOST", "postgres")
    db_name = os.getenv("DB_NAME", "bautomation_db")
    db_user = os.getenv("DB_USER", "bautomation_user")
    db_pass = os.getenv("DB_PASS", "admin123")
    db_port = os.getenv("DB_PORT", "5432")
    
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

def get_funds_list():
    """
    Busca a lista de fundos ativos do banco de dados
    Retorna uma lista com os nomes dos fundos
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        SELECT DISTINCT name 
        FROM public.funds 
        WHERE is_active = true 
        ORDER BY name
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query))
            funds = [row[0] for row in result.fetchall()]
            
        return funds
        
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        return []

def get_fund_info(fund_name: str):
    """
    Busca informações detalhadas de um fundo específico
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        SELECT id, name, slug, government_id, is_active 
        FROM public.funds 
        WHERE name = :fund_name AND is_active = true
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"fund_name": fund_name})
            fund_data = result.fetchone()
            
        if fund_data:
            return {
                "id": fund_data[0],
                "name": fund_data[1],
                "slug": fund_data[2],
                "government_id": fund_data[3],
                "is_active": fund_data[4]
            }
        else:
            return None
            
    except Exception as e:
        print(f"Erro ao buscar informações do fundo: {e}")
        return None


def get_fund_quotas(fund_id: int):
    """
    Busca todas as cotas de um fundo específico
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        SELECT id, type, quota_name, wallet_external_id 
        FROM public.fund_quotas 
        WHERE fund_id = :fund_id
        ORDER BY type, quota_name
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"fund_id": fund_id})
            quotas = result.fetchall()
            
        return quotas
        
    except Exception as e:
        print(f"Erro ao buscar cotas do fundo: {e}")
        return []
    
def save_mapping_to_db(fund_id: int, mapping_df: pd.DataFrame, name: str, filename: Optional[str] = None, sheet_name: Optional[str] = None):
    """
    Salva um mapeamento no banco de dados
    """
    try:
        engine = create_engine(get_database_url())
        
        # Converter DataFrame para JSON de forma mais robusta
        try:
            # Limpar dados problemáticos
            df_clean = mapping_df.copy()
            
            # Substituir NaN por None para melhor serialização JSON
            df_clean = df_clean.where(pd.notna(df_clean), None)
            
            # Converter para JSON
            mapping_json = df_clean.to_json(orient='records', force_ascii=False, date_format='iso')
            
            print(f"DEBUG: Salvando mapeamento '{name}' para fund_id {fund_id}")
            print(f"DEBUG: DataFrame shape: {mapping_df.shape}")
            print(f"DEBUG: JSON length: {len(mapping_json)}")
            
        except Exception as df_error:
            print(f"Erro ao converter DataFrame para JSON: {df_error}")
            return None
        
        query = """
        INSERT INTO public.mappings (fund_id, mapping_data, name, filename, sheet_name)
        VALUES (:fund_id, :mapping_data, :name, :filename, :sheet_name)
        ON CONFLICT (name, fund_id) 
        DO UPDATE SET 
            mapping_data = EXCLUDED.mapping_data,
            filename = EXCLUDED.filename,
            sheet_name = EXCLUDED.sheet_name,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {
                "fund_id": fund_id,
                "mapping_data": mapping_json,
                "name": name,
                "filename": filename,
                "sheet_name": sheet_name
            })
            row = result.fetchone()
            mapping_id = row[0] if row else None
            
        print(f"DEBUG: Mapeamento salvo com ID: {mapping_id}")
        return mapping_id
        
    except Exception as e:
        print(f"Erro ao salvar mapeamento no banco: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_mappings_by_fund(fund_id: int):
    """
    Busca todos os mapeamentos de um fundo específico
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        SELECT id, name, filename, sheet_name, created_at 
        FROM public.mappings 
        WHERE fund_id = :fund_id
        ORDER BY created_at DESC
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"fund_id": fund_id})
            mappings = result.fetchall()
            
        return [{"id": row[0], "name": row[1], "filename": row[2], 
                "sheet_name": row[3], "created_at": row[4]} for row in mappings]
        
    except Exception as e:
        print(f"Erro ao buscar mapeamentos do fundo: {e}")
        return []

def load_mapping_from_db(mapping_id: int):
    """
    Carrega um mapeamento específico do banco de dados
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        SELECT mapping_data, name 
        FROM public.mappings 
        WHERE id = :mapping_id
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"mapping_id": mapping_id})
            mapping_row = result.fetchone()
            
        if mapping_row:
            mapping_json = mapping_row[0]
            name = mapping_row[1]
            
            try:
                # Converter JSON de volta para DataFrame
                if isinstance(mapping_json, str):
                    # Se for string, fazer parse do JSON
                    import json
                    mapping_data = json.loads(mapping_json)
                else:
                    # Se já for objeto Python (dict/list)
                    mapping_data = mapping_json
                
                # Criar DataFrame a partir dos dados
                if isinstance(mapping_data, list) and len(mapping_data) > 0:
                    df = pd.DataFrame(mapping_data)
                elif isinstance(mapping_data, dict):
                    df = pd.DataFrame([mapping_data])
                else:
                    print(f"Formato de dados inesperado: {type(mapping_data)}")
                    return None, None
                    
                return df, name
                
            except Exception as json_error:
                print(f"Erro ao processar JSON do mapeamento {mapping_id}: {json_error}")
                return None, None
        else:
            print(f"Mapeamento com ID {mapping_id} não encontrado")
            return None, None
            
    except Exception as e:
        print(f"Erro ao carregar mapeamento do banco: {e}")
        return None, None

def check_mapping_exists(fund_id: int, name: str):
    """
    Verifica se um mapeamento com esse nome já existe para o fundo
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        SELECT EXISTS (
            SELECT 1 FROM public.mappings 
            WHERE fund_id = :fund_id AND name = :name
        )
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"fund_id": fund_id, "name": name})
            exists = result.scalar()
            
        return exists
        
    except Exception as e:
        print(f"Erro ao verificar existência do mapeamento: {e}")
        return False

def delete_mapping_from_db(mapping_id: int):
    """
    Exclui um mapeamento do banco de dados
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        DELETE FROM public.mappings 
        WHERE id = :mapping_id
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"mapping_id": mapping_id})
            
        # Retornar True se alguma linha foi afetada (deletada)
        return result.rowcount > 0
        
    except Exception as e:
        print(f"Erro ao excluir mapeamento do banco: {e}")
        return False

def delete_all_mappings_from_fund(fund_id: int):
    """
    Exclui todos os mapeamentos de um fundo específico
    """
    try:
        engine = create_engine(get_database_url())
        
        query = """
        DELETE FROM public.mappings 
        WHERE fund_id = :fund_id
        """
        
        with engine.begin() as connection:
            result = connection.execute(text(query), {"fund_id": fund_id})
            
        # Retornar o número de linhas deletadas
        return result.rowcount
        
    except Exception as e:
        print(f"Erro ao excluir todos os mapeamentos do fundo: {e}")
        return 0