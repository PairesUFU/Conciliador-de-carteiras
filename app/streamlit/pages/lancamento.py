import streamlit as st
import pandas as pd
import openpyxl
import sys
import os

# Adicionar o diretório pai da pasta streamlit ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_funds_list, get_fund_info, get_fund_quotas, save_mapping_to_db, get_mappings_by_fund, load_mapping_from_db, check_mapping_exists, delete_mapping_from_db, delete_all_mappings_from_fund

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
                        df_quotas = pd.DataFrame(quotas, columns=['ID', 'Tipo', 'Nome da Cota', 'wallet_external_id'])
                        df_quotas = df_quotas.drop('ID', axis=1)
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
        
        # Só mostrar opções de mapeamento se um fundo foi selecionado
        if selected_fund and selected_fund != "Selecione um fundo..." and st.session_state.get('selected_fund'):
            fund_id = st.session_state.selected_fund['id']
            
            # Radio button para escolher opção de mapeamento
            opcao_mapeamento = st.radio(
                "Escolha uma opção para o mapeamento:",
                ["Upload de arquivo Excel", "Usar mapeamento salvo no banco"],
                index=0,
                key="opcao_mapeamento"
            )
            
            if opcao_mapeamento == "Upload de arquivo Excel":
                # Upload do arquivo Excel
                mapeamento_file = st.file_uploader(
                    "Carregar arquivo Excel (.xlsx) do mapeamento",
                    type=["xlsx"],
                    help="Selecione um arquivo Excel no formato .xlsx (máximo 500MB)",
                    key="mapeamento_uploader"
                )
                
                # Processar arquivo do mapeamento
                if mapeamento_file is not None:
                    try:
                        # Processar o arquivo
                        df_mapeamento = _process_mapeamento_file(mapeamento_file)
                        
                        if df_mapeamento is not None:
                            # Salvar no session state
                            st.session_state['df_mapeamento'] = df_mapeamento
                            st.success("✅ Mapeamento processado com sucesso!")
                            
                            # Opção para salvar no banco
                            with st.expander("💾 Salvar Mapeamento no Banco de Dados", expanded=True):
                                # Gerar nome padrão apenas uma vez
                                if 'default_mapping_name' not in st.session_state:
                                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                                    # Limpar nome do arquivo (remover extensão e caracteres problemáticos)
                                    clean_filename = mapeamento_file.name.replace('.xlsx', '').replace('.xls', '')
                                    clean_filename = ''.join(c for c in clean_filename if c.isalnum() or c in '-_')
                                    st.session_state['default_mapping_name'] = f"Mapeamento_{clean_filename}_{timestamp}"
                                
                                # Nome para o mapeamento
                                nome_mapeamento = st.text_input(
                                    "Nome para salvar o mapeamento:",
                                    value=st.session_state.get('default_mapping_name', ''),
                                    help="Escolha um nome único para identificar este mapeamento",
                                    key="mapping_name_input"
                                )
                                
                                col_save1, col_save2 = st.columns([1, 2])
                                with col_save1:
                                    if st.button("💾 Salvar no Banco", type="primary", key="save_mapping_btn"):
                                        if nome_mapeamento.strip():
                                            # Verificar se já existe
                                            exists = check_mapping_exists(fund_id, nome_mapeamento.strip())
                                            if exists:
                                                st.warning("⚠️ Já existe um mapeamento com este nome. Será atualizado.")
                                            
                                            # Salvar no banco
                                            mapping_id = save_mapping_to_db(
                                                fund_id=fund_id,
                                                mapping_df=df_mapeamento,
                                                name=nome_mapeamento.strip(),
                                                filename=mapeamento_file.name,
                                                sheet_name=st.session_state.get('selected_sheet_name', '')
                                            )
                                            
                                            if mapping_id:
                                                st.success(f"✅ Mapeamento salvo no banco com ID: {mapping_id}")
                                                # Limpar o nome padrão para próximo upload
                                                if 'default_mapping_name' in st.session_state:
                                                    del st.session_state['default_mapping_name']
                                                # Force refresh da lista de mapeamentos
                                                if 'cached_mappings' in st.session_state:
                                                    del st.session_state['cached_mappings']
                                            else:
                                                st.error("❌ Erro ao salvar mapeamento no banco")
                                        else:
                                            st.error("❌ Nome do mapeamento não pode estar vazio")
                                
                                with col_save2:
                                    st.info("💡 O mapeamento ficará disponível para reutilização neste fundo")
                        else:
                            st.error("Erro ao processar o arquivo do mapeamento.")
                            
                    except Exception as e:
                        st.error(f"Erro ao carregar o arquivo do mapeamento: {str(e)}")
                        st.error("Tente recarregar a página e enviar o arquivo novamente.")
            
            else:  # Usar mapeamento salvo no banco
                st.info("📋 Mapeamentos salvos para este fundo:")
                
                # Buscar mapeamentos do fundo (usar cache para melhor performance)
                cache_key = f"mappings_{fund_id}"
                if cache_key not in st.session_state or st.button("🔄 Atualizar Lista", key="refresh_mappings"):
                    mappings = get_mappings_by_fund(fund_id)
                    st.session_state[cache_key] = mappings
                else:
                    mappings = st.session_state[cache_key]
                
                if mappings:
                    # Criar opções para o selectbox
                    mapping_options = ["Selecione um mapeamento..."] + [
                        f"{m['name']} (criado em {m['created_at'].strftime('%d/%m/%Y %H:%M')})" 
                        for m in mappings
                    ]
                    
                    selected_mapping_option = st.selectbox(
                        "Escolha o mapeamento:",
                        mapping_options,
                        key="mapping_selector"
                    )
                    
                    if selected_mapping_option != "Selecione um mapeamento...":
                        # Encontrar o mapeamento selecionado
                        selected_index = mapping_options.index(selected_mapping_option) - 1
                        selected_mapping = mappings[selected_index]
                        
                        # Botões para carregar e excluir
                        col_load, col_delete = st.columns([2, 1])
                        
                        with col_load:
                            if st.button(f"📥 Carregar '{selected_mapping['name']}'", key="load_mapping_btn"):
                                # Carregar mapeamento do banco
                                df_mapeamento, mapping_name = load_mapping_from_db(selected_mapping['id'])
                                
                                if df_mapeamento is not None:
                                    # Salvar no session state
                                    st.session_state['df_mapeamento'] = df_mapeamento
                                    st.success(f"✅ Mapeamento '{mapping_name}' carregado com sucesso!")
                                    # Rerun para atualizar a interface
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao carregar mapeamento do banco")
                        
                        with col_delete:
                            if st.button("🗑️ Excluir", key="delete_mapping_btn", type="secondary"):
                                # Mostrar confirmação antes de excluir
                                if 'confirm_delete' not in st.session_state:
                                    st.session_state['confirm_delete'] = selected_mapping['id']
                                    st.warning(f"⚠️ Tem certeza que deseja excluir o mapeamento '{selected_mapping['name']}'?")
                                    st.rerun()
                        
                        # Confirmar exclusão se necessário
                        if st.session_state.get('confirm_delete') == selected_mapping['id']:
                            col_confirm, col_cancel = st.columns([1, 1])
                            
                            with col_confirm:
                                if st.button("✅ Confirmar Exclusão", key="confirm_delete_btn", type="primary"):
                                    # Excluir mapeamento
                                    success = delete_mapping_from_db(selected_mapping['id'])
                                    
                                    if success:
                                        st.success(f"✅ Mapeamento '{selected_mapping['name']}' excluído com sucesso!")
                                        # Limpar cache e session state
                                        if cache_key in st.session_state:
                                            del st.session_state[cache_key]
                                        if 'confirm_delete' in st.session_state:
                                            del st.session_state['confirm_delete']
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao excluir mapeamento")
                            
                            with col_cancel:
                                if st.button("❌ Cancelar", key="cancel_delete_btn"):
                                    if 'confirm_delete' in st.session_state:
                                        del st.session_state['confirm_delete']
                                    st.rerun()
                        
                        # Mostrar informações do mapeamento selecionado
                        with st.expander("ℹ️ Informações do Mapeamento", expanded=False):
                            st.write(f"**Nome:** {selected_mapping['name']}")
                            st.write(f"**Arquivo:** {selected_mapping['filename'] or 'N/A'}")
                            st.write(f"**Aba:** {selected_mapping['sheet_name'] or 'N/A'}")
                            st.write(f"**Criado em:** {selected_mapping['created_at'].strftime('%d/%m/%Y %H:%M:%S')}")
                else:
                    st.info("🔍 Nenhum mapeamento salvo encontrado para este fundo.")
                    st.info("💡 Use a opção 'Upload de arquivo Excel' para criar o primeiro mapeamento.")
                
                # Seção de gerenciamento de mapeamentos (só aparecer se houver mapeamentos)
                if mappings:
                    with st.expander("🛠️ Gerenciar Mapeamentos", expanded=False):
                        st.subheader("Resumo dos Mapeamentos")
                        
                        # Criar DataFrame com informações dos mapeamentos
                        df_mappings = pd.DataFrame([
                            {
                                'Nome': m['name'],
                                'Arquivo': m['filename'] or 'N/A',
                                'Aba': m['sheet_name'] or 'N/A',
                                'Criado em': m['created_at'].strftime('%d/%m/%Y %H:%M')
                            }
                            for m in mappings
                        ])
                        
                        st.dataframe(df_mappings, use_container_width=True, hide_index=True)
                        
                        st.subheader("Ações em Lote")
                        st.warning("⚠️ **Atenção**: Estas ações são irreversíveis!")
                        
                        # Botão para excluir todos os mapeamentos do fundo
                        if st.button("🗑️ Excluir TODOS os mapeamentos deste fundo", key="delete_all_mappings_btn", type="secondary"):
                            if 'confirm_delete_all' not in st.session_state:
                                st.session_state['confirm_delete_all'] = True
                                st.error(f"⚠️ **ATENÇÃO**: Esta ação excluirá permanentemente TODOS os {len(mappings)} mapeamentos deste fundo!")
                                st.rerun()
                        
                        # Confirmar exclusão em lote
                        if st.session_state.get('confirm_delete_all'):
                            st.error("🚨 **CONFIRMAÇÃO NECESSÁRIA**: Você tem certeza absoluta?")
                            col_confirm_all, col_cancel_all = st.columns([1, 1])
                            
                            with col_confirm_all:
                                if st.button("🔥 SIM, EXCLUIR TODOS!", key="confirm_delete_all_btn", type="primary"):
                                    # Excluir todos os mapeamentos do fundo de uma vez
                                    deleted_count = delete_all_mappings_from_fund(fund_id)
                                    
                                    if deleted_count > 0:
                                        st.success(f"✅ {deleted_count} mapeamento(s) excluído(s) com sucesso!")
                                        # Limpar cache e session state
                                        if cache_key in st.session_state:
                                            del st.session_state[cache_key]
                                        if 'confirm_delete_all' in st.session_state:
                                            del st.session_state['confirm_delete_all']
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao excluir mapeamentos ou nenhum mapeamento encontrado")
                            
                            with col_cancel_all:
                                if st.button("❌ Cancelar", key="cancel_delete_all_btn"):
                                    if 'confirm_delete_all' in st.session_state:
                                        del st.session_state['confirm_delete_all']
                                    st.rerun()
                
                # Mostrar preview se já carregado
                if 'df_mapeamento' in st.session_state:
                    with st.expander("👁️ Preview do Mapeamento Atual", expanded=False):
                        st.dataframe(st.session_state['df_mapeamento'], use_container_width=True)
        
        else:
            st.info("👆 Selecione um fundo primeiro para acessar as opções de mapeamento.")

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
    
    # Mostrar status dos arquivos
    if balancete_file is None:
        st.warning("⚠️ Arquivo do balancete ainda não foi carregado.")
    
def _process_balancete_file(balancete_file):
    try:
        # Usar Latin-9 (ISO-8859-15) para melhor suporte a caracteres acentuados
        encoding = 'iso-8859-15'
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
        
        # Converter a coluna SldAnt para numérico (se existir)
        if 'SldAnt' in df.columns:
            # Limpar e converter valores numéricos
            df['SldAnt'] = df['SldAnt'].str.replace('.', '', regex=False)  # Remover separador de milhares
            df['SldAnt'] = df['SldAnt'].str.replace(',', '.', regex=False)  # Converter separador decimal
            df['SldAnt'] = pd.to_numeric(df['SldAnt'], errors='coerce').fillna(0.0)
        
        # Converter a coluna SldAtu para numérico (se existir)
        if 'SldAtu' in df.columns:
            # Limpar e converter valores numéricos
            df['SldAtu'] = df['SldAtu'].str.replace('.', '', regex=False)  # Remover separador de milhares
            df['SldAtu'] = df['SldAtu'].str.replace(',', '.', regex=False)  # Converter separador decimal
            df['SldAtu'] = pd.to_numeric(df['SldAtu'], errors='coerce').fillna(0.0)
        
        # Verificar colunas obrigatórias (pelo menos uma das opções deve existir)
        required_columns_conta = {"Conta", "Nome"}  # Pelo menos uma dessas
        required_columns_saldo = {"SldAnt", "SldAtu"}  # Pelo menos uma dessas
        
        # Converter nomes das colunas para strings e remover espaços extras
        df.columns = df.columns.str.strip()
        df_columns = set(str(col) for col in df.columns)
        
        # Verificar se pelo menos uma coluna de conta existe
        conta_cols_found = required_columns_conta.intersection(df_columns)
        if not conta_cols_found:
            st.error(f"O arquivo deve conter pelo menos uma das seguintes colunas de conta: {required_columns_conta}")
            st.info(f"Colunas encontradas: {list(df.columns)}")
            return None
        
        # Verificar se pelo menos uma coluna de saldo existe
        saldo_cols_found = required_columns_saldo.intersection(df_columns)
        if not saldo_cols_found:
            st.error(f"O arquivo deve conter pelo menos uma das seguintes colunas de saldo: {required_columns_saldo}")
            st.info(f"Colunas encontradas: {list(df.columns)}")
            return None
        
        # Mostrar quais colunas foram encontradas
        st.success(f"✅ Colunas de conta encontradas: {conta_cols_found}")
        st.success(f"✅ Colunas de saldo encontradas: {saldo_cols_found}")
        
        return df
        
    except Exception as e:
        st.error(f"Erro inesperado ao processar o arquivo CSV: {str(e)}")
        st.info("Verifique se o arquivo está no formato CSV correto e tente novamente.")
        st.info("Dica: Certifique-se de que o arquivo não está aberto em outro programa.")
        
        # Mostrar preview do arquivo raw para debug
        try:
            balancete_file.seek(0)
            raw_content = balancete_file.read(1000).decode('iso-8859-15', errors='ignore')
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
            # Salvar nome da aba no session state
            st.session_state['selected_sheet_name'] = selected_sheet
        else:
            # Se há apenas uma aba, usar ela diretamente
            sheet_name = list(all_sheets.keys())[0]
            df = all_sheets[sheet_name]
            # Salvar nome da aba no session state
            st.session_state['selected_sheet_name'] = sheet_name
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo de mapeamento: {e}")
        return None

