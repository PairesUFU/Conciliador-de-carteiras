#Importando
import streamlit as st
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

