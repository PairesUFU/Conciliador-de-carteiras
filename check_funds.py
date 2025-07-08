#!/usr/bin/env python3

import sys
import os
sys.path.append('app')

from app.database import get_funds_list, get_database_url
from app.encoding_utils import load_csv_with_encoding_fix
from sqlalchemy import create_engine, text
import pandas as pd

def check_database_funds():
    """Verifica se os fundos estão carregados no banco de dados"""
    try:
        engine = create_engine(get_database_url())
        
        # Contar total de fundos na tabela
        with engine.begin() as connection:
            total_query = "SELECT COUNT(*) FROM public.funds"
            total_result = connection.execute(text(total_query))
            total_funds = total_result.scalar()
            
            # Contar fundos ativos
            active_query = "SELECT COUNT(*) FROM public.funds WHERE is_active = true"
            active_result = connection.execute(text(active_query))
            active_funds = active_result.scalar()
            
            # Listar alguns fundos para verificação
            sample_query = "SELECT id, name, slug, government_id, is_active FROM public.funds LIMIT 10"
            sample_result = connection.execute(text(sample_query))
            sample_funds = sample_result.fetchall()
            
        print(f"📊 Estatísticas do banco de dados:")
        print(f"   Total de fundos: {total_funds}")
        print(f"   Fundos ativos: {active_funds}")
        
        if sample_funds:
            print(f"\n📋 Amostra de fundos no banco:")
            for fund in sample_funds:
                status = "✅ Ativo" if fund[4] else "❌ Inativo"
                print(f"   ID: {fund[0]} | Nome: {fund[1]} | {status}")
        
        return total_funds > 0
        
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return False

def check_csv_funds():
    """Verifica quantos fundos estão no arquivo CSV"""
    csv_path = "app/funds.csv"
    try:
        df = load_csv_with_encoding_fix(csv_path, encoding='cp1252')
        total_csv = len(df)
        active_csv = len(df[df['is_active'] == True])
        
        print(f"\n📁 Estatísticas do arquivo CSV:")
        print(f"   Total de fundos no CSV: {total_csv}")
        print(f"   Fundos ativos no CSV: {active_csv}")
        
        return total_csv
        
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo CSV: {e}")
        return 0

def test_streamlit_function():
    """Testa a função que o Streamlit usa para buscar fundos"""
    try:
        funds_list = get_funds_list()
        print(f"\n🔍 Teste da função get_funds_list():")
        print(f"   Número de fundos retornados: {len(funds_list)}")
        
        if funds_list:
            print(f"   Primeiros 5 fundos:")
            for i, fund in enumerate(funds_list[:5]):
                print(f"     {i+1}. {fund}")
                
        return len(funds_list)
        
    except Exception as e:
        print(f"❌ Erro ao testar função get_funds_list(): {e}")
        return 0

if __name__ == "__main__":
    print("🔍 Verificando status dos fundos...\n")
    
    # Verificar CSV
    csv_count = check_csv_funds()
    
    # Verificar banco de dados
    db_exists = check_database_funds()
    
    # Testar função do Streamlit
    streamlit_count = test_streamlit_function()
    
    print(f"\n📝 Resumo:")
    print(f"   Fundos no CSV: {csv_count}")
    print(f"   Banco funcionando: {'✅ Sim' if db_exists else '❌ Não'}")
    print(f"   Fundos retornados para Streamlit: {streamlit_count}")
    
    if csv_count > 0 and streamlit_count == 0:
        print(f"\n⚠️  PROBLEMA IDENTIFICADO:")
        print(f"   O CSV tem {csv_count} fundos, mas o Streamlit não está recebendo nenhum.")
        print(f"   Isso indica que os dados não foram populados no banco ou há problema na conexão.")
    elif csv_count == streamlit_count:
        print(f"\n✅ TUDO OK:")
        print(f"   O número de fundos no CSV corresponde ao retornado para o Streamlit.")
    else:
        print(f"\n⚠️  DISCREPÂNCIA:")
        print(f"   CSV: {csv_count} fundos | Streamlit: {streamlit_count} fundos")
