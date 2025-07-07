import streamlit as st
import pandas as pd
import openpyxl

# Página de lançamento de dados

def lancamento():
    st.title("Lançamento de Dados")
    st.write("Esta página é para o lançamento de dados.")

    # Criar duas colunas para os uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Balancete")
        balancete_file = st.file_uploader(
            "Carregar arquivo Excel (.xlsx) do balancete",
            type=["xlsx"],
            help="Selecione um arquivo Excel no formato .xlsx (máximo 500MB)",
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
            # Mostrar informações do arquivo
            st.info(f"Balancete carregado: {balancete_file.name} ({balancete_file.size} bytes)")
            
            # Processar o arquivo
            df_balancete = _process_balancete_file(balancete_file)
            
            # Retorno do processamento
            if df_balancete is not None:
                # Salvar no session state
                st.session_state['df_balancete_completo'] = df_balancete
                st.success("✅ Balancete processado e salvo com sucesso!")
            else:
                st.error("Erro ao processar o arquivo do balancete.")

        #Não leu      
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo do balancete: {str(e)}")
            st.error("Tente recarregar a página e enviar o arquivo novamente.")
    
    # Processar arquivo do mapeamento
    df_mapeamento = None
    # Recebeu o arquivo
    if mapeamento_file is not None:
        try:
            # Mostrar informações do arquivo
            st.info(f"Mapeamento carregado: {mapeamento_file.name} ({mapeamento_file.size} bytes)")
            
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
        # Ler o arquivo Excel (sheet_name=None retorna um dicionário com todas as abas)
        all_sheets = pd.read_excel(balancete_file, sheet_name=None)
        
        # Se há múltiplas abas, permitir que o usuário escolha
        if len(all_sheets) > 1:
            sheet_names = list(all_sheets.keys())
            selected_sheet = st.selectbox(
                "Selecione a aba do Excel para processar:",
                sheet_names,
                index=0
            )
            df = all_sheets[selected_sheet]
            st.info(f"Processando aba: {selected_sheet}")
        else:
            # Se há apenas uma aba, usar ela diretamente
            sheet_name = list(all_sheets.keys())[0]
            df = all_sheets[sheet_name]
        
        # Verificar colunas obrigatórias
        required_columns = {
            "503", "P0077", "C", "Carteira", "NomeCrt", "Cnpj", "Moeda", "Nome", "SldAnt",
            "SldAtu", "DataAtu", "DataAnt", "Negrito", "Afinidade", "PgIni", "bNtrzInv",
            "Periodo", "nGrupo", "MskNivel", "Mov", "Conta", "Debito", "Credito",
            "bAnalitica", "CodPlano", "TipoPes", "bAumtaAltura", "MaxPag"
        }
        
        # Converter nomes das colunas para strings para comparação
        df_columns = set(str(col) for col in df.columns)
        
        # Verificar se as colunas obrigatórias existem no DataFrame
        missing_columns = required_columns - df_columns
        if missing_columns:
            st.error(f"O arquivo não contém as seguintes colunas obrigatórias: {missing_columns}")
            st.info(f"Colunas disponíveis no arquivo: {list(df.columns)}")
            return None
        
        # Visualizar os dados
        _vizualize_data(df)
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None


def _vizualize_data(df):
    
    # Permitir visualização completa dos dados
    if st.checkbox("Mostrar os dados do balancete"):
        st.subheader("Balancete")
        st.dataframe(df, use_container_width=True)


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
        
        # Visualizar os dados do mapeamento
        _vizualize_mapeamento_data(df)
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo de mapeamento: {e}")
        return None


def _vizualize_mapeamento_data(df):
    # Permitir visualização dos dados do mapeamento
    if st.checkbox("Mostrar os dados do mapeamento"):
        st.subheader("Mapeamento")
        st.dataframe(df, use_container_width=True)

