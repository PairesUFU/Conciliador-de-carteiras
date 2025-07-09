import streamlit as st
import pandas as pd
import openpyxl
import sys
import os

# Adicionar o diretório pai da pasta streamlit ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_funds_list, get_fund_info, get_fund_quotas

# Página de lançamento de dados

def lancamento():
    st.title("Lançamento de Dados")
    
    # Seção de seleção de fundo
    st.header("📋 Seleção de Fundo")
    
    # Buscar lista de fundos
    funds_list = get_funds_list()
    
    if not funds_list:
        st.warning("⚠️ Nenhum fundo encontrado no banco de dados. Verifique se os dados foram populados corretamente.")
        selected_fund = None
    else:
        # Selectbox para escolher o fundo
        selected_fund = st.selectbox(
            "Escolha o fundo de interesse:",
            options=["Selecione um fundo..."] + funds_list,
            index=0,
            help="Selecione o fundo com o qual deseja trabalhar"
        )
        
        # Se um fundo foi selecionado, mostrar informações
        if selected_fund and selected_fund != "Selecione um fundo...":
            fund_info = get_fund_info(selected_fund)
            
            if fund_info:
                with st.expander("ℹ️ Informações do Fundo Selecionado", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Nome:** {fund_info['name']}")
                        st.write(f"**ID:** {fund_info['id']}")
                    
                    with col2:
                        st.write(f"**Slug:** {fund_info['slug']}")
                        st.write(f"**CNPJ:** {fund_info['government_id']}")
                        
                    st.subheader("📋 Cotas do Fundo")
                    quotas = get_fund_quotas(fund_info["id"])

                    if quotas:
                        df_quotas = pd.DataFrame(quotas, columns=['ID', 'Tipo', 'Nome da Cota', 'ID Externo'])
                        st.dataframe(df_quotas, use_container_width=True)
                    else:
                        st.info("Nenhuma cota encontrada para este fundo.")
                
                # Salvar o fundo selecionado na session state para uso futuro se necessário
                st.session_state.selected_fund = fund_info
            else:
                st.error("Erro ao carregar informações do fundo selecionado.")
    
    st.divider()
    st.write("Esta página é para o lançamento de dados.")

    # Criar duas colunas para os uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Balancete")
        balancete_file = st.file_uploader(
            "Carregar arquivo CSV (.csv) do balancete",
            type=["csv"],
            help="Selecione um arquivo CSV (máximo 500MB)",
            key="balancete_uploader"
        )
    
    with col2:
        st.subheader("🗺️ Mapeamento")
        mapeamento_file = st.file_uploader(
            "Carregar arquivo Excel (.xlsx) do mapeamento",
            type=["xlsx"],
            help="Selecione um arquivo Excel no formato .xlsx (máximo 500MB)",
            key="mapeamento_uploader"
        )
    
    # Processar arquivo do balancete
    df_balancete = None

    # Recebeu o arquivo
    if balancete_file is not None:
        #Ler
        try:
            
            # Processar o arquivo
            df_balancete = _process_balancete_file(balancete_file)
            
            # Retorno do processamento
            if df_balancete is not None:
                # Salvar no session state
                st.session_state['df_balancete_completo'] = df_balancete
                st.success("✅ Balancete processado e salvo com sucesso!")
            else:
                st.error("Erro ao processar o arquivo do balancete.")

        # Não leu      
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo do balancete: {str(e)}")
            st.error("Tente recarregar a página e enviar o arquivo novamente.")
    
    # Processar arquivo do mapeamento
    df_mapeamento = None
    # Recebeu o arquivo
    if mapeamento_file is not None:
        try:
            
            # Processar o arquivo
            df_mapeamento = _process_mapeamento_file(mapeamento_file)
            
            # Retorno do processamento
            if df_mapeamento is not None:
                # Salvar no session state
                st.session_state['df_mapeamento'] = df_mapeamento
                st.success("✅ Mapeamento processado e salvo com sucesso!")
            else:
                st.error("Erro ao processar o arquivo do mapeamento.")
                
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo do mapeamento: {str(e)}")
            st.error("Tente recarregar a página e enviar o arquivo novamente.")
    
    # Mostrar status dos arquivos
    if balancete_file is None and mapeamento_file is None:
        st.info("👆 Selecione os arquivos Excel para continuar.")
    elif balancete_file is None:
        st.warning("⚠️ Arquivo do balancete ainda não foi carregado.")
    elif mapeamento_file is None:
        st.warning("⚠️ Arquivo do mapeamento ainda não foi carregado.")
    
def _process_balancete_file(balancete_file):
    try:
        # Usar sempre latin-1 e separador ';'
        encoding = 'latin-1'
        separator = ';'
        
        # Reset do ponteiro do arquivo para o início
        balancete_file.seek(0)
        
        # Ler todas as linhas do arquivo
        lines = []
        for line in balancete_file:
            try:
                decoded_line = line.decode(encoding).strip()
                if decoded_line:  # Se a linha não está vazia
                    lines.append(decoded_line)
            except:
                break
        
        if len(lines) == 0:
            st.error("Arquivo vazio ou não foi possível ler as linhas.")
            return None
        
        # O header está na última linha
        header_line = lines[-1]
        data_lines = lines[:-1]  # Todas as linhas exceto a última
        
        # Dividir o header usando o separador
        columns = [col.strip() for col in header_line.split(separator)]
        
        # Processar as linhas de dados
        data_rows = []
        for line in data_lines:
            if line.strip():  # Se a linha não está vazia
                row_data = [cell.strip() for cell in line.split(separator)]
                # Garantir que a linha tem o mesmo número de colunas que o header
                if len(row_data) == len(columns):
                    data_rows.append(row_data)
        
        # Criar DataFrame
        df = pd.DataFrame(data_rows, columns=columns)
        
        # Converter a coluna SldAtu para numérico
        if 'SldAtu' in df.columns:
            # Limpar e converter valores numéricos
            df['SldAtu'] = df['SldAtu'].str.replace('.', '', regex=False)  # Remover separador de milhares
            df['SldAtu'] = df['SldAtu'].str.replace(',', '.', regex=False)  # Converter separador decimal
            df['SldAtu'] = pd.to_numeric(df['SldAtu'], errors='coerce').fillna(0.0)
        
        # Verificar colunas obrigatórias
        required_columns = {"Nome", "SldAtu"}
        
        # Converter nomes das colunas para strings e remover espaços extras
        df.columns = df.columns.str.strip()
        df_columns = set(str(col) for col in df.columns)
        
        # Verificar se as colunas obrigatórias existem no DataFrame
        missing_columns = required_columns - df_columns
        if missing_columns:
            st.error(f"O arquivo não contém as seguintes colunas obrigatórias: {missing_columns}")
            
            # Sugerir colunas similares
            for missing_col in missing_columns:
                similar_cols = [col for col in df.columns if missing_col.lower() in col.lower()]
                if similar_cols:
                    st.info(f"Colunas similares a '{missing_col}' encontradas: {similar_cols}")
            
            return None
        
        return df
        
    except Exception as e:
        st.error(f"Erro inesperado ao processar o arquivo CSV: {str(e)}")
        st.info("Verifique se o arquivo está no formato CSV correto e tente novamente.")
        st.info("Dica: Certifique-se de que o arquivo não está aberto em outro programa.")
        
        # Mostrar preview do arquivo raw para debug
        try:
            balancete_file.seek(0)
            raw_content = balancete_file.read(1000).decode('latin-1', errors='ignore')
            st.text_area("Primeiras linhas do arquivo (para debug):", raw_content, height=200)
        except:
            pass
        
        return None
    
def _process_mapeamento_file(mapeamento_file):
    try:
        # Ler o arquivo Excel (sheet_name=None retorna um dicionário com todas as abas)
        all_sheets = pd.read_excel(mapeamento_file, sheet_name=None)
        
        # Se há múltiplas abas, permitir que o usuário escolha
        if len(all_sheets) > 1:
            sheet_names = list(all_sheets.keys())
            selected_sheet = st.selectbox(
                "Selecione a aba do Excel de mapeamento para processar:",
                sheet_names,
                index=0,
                key="mapeamento_sheet_selector"
            )
            df = all_sheets[selected_sheet]
            st.info(f"Processando aba do mapeamento: {selected_sheet}")
        else:
            # Se há apenas uma aba, usar ela diretamente
            sheet_name = list(all_sheets.keys())[0]
            df = all_sheets[sheet_name]
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo de mapeamento: {e}")
        return None

