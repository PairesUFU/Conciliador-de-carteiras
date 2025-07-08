# Instruções para Executar o Projeto

## Como executar com Docker

1. **Certifique-se de que o Docker e Docker Compose estão instalados**

2. **Clone o repositório e navegue até o diretório do projeto**

3. **Execute o projeto com Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Acesse a aplicação:**
   - Streamlit: http://localhost:8501
   - PgAdmin (opcional): http://localhost:8080

## O que acontece quando você executa

1. **PostgreSQL** é iniciado e configurado
2. **Dados do arquivo funds.csv são automaticamente carregados** na tabela `funds` do banco
3. **Streamlit** é iniciado com a interface web
4. **Na tela principal**, você verá:
   - Um selectbox com todos os fundos disponíveis do arquivo funds.csv
   - Informações detalhadas do fundo selecionado
   - Navegação para as páginas: Lançamento de Dados, Carteira e Conciliador

## Estrutura do Banco de Dados

- **Tabela funds**: Contém os dados do arquivo funds.csv
  - id, name, slug, government_id, is_active, created_at, updated_at
- **Tabela fund_quotas**: Preparada para dados de cotas (se necessário no futuro)

## Observações

- A seleção de fundos é apenas para visualização e escolha do usuário
- As páginas funcionam normalmente, independente do fundo selecionado
- Os dados são persistidos no volume Docker `postgres_data`
- Para resetar os dados, execute: `docker-compose down -v` e depois `docker-compose up --build`
