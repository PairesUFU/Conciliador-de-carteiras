"""
Módulo para correção de problemas de encoding em dados CSV
"""
import pandas as pd
import re

def create_encoding_fixes():
    """Cria um dicionário com correções de encoding conhecidas"""
    # Mapeamento de caracteres problemáticos REAIS encontrados no CSV
    fixes = {
        # Padrões específicos completos (devem vir primeiro - mais específicos)
        'PRIMEPAG FIDC DE CARTâˆšÃ‰O DE CRâˆšÃ¢DITO': 'PRIMEPAG FIDC DE CARTÃO DE CRÉDITO',
        'UNAVANÂ¬â€ FIDCÂ¬â€ SUB': 'UNAVAN FIDC SUB',
        'CREDITÂ¬â€ HIGH': 'CREDIT HIGH',
        'MetropolitanaÂ¬â€ SB': 'Metropolitana SB',
        'CLMÂ¬â€ FIDC': 'CLM FIDC',
        'FICFIDCÂ¬â€ CREDÂ¬â€ MEZ': 'FICFIDC CRED MEZ',
        'CedroÂ¬â€ FII': 'Cedro FII',
        'VydeiraÂ¬â€ FIM': 'Vydeira FIM',
        'UrbanoÂ¬â€ FIDC': 'Urbano FIDC',
        'SilverÂ¬â€ LakeÂ¬â€ FIM': 'Silver Lake FIM',
        'AlbatrozÂ¬â€ FIDC': 'Albatroz FIDC',
        'SilverÂ¬â€ StoneÂ¬â€ SB': 'Silver Stone SB',
        'Empâˆšâ‰ ricaÂ¬â€ ImoÂ¬â€ Sub': 'Empírica Imo Sub',
        'HBÂ¬â€ FIDCÂ¬â€ NP': 'HB FIDC NP',
        'AceleraÂ¬â€ FIDC': 'Acelera FIDC',
        'SeteÂ¬â€ RocasÂ¬â€ SUB': 'Sete Rocas SUB',
        'TARGETÂ¬â€ FICÂ¬â€ FIMÂ¬â€ C': 'TARGET FIC FIM C',
        'MULTIBANKÂ¬â€ FIDC': 'MULTIBANK FIDC',
        'AroeiraÂ¬â€ FIDC': 'Aroeira FIDC',
        'ARACARÂ¬â€ FIDC': 'ARACAR FIDC',
        'BKÂ¬â€ IÂ¬â€ FIDCÂ¬â€ NP': 'BK I FIDC NP',
        'PRECÂ¬â€ BRÂ¬â€ FIDC': 'PREC BR FIDC',
        'J17Â¬â€ OrionÂ¬â€ FIMÂ¬â€ CP': 'J17 Orion FIM CP',
        'CoinvestÂ¬â€ FICFIDC': 'Coinvest FICFIDC',
        'QIÂ¬â€ FIDC': 'QI FIDC',
        'GAMGÂ¬â€ FIMÂ¬â€ CP': 'GAMG FIM CP',
        'ReconlogÂ¬â€ FIDC': 'Reconlog FIDC',
        'FATUREÂ¬â€ FIDC': 'FATURE FIDC',
        'LIFTCREDÂ¬â€ JR': 'LIFTCRED JR',
        'SOMACREDÂ¬â€ FIDC': 'SOMACRED FIDC',
        'QFLASHÂ¬â€ KG': 'QFLASH KG',
        'MAKENAÂ¬â€ FIDC': 'MAKENA FIDC',
        'PUSHÂ¬â€ FIDCÂ¬â€ COMEX': 'PUSH FIDC COMEX',
        'EOSÂ¬â€ FIDC': 'EOS FIDC',
        'CONTBANKÂ¬â€ FIDC': 'CONTBANK FIDC',
        'WCAPITALÂ¬â€ FIDC': 'WCAPITAL FIDC',
        'AtivaÂ¬â€ FIDC': 'Ativa FIDC',
        'AracuaÂ¬â€ FICFIM': 'Aracua FICFIM',
        'ZermattÂ¬â€ FICFIM': 'Zermatt FICFIM',
        'FatureÂ¬â€ FICÂ¬â€ FIM': 'Fature FIC FIM',
        '911Â¬â€ Bank': '911 Bank',
        'NOBELÂ¬â€ 2Â¬â€ FIDC': 'NOBEL 2 FIDC',
        'NETMONEYÂ¬â€ FIDC': 'NETMONEY FIDC',
        'HealthÂ¬â€ FIDC': 'Health FIDC',
        'GoorooÂ¬â€ Fidc': 'Gooroo Fidc',
        'BotucatuÂ¬â€ FIDC': 'Botucatu FIDC',
        'FATUREÂ¬â€ IIÂ¬â€ FIDC': 'FATURE II FIDC',
        'DOROÂ¬â€ FIDC': 'DORO FIDC',
        'NordeÂ¬â€ FIDC': 'Norte FIDC',
        'GREEN SOLFâˆšÃ…CIL VI FIDC LTDA': 'GREEN SOLFÁCIL VI FIDC LTDA',
        'AGROCANA FUNDO DE INVESTIMENTO EM DIREITOS CREDITâˆšÃ¬RIOS RESPONSABILIDADE LIMITADA': 'AGROCANA FUNDO DE INVESTIMENTO EM DIREITOS CREDITÓRIOS RESPONSABILIDADE LIMITADA',
        'FIDC Mâˆšâˆ«ltiplo BNK': 'FIDC Múltiplo BNK',
        'FIP TIG MultiestratâˆšÂ©gia': 'FIP TIG Multiestratégia',
        'FIP Macaâˆšâˆ«bas': 'FIP Macaúbas',
        'GRANA TECH CRâˆšÃ¢DITO POPULAR': 'GRANA TECH CRÉDITO POPULAR',
        
        # Padrões médios (palavras específicas)
        'CARTâˆšÃ‰O DE CRâˆšÃ¢DITO': 'CARTÃO DE CRÉDITO',
        'CREDITâˆšÃ¬RIOS': 'CREDITÓRIOS',
        'Mâˆšâˆ«ltiplo': 'Múltiplo',
        'MultiestratâˆšÂ©gia': 'Multiestratégia',
        'Macaâˆšâˆ«bas': 'Macaúbas',
        'SOLFâˆšÃ…CIL': 'SOLFÁCIL',
        'EmpâˆšÂ¡rica': 'Empírica',
        'Empâˆšâ‰ rica': 'Empírica',
        'CRâˆšÃ¢DITO': 'CRÉDITO',
        'CARTâˆšÃ‰O': 'CARTÃO',
        
        # Padrões de espaço mais específicos
        'Â¬â€ FIDC': ' FIDC',
        'Â¬â€ FIM': ' FIM',
        'Â¬â€ FII': ' FII',
        'Â¬â€ SUB': ' SUB',
        'Â¬â€ HIGH': ' HIGH',
        'Â¬â€ SB': ' SB',
        'Â¬â€ MEZ': ' MEZ',
        'Â¬â€ Bank': ' Bank',
        'Â¬â€ Lake': ' Lake',
        'Â¬â€ Stone': ' Stone',
        'Â¬â€ Imo': ' Imo',
        'Â¬â€ NP': ' NP',
        'Â¬â€ BR': ' BR',
        'Â¬â€ I': ' I',
        'Â¬â€ Orion': ' Orion',
        'Â¬â€ CP': ' CP',
        'Â¬â€ FIC': ' FIC',
        'Â¬â€ JR': ' JR',
        'Â¬â€ KG': ' KG',
        'Â¬â€ COMEX': ' COMEX',
        'Â¬â€ FICFIM': ' FICFIM',
        'Â¬â€ 2': ' 2',
        'Â¬â€ II': ' II',
        'Â¬â€ C': ' C',
        
        # Padrões individuais de caracteres problemáticos (devem vir por último)
        'âˆšÃ‰': 'Ã',      # CARTÃO
        'âˆšÃ¢': 'É',      # CRÉDITO  
        'âˆšâ‰': 'í',      # Empírica
        'âˆšÃ…': 'Á',      # SOLFÁCIL
        'âˆšÃ¬': 'Í',      # CREDITÓRIOS
        'âˆšâˆ«': 'ú',      # Múltiplo, Macaúbas
        'âˆšÂ©': 'é',      # Multiestratégia
        'âˆšÂ¡': 'í',      # Empírica
        'Â¬â€ ': ' ',      # espaço não-quebrado (padrão real mais geral)
        'Â¬â€': ' ',       # espaço não-quebrado sem espaço final
        
        # Caracteres individuais problemáticos
        '\u00A0': ' ',     # espaço não-quebrado
        'â€™': "'",        # apóstrofe curvado
        'â€œ': '"',        # aspas abertas
        'â€': '"',         # aspas fechadas
        'â€"': '-',        # hífen em dash
        'Â': '',           # Â isolado
        '¬': '',           # caractere negação isolado
    }
    
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
