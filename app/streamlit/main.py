import streamlit as st
import sys
import os

# Adiciona o diretório pai ao path para poder importar database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_funds_list, get_fund_info, test_database_connection
from pages.lancamento import lancamento
from pages.carteira import carteira
from pages.conciliador import conciliador

def page_lancamento():
    lancamento()

def page_carteira():
    carteira()

def page_conciliador():
    conciliador()

# Configuração da página
st.set_page_config(
    page_title="Conciliador",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏦 Sistema Conciliador")

# Testar conexão com banco de dados
if not test_database_connection():
    st.error("❌ Não foi possível conectar ao banco de dados. Verifique se o PostgreSQL está rodando.")
    st.stop()

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
            
            # Salvar o fundo selecionado na session state para uso futuro se necessário
            st.session_state.selected_fund = fund_info
        else:
            st.error("Erro ao carregar informações do fundo selecionado.")

st.divider()


# Definir as páginas
pages = [ 
    st.Page(page_lancamento, title="Lançamento de Dados", icon="📊"),
    st.Page(page_carteira, title="Carteira", icon="💼"),
    st.Page(page_conciliador, title="Conciliador", icon="🔄"),
]

# Navegação
pg = st.navigation(pages)

# Executar a página
pg.run()

