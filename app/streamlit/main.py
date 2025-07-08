#Importando
import streamlit as st
import sys
import os

# Adiciona o diretório pai ao path para poder importar database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_funds_list, get_fund_info, test_database_connection
from pages.lancamento import lancamento
from pages.carteira import carteira
from pages.conciliador import conciliador

# Definição das páginas importadas
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

