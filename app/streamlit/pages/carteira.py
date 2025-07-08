import streamlit as st
import pandas as pd

def carteira():
    st.title("Carteira de Ativos")
    st.write("Esta página mostra a carteira de ativos com seus respectivos valores.")
    
    # Dados de exemplo para a carteira
    dados_carteira = {
    'ativo': [
        'PATRIMÔNIO LÍQUIDO',
        'PATLIQ',
        'BC DO BRASIL',
        'BANCO_ITAU',
        'BANCO BRAD',
        'BANCO SANTAN',
        'BANCO ARBI',
        'Compromissada',
        'LFT',
        'LTN',
        'NTN',
        'CDB',
        'PLATINUM',
        'À VENC',
        'VENCIDO',
        'PDD',
        'Valor a Rec',
        'Ajustes de Cota',
        'AJCOD',
        'OUTROS DEVED',
        'IMÓVEL',
        'CVM',
        'ANBIMA',
        'RATING',
        'SEGDIREITO',
        'TÍTULOS PÚBLICOS',
        'COTAS DE FUNDO',
        'IRCALC',
        'RESGA',
        'AJCOT',
        'TXBANC',
        'AUDIT',
        'TXCUST',
        'SELIC',
        'CETIP',
        'DESP ADV',
        'TXCONS_MAI25',
        'TXAGCOB',
        'VALID',
        'SEGURODIRCRE',
        'SEGFRANQ',
        'TXADM',
        'TXGEST_MAI25',
        'DC A BAIXAR',
        'DESPPROT',
        'SOBE',
        'TXANBI',
        'SOBER',
        'TARIFBANC',
        'CR_CONCILIAR',
        'SEGURO APG'
    ],
    'valor': [
        15200.00, 14950.00, 9800.00, 8750.00, 2750.00, 12500.00, 3100.00,
        9000.00, 7200.00, 6300.00, 8100.00, 5400.00, 11500.00,
        4500.00, 3200.00, 1000.00, 2500.00, 1800.00, 1600.00, 1900.00, 20000.00,
        1300.00, 800.00, 700.00, 1500.00, 8700.00, 9200.00, 400.00, 450.00,
        600.00, 300.00, 280.00, 420.00, 700.00, 750.00, 1100.00, 500.00, 450.00,
        310.00, 700.00, 350.00, 600.00, 550.00, 1000.00, 900.00, 650.00,
        850.00, 300.00, 450.00, 480.00, 600.00
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