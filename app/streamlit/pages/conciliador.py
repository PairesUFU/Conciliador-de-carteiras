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
        colunas_necessarias = ['Conta', 'Ativo Carteira']

        # Coloca em minúsculas para facilitar a comparação e salva todas as colunas na variável 
        colunas_mapeamento = [col.lower() for col in df_mapeamento.columns]
        
        # Tentar encontrar as colunas com diferentes variações de nome
        conta_balancete_col = None
        ativo_carteira_col = None
        
        # Roda cada coluna do mapeamento e salva em col_lower para verificar se contém as palavras-chave necessárias
        for col in df_mapeamento.columns:
            col_lower = col.lower()
            if 'conta' in col_lower:
                conta_balancete_col = col
            elif 'ativo' in col_lower and 'carteira' in col_lower:
                ativo_carteira_col = col
        
        if conta_balancete_col is None or ativo_carteira_col is None:
            st.error("❌ Mapeamento não contém as colunas necessárias:")
            st.error("Colunas necessárias: 'Conta' e 'Ativo Carteira'")
            return None
        
        # Criar dicionário agrupado: ativo_carteira -> [lista de contas do balancete]
        mapeamento_agrupado = {}
        for i, row in df_mapeamento.iterrows():
            conta_bal = row[conta_balancete_col]
            ativo_cart = row[ativo_carteira_col]
            
            # Verificar se ambos os valores são válidos
            if pd.notna(conta_bal) and pd.notna(ativo_cart) and str(conta_bal).strip() != '' and str(ativo_cart).strip() != '':
                ativo_limpo = str(ativo_cart).strip()
                conta_bal_limpo = str(conta_bal).strip()
                
                if ativo_limpo not in mapeamento_agrupado:
                    mapeamento_agrupado[ativo_limpo] = []
                
                # Evitar duplicatas
                if conta_bal_limpo not in mapeamento_agrupado[ativo_limpo]:
                    mapeamento_agrupado[ativo_limpo].append(conta_bal_limpo)
        
        # Preparar dados para conciliação
        resultados = []
        
        # Detectar qual coluna de conta usar no balancete
        conta_col_balancete = None
        if 'Conta' in df_balancete.columns:
            conta_col_balancete = 'Conta'
        elif 'Nome' in df_balancete.columns:
            conta_col_balancete = 'Nome'
        else:
            st.error("❌ Balancete não contém coluna 'Conta' nem 'Nome'")
            st.info(f"Colunas disponíveis no balancete: {list(df_balancete.columns)}")
            return None
        
        # Detectar qual coluna de saldo usar no balancete
        saldo_col_balancete = None
        if 'SldAtu' in df_balancete.columns:
            saldo_col_balancete = 'SldAtu'
        elif 'SldAnt' in df_balancete.columns:
            saldo_col_balancete = 'SldAnt'
        else:
            st.error("❌ Balancete não contém coluna 'SldAtu' nem 'SldAnt'")
            st.info(f"Colunas disponíveis no balancete: {list(df_balancete.columns)}")
            return None
        
        # Mostrar quais colunas estão sendo usadas
        st.info(f"📋 Usando coluna '{conta_col_balancete}' para contas e '{saldo_col_balancete}' para saldos")
        
        # Criar uma versão do balancete com contas normalizadas para busca
        df_balancete_normalizado = df_balancete.copy()
        
        # Função para normalizar números (tanto do mapeamento quanto do balancete)
        def normalizar_conta(conta):
            if pd.isna(conta):
                return ''
            conta_str = str(conta).strip()
            # Converter vírgula para ponto para padronizar
            conta_str = conta_str.replace(',', '.')
            # Tentar converter para float e depois para int se for número inteiro
            try:
                conta_float = float(conta_str)
                if conta_float.is_integer():
                    return str(int(conta_float))
                else:
                    return str(conta_float)
            except ValueError:
                return conta_str
        
        # Normalizar as contas do balancete
        df_balancete_normalizado['Conta_Normalizado'] = df_balancete_normalizado[conta_col_balancete].apply(normalizar_conta)
        
        # Iterar pelos itens da carteira
        for i, (_, row_carteira) in enumerate(df_carteira.iterrows()):
            ativo_carteira = row_carteira['ativo']
            valor_carteira = row_carteira['valor']
            
            # Verificar se o ativo da carteira está no mapeamento
            if ativo_carteira not in mapeamento_agrupado:
                # Ativo da carteira não encontrado no mapeamento
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Conta Balancete': 'NÃO MAPEADO',
                    'Valor Carteira': valor_carteira,
                    'Saldo Balancete': 0.0,
                    'Diferença': valor_carteira,
                    'Numero de Registros': 0,
                    'Status': 'NÃO MAPEADO'
                })
                continue
            
            # Obter todos os nomes do balancete que correspondem a este ativo da carteira
            contas_balancete = mapeamento_agrupado[ativo_carteira]
            
            # Buscar e somar TODOS os registros no balancete para TODOS os nomes mapeados
            saldo_total_balancete = 0.0
            contas_encontrados = []
            total_registros_encontrados = 0
            
            for conta_balancete in contas_balancete:
                # Normalizar a conta do mapeamento da mesma forma que o balancete
                conta_balancete_normalizado = normalizar_conta(conta_balancete)
                
                # Procurar TODOS os registros no balancete com esta conta (busca exata apenas)
                balancete_matches = df_balancete_normalizado[
                    df_balancete_normalizado['Conta_Normalizado'] == conta_balancete_normalizado
                ]
                
                # Se encontrou registros para esta conta, somar os valores
                if not balancete_matches.empty:
                    contas_encontrados.append(f"{conta_balancete}")
                    total_registros_encontrados += len(balancete_matches)
                    
                    for _, match_row in balancete_matches.iterrows():
                        saldo_atual = match_row[saldo_col_balancete]
                        
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
            if len(contas_encontrados) == 0:
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Conta Balancete': f"NÃO ENCONTRADO", #({len(contas_balancete)} nomes mapeados)",
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
                if len(contas_encontrados) == 1:
                    conta_exibicao = contas_encontrados[0]
                else:
                    conta_exibicao = f"MÚLTIPLOS: {', '.join(contas_encontrados[:2])}"
                    if len(contas_encontrados) > 2:
                        conta_exibicao += f" + {len(contas_encontrados) - 2} outros"
                
                resultados.append({
                    'Ativo Carteira': ativo_carteira,
                    'Conta Balancete': conta_exibicao,
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
        ["TODOS", "MAPEADOS", "CONCILIADOS", "DIVERGENTES", "NÃO MAPEADOS"],
    )
    
    if status_filter == "TODOS":
        df_filtrado = df_resultado
    elif status_filter == "MAPEADOS":
        df_filtrado = df_resultado[df_resultado['Status'].isin(['CONCILIADO', 'DIVERGENTE'])]
    elif status_filter == "CONCILIADOS":
        df_filtrado = df_resultado[df_resultado['Status'] == 'CONCILIADO']
    elif status_filter == "DIVERGENTES":
        df_filtrado = df_resultado[df_resultado['Status'] == 'DIVERGENTE']
    elif status_filter == "NÃO MAPEADOS":
        df_filtrado = df_resultado[df_resultado['Status'] == 'NÃO MAPEADO']
    
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
            return ['background-color: #FFB74D'] * len(row)
        else:
            return ['background-color: #FFB74D'] * len(row)
    
    st.dataframe(
        df_display.style.apply(colorir_status, axis=1),
        use_container_width=True,
        hide_index=True
    )

# Função para ser chamada pelo main.py
if __name__ == "__main__":
    conciliador()