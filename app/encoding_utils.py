"""
Módulo para correção de problemas de encoding em dados CSV
"""
import pandas as pd

def load_csv_with_encoding_fix(csv_path, encoding='iso-8859-15'):
    """
    Carrega um CSV usando Latin-9 (ISO-8859-15) que suporta caracteres acentuados portugueses
    
    Args:
        csv_path (str): Caminho para o arquivo CSV
        encoding (str): Encoding a ser usado (padrão: iso-8859-15 / latin-9)
        
    Returns:
        pandas.DataFrame: DataFrame com dados carregados
    """
    try:
        # Tenta latin-9 primeiro (melhor suporte para português)
        encodings_to_try = ['iso-8859-15', 'latin-1', 'cp1252', 'utf-8']
        
        df = None
        encoding_used = None
        
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(csv_path, encoding=enc)
                encoding_used = enc
                print(f"✅ CSV carregado com sucesso usando encoding: {enc}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("Não foi possível ler o arquivo CSV com nenhum encoding testado")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {e}")
        raise
