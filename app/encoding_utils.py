"""
Módulo para correção de problemas de encoding em dados CSV
"""
import pandas as pd
import re

def create_encoding_fixes():
    """Cria um dicionário com correções de encoding conhecidas"""
    # Mapeamento de caracteres problemáticos para corretos
    fixes = {
        # Caracteres individuais problemáticos
        '√É': 'Ã',
        '√â': 'É',  # Corrigido para É em vez de Ê
        '√≠': 'í',
        '¬†': ' ',  # espaço não-quebrado
        '√Å': 'Á',
        '√ì': 'Í',
        '√∫': 'ú',
        '√©': 'é',
        '√≤': 'ò',
        '√°': 'à',
        '√´': 'ô',
        '√±': 'ã',
        '√ß': 'ç',
        '√∞': 'ñ',
        '¬∞': 'º',
        '¬™': '™',
        
        # Padrões específicos mais longos (devem vir antes dos individuais)
        'CART√ÉO DE CR√âDITO': 'CARTÃO DE CRÉDITO',
        'CREDIT√ìRIOS': 'CREDITÓRIOS',
        'M√∫ltiplo': 'Múltiplo',
        'Multiestrat√©gia': 'Multiestratégia',
        'Maca√∫bas': 'Macaúbas',
        'SOLF√ÅCIL': 'SOLFÁCIL',
        'Emp√≠rica': 'Empírica',
        'CR√âDITO': 'CRÉDITO',
        'CART√ÉO': 'CARTÃO',
    }
    
    # Adiciona padrões com espaços não-quebrados
    space_fixes = {
        '¬†FIDC¬†': ' FIDC ',
        '¬†FIM¬†': ' FIM ',
        '¬†FII¬†': ' FII ',
        '¬†SUB¬†': ' SUB ',
        '¬†CRED¬†': ' CRED ',
        '¬†Lake¬†': ' Lake ',
        '¬†FIDC': ' FIDC',
        '¬†FIM': ' FIM',
        '¬†FII': ' FII',
        '¬†SUB': ' SUB',
        '¬†HIGH': ' HIGH',
        '¬†SB': ' SB',
        '¬†MEZ': ' MEZ',
    }
    
    # Combina todos os fixes
    fixes.update(space_fixes)
    
    return fixes

def fix_text_encoding(text):
    """
    Corrige problemas de encoding em um texto
    
    Args:
        text (str): Texto com possíveis problemas de encoding
        
    Returns:
        str: Texto corrigido
    """
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    fixes = create_encoding_fixes()
    
    # Aplica as correções em ordem (padrões mais longos primeiro)
    fixed_text = text
    for wrong_pattern, correct_pattern in fixes.items():
        fixed_text = fixed_text.replace(wrong_pattern, correct_pattern)
    
    # Limpeza adicional de espaços múltiplos
    fixed_text = re.sub(r'\s+', ' ', fixed_text.strip())
    
    return fixed_text

def load_csv_with_encoding_fix(csv_path, encoding='utf-8'):
    """
    Carrega um CSV e aplica correções de encoding automaticamente
    
    Args:
        csv_path (str): Caminho para o arquivo CSV
        encoding (str): Encoding a ser usado na leitura inicial
        
    Returns:
        pandas.DataFrame: DataFrame com dados corrigidos
    """
    try:
        # Tenta diferentes encodings se o padrão falhar
        encodings_to_try = [encoding, 'cp1252', 'latin-1', 'utf-8', 'iso-8859-1']
        
        df = None
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(csv_path, encoding=enc)
                print(f"✅ CSV carregado com sucesso usando encoding: {enc}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception("Não foi possível ler o arquivo CSV com nenhum encoding testado")
        
        # Aplica correções de encoding nas colunas de texto
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].apply(fix_text_encoding)
            
        corrected_count = 0
        for col in text_columns:
            original_values = pd.read_csv(csv_path, encoding=encodings_to_try[0] if encodings_to_try else 'utf-8')[col]
            corrected_count += (df[col] != original_values).sum()
        
        if corrected_count > 0:
            print(f"🔧 {corrected_count} valores corrigidos para problemas de encoding")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {e}")
        raise
