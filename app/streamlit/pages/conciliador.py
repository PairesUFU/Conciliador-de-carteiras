import streamlit as st
import pandas as pd

def conciliador():
    st.title("Conciliador")
    st.write("Esta página realiza a conciliação entre a carteira, balancete e mapeamento.")
    
    # Verificar se todos os dados necessários estão disponíveis
    dados_disponiveis = {
        'df_balancete_completo': 'df_balancete_completo' in st.session_state,
        'df_mapeamento': 'df_mapeamento' in st.session_state,
        'df_carteira': 'df_carteira' in st.session_state
    }
    
    if all(dados_disponiveis.values()):
        st.success("✅ Todos os dados necessários estão carregados!")
        
        # Realizar a conciliação
        resultado_conciliacao = realizar_conciliacao(
            st.session_state['df_carteira'],
            st.session_state['df_balancete_completo'],
            st.session_state['df_mapeamento']
        )
        
        if resultado_conciliacao is not None:
            exibir_resultado_conciliacao(resultado_conciliacao)
        
    else:
        st.warning("⚠️ Nem todos os dados necessários estão disponíveis.")
        
        # Mostrar status de cada tipo de dado
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if dados_disponiveis['df_carteira']:
                st.success("✅ Carteira carregada")
            else:
                st.error("❌ Carteira não carregada")
                st.info("Vá para a página 'Carteira' para carregar os dados")
        
        with col2:
            if dados_disponiveis['df_balancete_completo']:
                st.success("✅ Balancete carregado")
            else:
                st.error("❌ Balancete não carregado")
                st.info("Vá para a página 'Lançamento de Dados' e carregue o balancete")
        
        with col3:
            if dados_disponiveis['df_mapeamento']:
                st.success("✅ Mapeamento carregado")
            else:
                st.error("❌ Mapeamento não carregado")
                st.info("Vá para a página 'Lançamento de Dados' e carregue o mapeamento")


def realizar_conciliacao(df_carteira, df_balancete, df_mapeamento):
    """
    Realiza a conciliação entre carteira, balancete e mapeamento
    """
    try:
        # Verificar se o mapeamento tem as colunas necessárias
        colunas_necessarias = ['nome balancete', 'Ativo Carteira']
        colunas_mapeamento = [col.lower() for col in df_mapeamento.columns]
        
        # Tentar encontrar as colunas com diferentes variações de nome
        nome_balancete_col = None
        ativo_carteira_col = None
        
        for col in df_mapeamento.columns:
            col_lower = col.lower()
            if 'nome' in col_lower and 'balancete' in col_lower:
                nome_balancete_col = col
            elif 'ativo' in col_lower and 'carteira' in col_lower:
                ativo_carteira_col = col
        
        if nome_balancete_col is None or ativo_carteira_col is None:
            st.error("❌ Mapeamento não contém as colunas necessárias:")
            st.error("Colunas necessárias: 'Nome Balancete' e 'Ativo Carteira'")
            st.error(f"Colunas encontradas: {list(df_mapeamento.columns)}")
            return None
        
        # Criar dicionário de mapeamento
        mapeamento_dict = dict(zip(df_mapeamento[nome_balancete_col], df_mapeamento[ativo_carteira_col]))
        
        # Preparar dados para conciliação
        resultados = []
        
        # Iterar pelos itens da carteira
        for i, (_, row_carteira) in enumerate(df_carteira.iterrows()):
            ativo_carteira = row_carteira['ativo']
            valor_carteira = row_carteira['valor']
            
            # Procurar o nome correspondente no balancete através do mapeamento
            nome_balancete = None
            for nome_bal, ativo_cart in mapeamento_dict.items():
                if str(ativo_cart).strip() == str(ativo_carteira).strip():
                    nome_balancete = nome_bal
                    break
            
            if nome_balancete is None:
                # Ativo da carteira não encontrado no mapeamento
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Nome Balancete': 'NÃO MAPEADO',
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': 0.0,
                    'Diferença': valor_carteira,
                    'Status': 'NÃO MAPEADO'
                })
                continue
            
            # Procurar o saldo no balancete
            # Primeiro, tentar busca exata
            balancete_match = df_balancete[df_balancete['Nome'] == nome_balancete]
            
            # Se não encontrou, tentar busca flexível
            if balancete_match.empty:
                # Remover acentos e espaços extras, converter para maiúsculas
                nome_limpo = str(nome_balancete).strip().upper()
                df_balancete_limpo = df_balancete.copy()
                df_balancete_limpo['Nome_Limpo'] = df_balancete_limpo['Nome'].astype(str).str.strip().str.upper()
                
                # Tentar busca exata com nome limpo
                balancete_match = df_balancete[df_balancete_limpo['Nome_Limpo'] == nome_limpo]
                
                # Se ainda não encontrou, tentar busca parcial
                if balancete_match.empty:
                    balancete_match = df_balancete[df_balancete_limpo['Nome_Limpo'].str.contains(nome_limpo, na=False)]
            
            if balancete_match.empty:
                # Nome do balancete não encontrado
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Nome Balancete': nome_balancete,
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': 0.0,
                    'Diferença': valor_carteira,
                    'Status': 'NÃO ENCONTRADO NO BALANCETE'
                })
            else:
                # Encontrado - calcular diferença
                saldo_balancete = balancete_match['SldAtu'].iloc[0]
                
                # Verificar se o valor é válido (não é NaN ou None)
                if pd.isna(saldo_balancete):
                    saldo_balancete = 0.0
                
                # Converter para float se necessário
                try:
                    saldo_balancete = float(saldo_balancete)
                except (ValueError, TypeError):
                    saldo_balancete = 0.0
                
                diferenca = valor_carteira - saldo_balancete
                
                # Determinar status
                if abs(diferenca) < 0.01:  # Considerar diferenças menores que 1 centavo como iguais
                    status = 'CONCILIADO'
                else:
                    status = 'DIVERGENTE'
                
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Nome Balancete': nome_balancete,
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': saldo_balancete,
                    'Diferença': diferenca,
                    'Status': status
                })
        
        return pd.DataFrame(resultados)
        
    except Exception as e:
        st.error(f"Erro ao realizar conciliação: {str(e)}")
        return None


def exibir_resultado_conciliacao(df_resultado):
    """
    Exibe os resultados da conciliação
    """
    st.subheader("📊 Resultado da Conciliação")
    
    # Estatísticas gerais
    total_itens = len(df_resultado)
    conciliados = len(df_resultado[df_resultado['Status'] == 'CONCILIADO'])
    divergentes = len(df_resultado[df_resultado['Status'] == 'DIVERGENTE'])
    nao_mapeados = len(df_resultado[df_resultado['Status'] == 'NÃO MAPEADO'])
    nao_encontrados = len(df_resultado[df_resultado['Status'] == 'NÃO ENCONTRADO NO BALANCETE'])
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Itens", total_itens)
    
    with col2:
        st.metric("Conciliados", conciliados)
    
    with col3:
        st.metric("Divergentes", divergentes)
    
    with col4:
        st.metric("Não Mapeados", nao_mapeados + nao_encontrados)
    
    # Filtro por status
    st.subheader("🔍 Filtrar por Status")
    status_filter = st.selectbox(
        "Selecione o status para filtrar:",
        ["TODOS", "CONCILIADO", "DIVERGENTE", "NÃO MAPEADO", "NÃO ENCONTRADO NO BALANCETE"]
    )
    
    if status_filter == "TODOS":
        df_filtrado = df_resultado
    else:
        df_filtrado = df_resultado[df_resultado['Status'] == status_filter]
    
    # Formatação da tabela para exibição
    df_display = df_filtrado.copy()
    df_display['Valor Carteira'] = df_display['Valor Carteira'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    df_display['Saldo Balancete'] = df_display['Saldo Balancete'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    df_display['Diferença'] = df_display['Diferença'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    # Colorir a tabela baseado no status
    def colorir_status(row):
        if row['Status'] == 'CONCILIADO':
            return ['background-color: #228B22'] * len(row)
        elif row['Status'] == 'DIVERGENTE':
            return ['background-color: #8B0000'] * len(row)
        elif row['Status'] == 'NÃO MAPEADO':
            return ['background-color: #FFEA33'] * len(row)
        else:
            return ['background-color: #FFEA33'] * len(row)
    
    st.dataframe(
        df_display.style.apply(colorir_status, axis=1),
        use_container_width=True,
        hide_index=True
    )


# Função para ser chamada pelo main.py
if __name__ == "__main__":
    conciliador()