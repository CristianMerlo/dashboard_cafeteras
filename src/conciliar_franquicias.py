import pandas as pd
import os
import shutil

def clean_boolean(val):
    if pd.isna(val) or str(val).strip() == '': return ""
    v = str(val).strip().upper()
    if v in ['SI', 'SÍ', 'S', '1', 'TRUE']: return "Sí"
    if v in ['NO', 'N', '0', 'FALSE']: return "No"
    return str(val).strip()

def conciliar():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_file = os.path.join(base_dir, 'base', 'base_datos_cafeteras.xlsx')
    source_file = os.path.join(base_dir, 'source', 'Datos de Franquicias.xlsx')
    backup_file = os.path.join(base_dir, 'base', 'base_datos_cafeteras_CONCILIACION_BAK.xlsx')

    print(f"📂 Cargando base actual...")
    df_base = pd.read_excel(base_file)
    
    print(f"📂 Cargando datos nuevos desde source...")
    df_new = pd.read_excel(source_file)

    # Crear backup
    shutil.copy2(base_file, backup_file)
    print(f"🛡️  Backup creado en: {backup_file}")

    # Diccionario de búsqueda por SIGLA
    new_data = {}
    for _, row in df_new.iterrows():
        sigla = str(row.get('SIGLA', '')).strip().upper()
        if sigla and sigla != 'NAN':
            new_data[sigla] = row

    stats = {'shots': 0, 'agua': 0}
    
    # Columnas de mapeo [Columna en Nuevo Excel] -> [Columna en Base]
    mapping = {
        'Cimballi 1- Shots': 'Shots',
        'Cimballi 2 - Shots': 'Shots 2',
        'Filtros Caferas': 'Filtros',
        'Ablandador de agua': 'Ablandador',
        'Osmosis': 'Osmosis'
    }

    print("🔄 Procesando conciliación...")
    
    for i, row in df_base.iterrows():
        sigla_base = str(row.get('Sigla', '')).strip().upper()
        
        if sigla_base in new_data:
            n_row = new_data[sigla_base]
            
            # 1. Conciliar SHOTS (Solo si el nuevo dato es numérico y la base está vacía o el nuevo es mayor)
            for n_col in ['Cimballi 1- Shots', 'Cimballi 2 - Shots']:
                b_col = mapping[n_col]
                new_val = n_row.get(n_col)
                
                if pd.notna(new_val) and str(new_val).strip() != '':
                    try:
                        new_num = int(float(new_val))
                        base_val = df_base.at[i, b_col]
                        base_num = 0
                        
                        if pd.notna(base_val) and str(base_val).strip() != '':
                            try: base_num = int(float(base_val))
                            except: base_num = 0
                            
                        if new_num > base_num:
                            df_base.at[i, b_col] = new_num
                            stats['shots'] += 1
                    except:
                        pass # No es un número válido

            # 2. Conciliar AGUA (Normalizar y actualizar si la base está vacía)
            for n_col in ['Filtros Caferas', 'Ablandador de agua', 'Osmosis']:
                b_col = mapping[n_col]
                new_val = clean_boolean(n_row.get(n_col))
                
                if new_val != "":
                    # Si el nuevo dato es "Sí", lo ponemos siempre para asegurar cobertura técnica
                    # Si el nuevo dato es "No" y la base estaba vacía, también lo ponemos
                    base_val = str(df_base.at[i, b_col]).strip()
                    
                    if base_val in ['', 'nan', 'None', '—']:
                        df_base.at[i, b_col] = new_val
                        stats['agua'] += 1
                    elif new_val == "Sí" and base_val == "No":
                        df_base.at[i, b_col] = "Sí"
                        stats['agua'] += 1

    # Guardar resultados
    df_base.to_excel(base_file, index=False)
    
    print(f"\n✨ Conciliación finalizada.")
    print(f"📊 Contadores de Shots actualizados: {stats['shots']}")
    print(f"💧 Sistemas de agua actualizados: {stats['agua']}")

if __name__ == "__main__":
    conciliar()
