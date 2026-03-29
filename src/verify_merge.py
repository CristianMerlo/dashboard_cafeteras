import pandas as pd
import re

def normalize_text(text):
    if not text: return ""
    text = re.sub(r'\(.*?\)', '', str(text)).strip()
    text = text.lower()
    text = re.sub(r'\b(de|la|el|del|y)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_sigla(text):
    m = re.search(r'\((.*?)\)', str(text))
    return m.group(1).strip().lower() if m else None

def verify_data():
    base_file = 'base/base_datos_cafeteras.xlsx'
    serv_file = 'base/SERVICIOS.xlsx'
    
    df_base = pd.read_excel(base_file)
    df_serv = pd.read_excel(serv_file)
    
    print("\n🧐 Iniciando Revisión de Datos (Final)...")
    
    matches = 0
    errors = 0
    
    # Pre-process base data for lookup
    base_lookup = {}
    for _, row in df_base.iterrows():
        sigla = str(row['Sigla']).strip().lower()
        norm_name = normalize_text(row['Local'])
        val = row['Servicios']
        
        if sigla: base_lookup[sigla] = val
        if norm_name: base_lookup[norm_name] = val

    for _, row in df_serv.iterrows():
        raw_name = str(row['Local (Sigla)'])
        norm_name = normalize_text(raw_name)
        sigla = extract_sigla(raw_name)
        source_val = row['Total de Servicios']
        
        # Check matching in base
        base_val = base_lookup.get(sigla) or base_lookup.get(norm_name)
        
        # If no direct match, check substrings
        if base_val is None:
            for b_key in base_lookup:
                if len(norm_name) > 4 and (norm_name in b_key or b_key in norm_name):
                    base_val = base_lookup[b_key]
                    break

        if base_val == source_val:
            matches += 1
        elif source_val == 0 and (base_val is None or pd.isna(base_val)):
            matches += 1
        else:
            print(f"❌ {raw_name}: {source_val} -> Error (Base tiene: {base_val})")
            errors += 1
            
    print(f"\n📈 Resumen final de revisión:")
    print(f"✅ Coincidencias validadas: {matches}")
    print(f"❌ Discrepancias encontradas: {errors}")
    print(f"📊 Cobertura Total: {(matches/(matches+errors))*100:.1f}%")

if __name__ == "__main__":
    verify_data()
