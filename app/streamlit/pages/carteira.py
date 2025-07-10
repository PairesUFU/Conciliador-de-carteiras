import streamlit as st
import pandas as pd
import io

def carteira():
    st.title("Carteira de Ativos")
    st.write("Esta página permite carregar a carteira de ativos ou usar dados de exemplo.")
    
    # Opção para escolher entre upload ou dados de exemplo
    opcao = st.radio(
        "Escolha uma opção:",
        ["Upload de arquivo CSV", "Usar dados de exemplo"],
        index=0
    )
    
    if opcao == "Upload de arquivo CSV":
        # Upload do arquivo CSV
        uploaded_file = st.file_uploader(
            "Faça upload do arquivo CSV da carteira",
            type=['csv'],
            help="O arquivo deve conter as colunas 'Titulo' (nome do ativo) e 'VlMrc' (valor). Header na penúltima linha. Usar sempre latin-1 e separador ';'"
        )
        
        if uploaded_file is not None:
            try:
                # Processar arquivo com header na penúltima linha
                resultado = _process_carteira_file(uploaded_file)
                
                if resultado is not None:
                    df_carteira_dados, total_registros_antes = resultado
                    
                    # Armazenar no session state para usar na página conciliador
                    st.session_state['df_carteira'] = df_carteira_dados
                    
                    # Configurar formatação para exibição
                    df_carteira_display = df_carteira_dados.copy()
                    df_carteira_display['valor'] = df_carteira_display['valor'].apply(
                        lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    )
                    
                    # Exibir a tabela
                    st.subheader("📈 Carteira Carregada")
                    st.success(f"✅ Carteira carregada com sucesso! {len(df_carteira_dados)} ativos diferentes encontrados.")
                    
                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Registros", total_registros_antes)
                        
                    with col2:
                        st.metric("Total de Ativos", len(df_carteira_dados))
                        
                    with col3:
                        valor_total = df_carteira_dados['valor'].sum()
                        st.metric("Valor Total", f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                    
                    # Tabela interativa
                    st.dataframe(
                        df_carteira_display,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "ativo": st.column_config.TextColumn("Ativo", width="medium"),
                            "valor": st.column_config.TextColumn("Valor", width="medium")
                        }
                    )
                
            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
                st.info("Verifique se o arquivo está no formato correto (CSV com encoding latin-1 e separador ';') e contém as colunas 'Titulo' e 'VlMrc'")
    
    else:
        # Dados de exemplo (código existente)
        st.subheader("📈 Dados de Exemplo")
        
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
        df_carteira_display['valor'] = df_carteira_display['valor'].apply(
            lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
        
        # Estatísticas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Ativos", len(df_carteira))
        with col2:
            valor_total = df_carteira['valor'].sum()
            st.metric("Valor Total", f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
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

def _process_carteira_file(carteira_file):
    """
    Processa o arquivo CSV da carteira com header na penúltima linha
    Agrupa títulos repetidos somando seus valores
    Retorna: (df_carteira_dados, total_registros_antes)
    """
    try:
        # Usar sempre latin-1 e separador ';'
        encoding = 'latin-1'
        separator = ';'
        
        # Reset do ponteiro do arquivo para o início
        carteira_file.seek(0)
        
        # Ler todas as linhas do arquivo
        lines = []
        for line in carteira_file:
            try:
                decoded_line = line.decode(encoding).strip()
                if decoded_line:  # Se a linha não está vazia
                    lines.append(decoded_line)
            except:
                break
        
        if len(lines) < 2:
            st.error("Arquivo deve ter pelo menos 2 linhas (dados + header).")
            return None
        
        # O header está na última linha
        header_line = lines[-1]
        data_lines = lines[:-1]  # Todas as linhas exceto a última
        
        # Dividir o header usando o separador
        columns = [col.strip() for col in header_line.split(separator)]
        
        # Verificar se as colunas necessárias existem
        col_titulo = None
        col_valor = None
        
        for col in columns:
            col_lower = col.lower().strip()
            if 'titulo' in col_lower:
                col_titulo = col
            elif 'vlmrc' in col_lower:
                col_valor = col
        
        if col_titulo is None:
            st.error("❌ Coluna 'Titulo' não encontrada no header")
            st.info(f"Colunas disponíveis: {columns}")
            return None
            
        if col_valor is None:
            st.error("❌ Coluna 'VlMrc' não encontrada no header")
            st.info(f"Colunas disponíveis: {columns}")
            return None
        
        # Processar as linhas de dados
        data_rows = []
        for line in data_lines:
            if line.strip():  # Se a linha não está vazia
                row_data = [cell.strip() for cell in line.split(separator)]
                # Garantir que a linha tem o mesmo número de colunas que o header
                if len(row_data) == len(columns):
                    data_rows.append(row_data)
        
        # Criar DataFrame temporário
        df_temp = pd.DataFrame(data_rows, columns=columns)
        
        # Processar valores numéricos (considerando formato brasileiro)
        df_temp[col_valor] = df_temp[col_valor].astype(str)
        df_temp[col_valor] = df_temp[col_valor].str.replace('.', '', regex=False)  # Remover separador de milhares
        df_temp[col_valor] = df_temp[col_valor].str.replace(',', '.', regex=False)  # Converter separador decimal
        df_temp[col_valor] = pd.to_numeric(df_temp[col_valor], errors='coerce').fillna(0)
        
        # Limpar e padronizar os títulos
        df_temp[col_titulo] = df_temp[col_titulo].astype(str).str.strip()
        
        # Remover linhas com títulos vazios ou nulos
        df_temp = df_temp[
            (df_temp[col_titulo].notna()) & 
            (df_temp[col_titulo].str.strip() != '')
        ]
        
        # SALVAR O TOTAL DE REGISTROS ANTES DO AGRUPAMENTO
        total_registros_antes = len(df_temp)
        
        # AGRUPAR TÍTULOS REPETIDOS E SOMAR VALORES
        df_agrupado = df_temp.groupby(col_titulo)[col_valor].sum().reset_index()
        
        # Mostrar informações do agrupamento
        titulos_unicos_antes = df_temp[col_titulo].nunique()
        titulos_unicos_depois = len(df_agrupado)
        registros_duplicados = total_registros_antes - titulos_unicos_depois
        
        # Criar DataFrame final da carteira
        df_carteira_dados = pd.DataFrame({
            'ativo': df_agrupado[col_titulo],
            'valor': df_agrupado[col_valor]
        })
        
        # Retornar tanto o DataFrame quanto o total de registros antes do agrupamento
        return df_carteira_dados, total_registros_antes
        
    except Exception as e:
        st.error(f"Erro inesperado ao processar o arquivo CSV: {str(e)}")
        st.info("Verifique se o arquivo está no formato correto e tente novamente.")
        
        return None

# Função para ser chamada pelo main.py
if __name__ == "__main__":
    carteira()