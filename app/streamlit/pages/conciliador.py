import streamlit as st
import pandas as pd

def conciliador():
    st.title("Conciliador")
    st.write("Esta página realiza a conciliação entre a carteira, balancete e mapeamento.")
    
    # Verificar se todos os dados necessários estão disponíveis no session state
    dados_disponiveis = {
        'df_balancete_completo': 'df_balancete_completo' in st.session_state,
        'df_mapeamento': 'df_mapeamento' in st.session_state,
        'df_carteira': 'df_carteira' in st.session_state
    }

    # Todos os dados necessários estão carregados?
    if all(dados_disponiveis.values()):
        st.success("✅ Todos os dados necessários estão carregados!")
        
        # Realizar a conciliação
        resultado_conciliacao = realizar_conciliacao(
            st.session_state['df_carteira'],
            st.session_state['df_balancete_completo'],
            st.session_state['df_mapeamento']
        )
        
        #Exibir o resultado da conciliação se ela foi realizada com sucesso
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
        # Inverter o DataFrame do mapeamento (de baixo para cima)
        df_mapeamento = df_mapeamento.iloc[::-1].reset_index(drop=True)
        
        # Verificar se o mapeamento tem as colunas necessárias
        colunas_necessarias = ['Nome Balancete', 'Ativo Carteira']

        # Coloca em minúsculas para facilitar a comparação e salva todas as colunas na variável 
        colunas_mapeamento = [col.lower() for col in df_mapeamento.columns]
        
        # Tentar encontrar as colunas com diferentes variações de nome
        nome_balancete_col = None
        ativo_carteira_col = None
        
        # Roda cada coluna do mapeamento e salva em col_lower para verificar se contém as palavras-chave necessárias
        for col in df_mapeamento.columns:
            col_lower = col.lower()
            if 'nome' in col_lower and 'balancete' in col_lower:
                nome_balancete_col = col
            elif 'ativo' in col_lower and 'carteira' in col_lower:
                ativo_carteira_col = col
        
        if nome_balancete_col is None or ativo_carteira_col is None:
            st.error("❌ Mapeamento não contém as colunas necessárias:")
            st.error("Colunas necessárias: 'Nome Balancete' e 'Ativo Carteira'")
            return None
        
        # Criar dicionário agrupado: ativo_carteira -> [lista de nomes do balancete]
        # Um ativo da carteira pode ter vários nomes correspondentes no balancete
        mapeamento_agrupado = {}
        for i, row in df_mapeamento.iterrows():
            nome_bal = row[nome_balancete_col]
            ativo_cart = row[ativo_carteira_col]
            
            # Verificar se ambos os valores são válidos
            if pd.notna(nome_bal) and pd.notna(ativo_cart) and str(nome_bal).strip() != '' and str(ativo_cart).strip() != '':
                ativo_limpo = str(ativo_cart).strip()
                nome_bal_limpo = str(nome_bal).strip()
                
                if ativo_limpo not in mapeamento_agrupado:
                    mapeamento_agrupado[ativo_limpo] = []
                
                # Evitar duplicatas
                if nome_bal_limpo not in mapeamento_agrupado[ativo_limpo]:
                    mapeamento_agrupado[ativo_limpo].append(nome_bal_limpo)
        
        # Preparar dados para conciliação
        resultados = []
        
        # Criar uma versão do balancete com nomes normalizados para busca case-insensitive
        df_balancete_normalizado = df_balancete.copy()
        df_balancete_normalizado['Nome_Normalizado'] = df_balancete_normalizado['Nome'].astype(str).str.strip().str.upper()
        
        # Iterar pelos itens da carteira
        for i, (_, row_carteira) in enumerate(df_carteira.iterrows()):
            ativo_carteira = row_carteira['ativo']
            valor_carteira = row_carteira['valor']
            
            # Verificar se o ativo da carteira está no mapeamento
            if ativo_carteira not in mapeamento_agrupado:
                # Ativo da carteira não encontrado no mapeamento
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Nome Balancete': 'NÃO MAPEADO',
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': 0.0,
                    'Diferença': valor_carteira,
                    'Numero de Registros': 0,
                    'Status': 'NÃO MAPEADO'
                })
                continue
            
            # Obter todos os nomes do balancete que correspondem a este ativo da carteira
            nomes_balancete = mapeamento_agrupado[ativo_carteira]
            
            # Buscar e somar TODOS os registros no balancete para TODOS os nomes mapeados
            saldo_total_balancete = 0.0
            nomes_encontrados = []
            total_registros_encontrados = 0
            
            for nome_balancete in nomes_balancete:
                # Normalizar o nome do balancete para busca case-insensitive
                nome_balancete_normalizado = str(nome_balancete).strip().upper()
                
                # Procurar TODOS os registros no balancete com este nome (case-insensitive)
                balancete_matches = df_balancete_normalizado[
                    df_balancete_normalizado['Nome_Normalizado'] == nome_balancete_normalizado
                ]
                
                # Se não encontrou com busca exata, tentar busca parcial (contains)
                if balancete_matches.empty:
                    balancete_matches = df_balancete_normalizado[
                        df_balancete_normalizado['Nome_Normalizado'].str.contains(nome_balancete_normalizado, na=False, regex=False)
                    ]
                
                # Se encontrou registros para este nome, somar os valores
                if not balancete_matches.empty:
                    nomes_encontrados.append(f"{nome_balancete}")
                    total_registros_encontrados += len(balancete_matches)
                    
                    for _, match_row in balancete_matches.iterrows():
                        saldo_atual = match_row['SldAtu']
                        
                        # Verificar se o valor é válido (não é NaN ou None)
                        if pd.isna(saldo_atual):
                            saldo_atual = 0.0
                        
                        # Converter para float se necessário
                        try:
                            saldo_atual = float(saldo_atual)
                            saldo_total_balancete += saldo_atual
                        except (ValueError, TypeError):
                            continue  # Pular valores inválidos
            
            # Se não encontrou nenhum nome no balancete
            if len(nomes_encontrados) == 0:
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Nome Balancete': f"NÃO ENCONTRADO", #({len(nomes_balancete)} nomes mapeados)",
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': 0.0,
                    'Diferença': valor_carteira,
                    'Numero de Registros': 0,
                    'Status': 'NÃO MAPEADO'
                })
            else:
                # Calcular diferença
                diferenca = valor_carteira - saldo_total_balancete
                
                # Determinar status
                if abs(diferenca) < 0.01:  # Considerar diferenças menores que 1 centavo como iguais
                    status = 'CONCILIADO'
                else:
                    status = 'DIVERGENTE'
                
                # Criar descrição dos nomes encontrados
                if len(nomes_encontrados) == 1:
                    nome_exibicao = nomes_encontrados[0]
                else:
                    nome_exibicao = f"MÚLTIPLOS: {', '.join(nomes_encontrados[:2])}"
                    if len(nomes_encontrados) > 2:
                        nome_exibicao += f" + {len(nomes_encontrados) - 2} outros"
                
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Nome Balancete': nome_exibicao,
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': saldo_total_balancete,
                    'Diferença': diferenca,
                    'Numero de Registros': total_registros_encontrados,
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
    mapeados = conciliados + divergentes  # Total de mapeados (conciliados + divergentes)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Itens", total_itens)
    
    with col2:
        st.metric("Mapeados", mapeados)
    
    with col3:
        st.metric("Não Mapeados", nao_mapeados)
    
    # Segunda linha de métricas
    col4, col5 = st.columns(2)
    
    with col4:
        st.metric("Conciliados", conciliados)
    
    with col5:
        st.metric("Divergentes", divergentes)
    
    # Filtro por status
    st.subheader("🔍 Filtrar por Status")
    status_filter = st.selectbox(
        "Selecione o status para filtrar:",
        ["TODOS", "MAPEADOS", "CONCILIADO", "DIVERGENTE", "NÃO MAPEADO"]
    )
    
    if status_filter == "TODOS":
        df_filtrado = df_resultado
    elif status_filter == "MAPEADOS":
        df_filtrado = df_resultado[df_resultado['Status'].isin(['CONCILIADO', 'DIVERGENTE'])]
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
            return ['background-color: #FF1616'] * len(row)
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