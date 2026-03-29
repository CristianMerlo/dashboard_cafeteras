import pandas as pd
import os
import shutil
import io
import re

def parse_ppm(ppm_str):
    if pd.isna(ppm_str): return 0
    match = re.search(r'\d+', str(ppm_str))
    return int(match.group()) if match else 0

def check_negative(text):
    if pd.isna(text): return False
    words = ['no funciona', 'roto', 'vencido', 'cambiar', 'mal ', 'reparar', 'fuera de servicio', 'falla', 'falta', 'incompleto']
    return any(w in str(text).lower() for w in words)

def sync_google_sheets_live():
    URL_XLSX = "https://docs.google.com/spreadsheets/d/18fMrQrBAR7S7UyHvEjPgNz2GzwYqrJRJ3Ej7yn31BPA/export?format=xlsx"
    base_file = 'base/base_datos_cafeteras.xlsx'
    backup_file = 'base/base_datos_cafeteras_SHEET_BAK.xlsx'
    
    print("🚀 Descargando libro de cálculo (múltiples hojas) en tiempo real desde Google Drive...")
    
    try:
        xls = pd.ExcelFile(URL_XLSX)
        has_caf = 'CAFETERAS' in xls.sheet_names
        has_agua = 'CALIDAD DE AGUA' in xls.sheet_names
        if not (has_caf and has_agua):
            print("❌ El documento online no contiene las hojas requeridas: 'CAFETERAS' y 'CALIDAD DE AGUA'.")
            return
            
        df_caf = pd.read_excel(xls, sheet_name='CAFETERAS')
        df_agua = pd.read_excel(xls, sheet_name='CALIDAD DE AGUA')
        print(f"📥 Descarga completada. Filas detectadas (Cafeteras): {len(df_caf)} | (Agua): {len(df_agua)}")
    except Exception as e:
        print(f"❌ Error al procesar el archivo XLSX desde Google Drive: {e}")
        return

    # Respaldo de seguridad
    shutil.copy2(base_file, backup_file)
    df_base = pd.read_excel(base_file)

    updates_caf = 0
    updates_water = 0

    # 1. ACTUALIZAR EQUIPOS
    caf_cols_to_sync = ['Marca 1', 'Serie 1', 'Shots', 'Estado', 'Marca 2', 'Serie 2', 'Shots.1', 'Estado.1']
    caf_lookup = {str(r['Sigla']).strip().upper(): r for _, r in df_caf.iterrows() if str(r['Sigla']).strip().upper() not in ['NAN', 'NONE']}

    for i, row in df_base.iterrows():
        sigla_base = str(row['Sigla']).strip().upper()
        if sigla_base in caf_lookup:
            s_row = caf_lookup[sigla_base]
            changed = False
            for col in caf_cols_to_sync:
                if col in s_row.keys() and pd.notna(s_row[col]) and str(s_row[col]).strip() != '':
                    if df_base.at[i, col] != s_row[col]:
                        df_base.at[i, col] = s_row[col]
                        changed = True
            if changed: updates_caf += 1

    # 2. ACTUALIZAR AGUA Y SEMÁFORO
    agua_mapping = {
        'PPM': 'PPM',
        'Cuenta con filtros': 'Filtros',
        'Tiene sistema ablandador de agua': 'Ablandador',
        'Tiene sistema de ósmosis inversa': 'Osmosis'
    }
    
    agua_lookup = {str(r['Sigla']).strip().upper(): r for _, r in df_agua.iterrows() if str(r['Sigla']).strip().upper() not in ['NAN', 'NONE']}

    # Para ser flexibles si el usuario renombra la columna de estado
    col_estado_sheet = 'Estado Agua' if 'Estado Agua' in df_agua.columns else 'Estado general del equipo'
    agua_mapping[col_estado_sheet] = 'Estado Agua'

    for i, row in df_base.iterrows():
        sigla_base = str(row['Sigla']).strip().upper()
        
        # --- Sincronizar Campos de Agua ---
        if sigla_base in agua_lookup:
            a_row = agua_lookup[sigla_base]
            changed = False
            for sheet_col, base_col in agua_mapping.items():
                if sheet_col in a_row.keys() and pd.notna(a_row[sheet_col]) and str(a_row[sheet_col]).strip() != '':
                    
                    val = a_row[sheet_col]
                    if isinstance(val, bool) or val in ['TRUE', 'FALSE', 'True', 'False', True, False]:
                        val = "Sí" if str(val).upper() == "TRUE" else "No"
                        
                    if df_base.at[i, base_col] != val:
                        df_base.at[i, base_col] = val
                        changed = True
            if changed: updates_water += 1

        # --- MOTOR SEMÁFORO (Se calcula siempre para todos los locales que tengan PPM) ---
        ppm_val = df_base.at[i, 'PPM']
        filtros = str(df_base.at[i, 'Filtros']) == 'Sí'
        abland = str(df_base.at[i, 'Ablandador']) == 'Sí'
        osmo = str(df_base.at[i, 'Osmosis']) == 'Sí'
        estado_txt = str(df_base.at[i, 'Estado Agua'])
        
        ppm = parse_ppm(ppm_val)
        is_bad = check_negative(estado_txt)
        semaforo = ""
        
        if ppm > 0:
            if ppm <= 100:
                semaforo = "Amarillo" if is_bad else "Verde" 
                # Si ppm es bajo pero hay fallo de otro tipo de agua, amarillo
                
            elif 100 < ppm <= 150:
                if filtros:
                    semaforo = "Amarillo" if is_bad else "Verde"
                else:
                    semaforo = "Amarillo"
                    
            elif 150 < ppm <= 200:
                if filtros and abland:
                    semaforo = "Amarillo" if is_bad else "Verde"
                elif filtros or abland:
                    semaforo = "Amarillo" # Falta uno o el otro
                else:
                    semaforo = "Rojo" # Faltan ambos
                    
            elif ppm > 200:
                if osmo:
                    semaforo = "Amarillo" if is_bad else "Verde"
                else:
                    semaforo = "Rojo" # Riesgo Crítico sin ósmosis
                    
        df_base.at[i, 'Semaforo'] = semaforo

    df_base.to_excel(base_file, index=False)
    
    print("\n🏁 Sincronización en vivo + SEMÁFORO finalizada exitosamente.")
    print(f"✅ Locales actualizados (Equipos/Shots): {updates_caf}")
    print(f"💧 Locales procesados (Tratamiento Agua): {updates_water}")

if __name__ == "__main__":
    sync_google_sheets_live()
