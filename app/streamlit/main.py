import streamlit as st
from pages.lancamento import lancamento

def page_lancamento():
    lancamento()

# Configuração da página
st.set_page_config(
    page_title="Lançamento de Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações do Streamlit para upload de arquivos
st.set_option("server.maxUploadSize", 500)  # 500MB
st.set_option("server.maxMessageSize", 500)  # 500MB

# Definir as páginas
pages = [ 
    st.Page(page_lancamento, title="Lançamento de Dados", icon="📊"),
]

# Navegação
pg = st.navigation(pages)

# Executar a página
pg.run()

