import streamlit as st
import pandas as pd

def carteira():
    st.title("Carteira de Ativos")
    st.write("Esta página mostra a carteira de ativos com seus respectivos valores.")
    
    # Dados de exemplo para a carteira
    dados_carteira = {
        'ativo': [
            'PATRIMONIO LIQUIDO',
            'BANCO SANTAN',
            'BANCO_ITAU',
            'BANCO BRAD'
        ],
        'valor': [
            15000.00,
            12500.00,
            8750.00,
            2750.00
        ]
    }
    
    # Criar DataFrame
    df_carteira = pd.DataFrame(dados_carteira)
    
    # Armazenar no session state para usar na página conciliador (com valores numéricos)
    df_carteira_numerica = pd.DataFrame({
        'ativo': dados_carteira['ativo'],
        'valor': dados_carteira['valor']
    })
    st.session_state['df_carteira'] = df_carteira_numerica
    
    # Configurar formatação da coluna valor apenas para exibição
    df_carteira_display = df_carteira.copy()
    df_carteira_display['valor'] = df_carteira_display['valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Exibir a tabela
    st.subheader("📈 Carteira")
    
    # Usar st.dataframe para uma tabela mais interativa
    st.dataframe(
        df_carteira_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ativo": st.column_config.TextColumn("Ativo", width="medium"),
            "valor": st.column_config.TextColumn("Valor", width="medium")
        }
    )
    

# Função para ser chamada pelo main.py
if __name__ == "__main__":
    carteira()