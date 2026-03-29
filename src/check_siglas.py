import pandas as pd
import re
import os

def check_siglas():
    base_file = 'base/base_datos_cafeteras.xlsx'
    servicios_file = 'base/SERVICIOS.xlsx'
    
    if not os.path.exists(base_file) or not os.path.exists(servicios_file):
        print("❌ Error: Files not found.")
        return

    df_base = pd.read_excel(base_file)
    df_serv = pd.read_excel(servicios_file)
    
    base_siglas = set(df_base['Sigla'].dropna().astype(str).unique())
    
    def extract_sigla(x):
        m = re.search(r'\((.*?)\)', str(x))
        return m.group(1).strip() if m else str(x).strip()

    serv_siglas_raw = df_serv['Local (Sigla)'].dropna().unique()
    serv_siglas = {extract_sigla(s): s for s in serv_siglas_raw}
    
    matched = []
    unmatched_base = []
    unmatched_serv = []
    
    for s in serv_siglas:
        if s in base_siglas:
            matched.append(s)
        else:
            unmatched_serv.append(s)
            
    for s in base_siglas:
        if s not in serv_siglas:
            unmatched_base.append(s)
            
    print(f"📊 Resumen de Match:")
    print(f"✅ Match encontrados: {len(matched)}")
    print(f"❌ Siglas en Servicios NO encontradas en Base: {len(unmatched_serv)}")
    print(f"⚠️  Siglas en Base NO encontradas en Servicios: {len(unmatched_base)}")
    
    if unmatched_serv:
        print("\n🔍 Detalles de Siglas en Servicios no encontradas:")
        for s in unmatched_serv:
            print(f"   - {s} (Original: {serv_siglas[s]})")
            
    if matched:
        print("\n✅ Muestra de Matches (Primeros 5):")
        for s in matched[:5]:
            print(f"   - {s}")

if __name__ == "__main__":
    check_siglas()
