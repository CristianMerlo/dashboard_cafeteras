#!/bin/bash

echo "--- 🚀 Iniciando Pipeline de Despliegue NEXUS ---"

# 1. Sincronizar datos de Google Sheets hacia el Excel base
python3 src/sync_google_sheet.py
if [ $? -ne 0 ]; then
    echo "❌ Falló la sincronización con Google Sheets. Abortando despliegue."
    exit 1
fi

# 2. Ejecutar conversión Excel → JSON
python3 src/xlsx_to_json.py

# 2. Verificar si la conversión fue exitosa
if [ $? -eq 0 ]; then
    echo "--- ✅ Conversión exitosa. Sincronizando entorno de producción (/docs) ---"
    
    # 3. Preparar GitHub Pages
    cp web/data.json docs/data.json
    cp web/index.html docs/index.html
    
    # 4. Git Workflow
    git add web/data.json web/index.html docs/data.json docs/index.html
    
    # Verificar si hay cambios pendientes
    if ! git diff-index --quiet HEAD --; then
        FECHA=$(date +'%d/%m/%Y %H:%M')
        git commit -m "Actualización Dashboard NEXUS - ${FECHA}"
        
        echo ""
        echo "📋 Cambios preparados. ¿Autorizas el despliegue a GitHub Pages?"
        read -p "   Responde 'si' para confirmar: " respuesta
        
        if [ "$respuesta" == "si" ] || [ "$respuesta" == "sí" ] || [ "$respuesta" == "Sí" ]; then
            git push origin main
            echo "🚀 Dashboard publicado correctamente en GitHub Pages."
            echo "🌐 URL: https://cristianmerlo.github.io/dashboard_cafeteras/"
        else
            echo "🚫 Despliegue cancelado. El commit local está guardado."
        fi
    else
        echo "✅ No hay cambios nuevos en los datos. Dashboard al día."
    fi
else
    echo "❌ Error en el proceso de datos. Despliegue abortado."
fi
