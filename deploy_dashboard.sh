#!/bin/bash

echo "--- 🚀 Iniciando Pipeline de Despliegue NEXUS ---"

# 1. Ejecutar conversión Excel → JSON
python3 src/xlsx_to_json.py

# 2. Verificar si la conversión fue exitosa
if [ $? -eq 0 ]; then
    echo "--- ✅ Conversión exitosa. Preparando Git ---"
    
    # 3. Git Workflow
    git add web/data.json web/index.html
    
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
