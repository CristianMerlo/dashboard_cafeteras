import pandas as pd
import json
import os
import sys

def procesar_datos():
    # Rutas relativas a este script (src/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'base', 'base_datos_cafeteras.xlsx')
    output_file = os.path.join(base_dir, 'web', 'data.json')

    print(f"📂 Leyendo: {input_file}")

    # 1. Verificar existencia del archivo
    if not os.path.exists(input_file):
        print(f"❌ Error: El archivo {input_file} no existe.")
        print("💡 Tip: Asegúrate de que el Excel tenga el nombre 'base_datos_cafeteras.xlsx' en la carpeta base/")
        sys.exit(1)

    try:
        # 2. Leer el Excel
        df = pd.read_excel(input_file)

        # 3. Validar que no esté vacío
        if df.empty:
            print("⚠️ Advertencia: El archivo Excel está vacío. Despliegue abortado.")
            sys.exit(1)

        # 4. Renombrar columnas duplicadas (Shots.1, Estado.1) a nombres legibles
        df.columns = [
            col.replace('Shots.1', 'Shots 2').replace('Estado.1', 'Estado 2')
            for col in df.columns
        ]

        # 5. Limpieza: reemplazar NaN por cadena vacía
        df = df.fillna('')

        # 6. Convertir a JSON
        data = df.to_dict(orient='records')

        # 7. Construcción de métricas para el dashboard
        total = len(data)
        con_serie = sum(1 for r in data if str(r.get('Serie 1', '')).strip() not in ('', 'No especificado', 'S/N'))
        sin_serie = total - con_serie
        marcas = {}
        for r in data:
            m1 = str(r.get('Marca 1', '')).strip()
            m2 = str(r.get('Marca 2', '')).strip()
            if m1: marcas[m1] = marcas.get(m1, 0) + 1
            if m2: marcas[m2] = marcas.get(m2, 0) + 1

        output = {
            "meta": {
                "total_locales": total,
                "con_serie_confirmada": con_serie,
                "sin_serie": sin_serie,
                "marcas": marcas
            },
            "locales": data
        }

        # 8. Guardar JSON
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

        print(f"✅ Éxito: {total} locales procesados.")
        print(f"   📊 Con serie confirmada: {con_serie} | Sin serie: {sin_serie}")
        print(f"   🏷️  Marcas: {marcas}")
        print(f"   💾 Guardado en: {output_file}")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    procesar_datos()
