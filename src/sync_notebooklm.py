import pandas as pd
import re
import os
import shutil

def normalize_text(text):
    if not text: return ""
    text = re.sub(r'\(.*?\)', '', str(text)).strip()
    text = text.lower()
    text = re.sub(r'\b(de|la|el|del|y)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def sync_notebooklm():
    base_file = 'base/base_datos_cafeteras.xlsx'
    backup_file = 'base/base_datos_cafeteras_NB_FIX_BAK.xlsx'
    
    # ---------------------------------------------------------
    # AUTHORITATIVE DATA FROM TICKET BASE (2025-2026)
    # ---------------------------------------------------------
    nb_data_raw = {
        "Quilmes Peatonal": 58, "Once": 55, "Cabildo": 52, "Boedo": 43, "Palmas del Pilar": 39,
        "San Fernando": 35, "Liniers": 38, "Pompeya": 43, "Berazategui": 27, "Carrefour Quilmes": 25,
        "Primera Junta": 24, "Moreno": 23, "Jose C. Paz": 23, "Güemes": 23, "San Martín Auto": 22,
        "Avellaneda": 22, "Merlo": 21, "San Martín Peatonal": 18, "San Justo 3": 18, "Luján": 17,
        "Flores": 16, "Urquiza": 16, "Parque Chacabuco": 15, "Monte Grande": 15, "Grand Bourg": 15,
        "Callao": 15, "San Isidro": 13, "Francisco Alvarez": 13, "Portal Rosario": 13, "San Telmo": 12,
        "Constitución": 12, "La Plata 2": 11, "Mendoza Centro": 11, "Gonnet": 11, "Wilde": 11,
        "La Plata 6": 10, "República de los Niños": 10, "La Plata 4": 10, "La Plata 3": 9,
        "Cabildo 2": 9, "San Miguel Auto": 8, "Villa del Parque": 8, "Lanús Auto": 8, "Canning": 8,
        "Carlos Paz": 7, "Laferrere 2": 7, "San Miguel 3": 7, "Ramos Mejía": 7, "Rotonda Gutiérrez": 7,
        "Santa Fe Peatonal": 6, "9 de Julio": 5, "Bolívar": 5, "Ushuaia": 5, "Zárate": 5,
        "Rosario Sur": 4, "Rosario Puma": 4, "Junín Auto": 4, "Mar del Plata Peatonal": 4,
        "Castelar": 3, "Lomas Auto": 3, "Walmart Santa Fe": 3, "Tandil": 2, "Ribera Santa Fe": 2,
        "Tucumán 4": 2, "Gualeguaychú": 2, "Lomas": 2, "La Rioja": 2, "La Perla": 2, "Paseo Aldrey": 1,
        "Plaza España": 1, "Rio Grande": 1, "Salta Libertad": 1, "Salta Orán": 1,
        "Santiago del Estero": 1, "San Antonio Oeste": 1, "San Nicolas": 1,
        "Rafael Nuñez": 1, "Funes": 1, "Mendoza Colón": 1, "Los Gallegos": 1
    }
    nb_lookup = {normalize_text(k): v for k, v in nb_data_raw.items()}
    
    # Manual Mapping for Edge Cases (Sigla or variations)
    manual_maps = {
        'F9DJ': '9 de julio',
        'FQUP': 'quilmes peatonal',
        'FPPI': 'palmas pilar'
    }
    
    print("🚀 Iniciando CORRECCIÓN de sincronización (Fix Name Collision)...")
    
    # Backup
    shutil.copy2(base_file, backup_file)
    
    df_base = pd.read_excel(base_file)
    
    total_updates = 0
    results_to_show = []

    for i, row in df_base.iterrows():
        name_base = normalize_text(row['Local'])
        sigla_base = str(row['Sigla']).strip().upper()
        
        match_val = None
        
        # 1. Exact Name Match (Highest priority)
        if name_base in nb_lookup:
            match_val = nb_lookup[name_base]
        
        # 2. Manual Mapping
        elif sigla_base in manual_maps and normalize_text(manual_maps[sigla_base]) in nb_lookup:
             match_val = nb_lookup[normalize_text(manual_maps[sigla_base])]

        # 3. Fuzzy match (only if NO exact match)
        else:
            for nb_key in nb_lookup:
                # Substring match with minimum length to avoid random hits
                if len(name_base) > 4 and (name_base == nb_key or name_base in nb_key or nb_key in name_base):
                    # One more guard: if name_base ends in number and nb_key doesn't (or vice versa), reject
                    if (re.search(r'\d$', name_base) and not re.search(r'\d$', nb_key)) or \
                       (not re.search(r'\d$', name_base) and re.search(r'\d$', nb_key)):
                        continue
                    match_val = nb_lookup[nb_key]
                    break
        
        if match_val is not None:
            df_base.at[i, 'Servicios'] = match_val
            total_updates += 1
            if 'Cabildo' in row['Local'] or 'Mayo' in row['Local'] or 'San Martin' in row['Local']:
                results_to_show.append(f"{row['Local']}: {match_val}")

    df_base.to_excel(base_file, index=False)
    
    print("\n🏁 Corrección finalizada.")
    print(f"📊 Total actualizados: {total_updates}")
    print("\n🔍 Muestra de Verificación de Colisiones:")
    for res in results_to_show:
        print(f"   ✅ {res}")

if __name__ == "__main__":
    sync_notebooklm()
