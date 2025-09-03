#!/bin/bash
echo ""
echo "=================================================="
echo " 🚀 INICIANDO DASH020925 - SISTEMA DE GESTION 🚀"
echo "=================================================="
echo ""
echo "Asegurate de que Docker este en ejecucion."
echo ""
echo "Este script hara lo siguiente:"
echo "  1. Construira la imagen de la aplicacion (si es necesario)."
echo "  2. Iniciara el contenedor de la base de datos."
echo "  3. Iniciara el contenedor de la aplicacion."
echo "  4. Ejecutara las migraciones de la base de datos."
echo "  5. Creara los usuarios por defecto."
echo "  6. Iniciara la aplicacion Streamlit."
echo ""
read -p "Presiona Enter para continuar o Ctrl+C para cancelar..."

echo ""
echo "Iniciando Docker Compose en segundo plano..."
docker compose -f docker/docker-compose.yml up --build -d

echo ""
echo "Esperando a que la aplicacion se inicie (15 segundos)..."
sleep 15

echo "Abriendo la aplicacion en tu navegador..."
# Usar el comando adecuado para cada SO
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8501
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8501
else
    echo "No se pudo detectar el sistema operativo para abrir el navegador."
    echo "Por favor, abre manualmente: http://localhost:8501"
fi

echo ""
echo "La aplicacion se esta ejecutando en segundo plano."
echo "Para detenerla, ejecuta: docker compose -f docker/docker-compose.yml down"
echo ""
