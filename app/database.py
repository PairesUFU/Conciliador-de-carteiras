import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

def get_database_url():
    """Constrói a URL do banco de dados usando variáveis de ambiente"""
    db_host = os.getenv("DB_HOST", "postgres")
    db_name = os.getenv("DB_NAME", "bautomation_db")
    db_user = os.getenv("DB_USER", "bautomation_user")
    db_pass = os.getenv("DB_PASS", "admin123")
    db_port = os.getenv("DB_PORT", "5432")
    
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

@st.cache_data
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
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        return []

@st.cache_data
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
        st.error(f"Erro ao buscar informações do fundo: {e}")
        return None

def test_database_connection():
    """
    Testa a conexão com o banco de dados
    """
    try:
        engine = create_engine(get_database_url())
        
        with engine.begin() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
            
    except Exception as e:
        return False
