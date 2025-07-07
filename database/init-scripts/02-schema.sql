-- ==============================================================================
-- SCRIPT SQL DE INICIALIZAÇÃO (OPCIONAL)
-- ==============================================================================
-- Este arquivo pode conter comandos SQL adicionais que serão executados
-- automaticamente durante a inicialização do banco de dados.
-- Exemplos: criação de tabelas, inserção de dados iniciais, etc.
-- ==============================================================================

-- Exemplo: Criar uma tabela de teste
-- CREATE TABLE IF NOT EXISTS test_table (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Exemplo: Inserir dados de teste
-- INSERT INTO test_table (name) VALUES 
--     ('Test Record 1'),
--     ('Test Record 2');

-- Confirmar que a inicialização foi bem-sucedida
SELECT 'Database initialization completed successfully!' AS status;
