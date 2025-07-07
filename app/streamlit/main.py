import streamlit as st
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
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)


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

