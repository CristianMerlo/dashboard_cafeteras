import pandas as pd
import re
import os
import shutil

def normalize_text(text):
    if not text: return ""
    # Remove everything inside parentheses and trim
    text = re.sub(r'\(.*?\)', '', str(text)).strip()
    # Normalize spaces and remove "del", "de", "la", "el" for better matching
    text = text.lower()
    text = re.sub(r'\b(de|la|el|del|y)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_sigla(text):
    m = re.search(r'\((.*?)\)', str(text))
    return m.group(1).strip().lower() if m else None

def merge_data():
    base_file = 'base/base_datos_cafeteras.xlsx'
    serv_file = 'base/SERVICIOS.xlsx'
    backup_path = 'base/base_datos_cafeteras_BAK.xlsx'
    
    print(f"🔄 Iniciando combinación de datos (Lógica Mejorada)...")
    
    # Backup (using copy2 to preserve metadata)
    shutil.copy2(base_file, backup_path)
    
    df_base = pd.read_excel(base_file)
    df_serv = pd.read_excel(serv_file)
    
    # Manual Mapping for Edge Cases
    manual_maps = {
        'F9DJ': 'FM9JU',     # 9 de Julio
        'FCAB': 'FCABI',    # Cabildo
        'FMQCA': 'FMQCA',   # Quilmes Peatonal - Wait, let's map FQUP
        'FQUP': 'FMQCA',    # Quilmes Peatonal in base is FQUP
        'FBA1': 'FBAH'      # Bariloche? (Check sigla)
    }
    
    # Pre-process services into dictionaries for fast lookup
    serv_lookup = {}
    for _, row in df_serv.iterrows():
        raw = str(row['Local (Sigla)'])
        sigla = extract_sigla(raw)
        norm = normalize_text(raw)
        val = row['Total de Servicios']
        
        if sigla: serv_lookup[sigla] = val
        if norm: serv_lookup[norm] = val

    updates = 0
    misses = []
    
    for i, row in df_base.iterrows():
        name_base = normalize_text(row['Local'])
        sigla_base = str(row['Sigla']).strip().lower()
        
        match_val = None
        
        # 1. Direct Sigla Match
        if sigla_base in serv_lookup:
            match_val = serv_lookup[sigla_base]
        
        # 2. Manual Mapping
        elif sigla_base.upper() in manual_maps and manual_maps[sigla_base.upper()].lower() in serv_lookup:
            match_val = serv_lookup[manual_maps[sigla_base.upper()].lower()]

        # 3. Normalized Name Match
        elif name_base in serv_lookup:
            match_val = serv_lookup[name_base]
            
        # 4. Fuzzy Match: Substring
        else:
            for s_key in serv_lookup:
                if len(name_base) > 4 and (name_base in s_key or s_key in name_base):
                    match_val = serv_lookup[s_key]
                    break

        if match_val is not None:
            df_base.at[i, 'Servicios'] = match_val
            updates += 1
        else:
            misses.append(row['Local'])
            
    df_base.to_excel(base_file, index=False)
    print(f"✅ Proceso completo.")
    print(f"   📈 Actualizados: {updates}")
    print(f"   📉 Sin datos: {len(misses)}")
    
    if misses:
        with open('tmp/missed_locales.txt', 'w') as f:
            for m in misses: f.write(f"{m}\n")

if __name__ == "__main__":
    merge_data()
