@echo off
echo.
echo ==================================================
echo  🚀 INICIANDO DASH020925 - SISTEMA DE GESTION 🚀
echo ==================================================
echo.
echo Asegurate de que Docker Desktop este en ejecucion.
echo.
echo Este script hara lo siguiente:
echo   1. Construira la imagen de la aplicacion (si es necesario).
echo   2. Iniciara el contenedor de la base de datos.
echo   3. Iniciara el contenedor de la aplicacion.
echo   4. Ejecutara las migraciones de la base de datos.
echo   5. Creara los usuarios por defecto.
echo   6. Iniciara la aplicacion Streamlit.
echo.
echo Presiona cualquier tecla para continuar o cierra esta ventana para cancelar...
pause > nul

echo.
echo Iniciando Docker Compose...
echo La aplicacion puede tardar un momento en estar disponible.
echo.

start "DASH020925" /B docker compose -f docker/docker-compose.yml up --build

echo.
echo Esperando a que la aplicacion se inicie (15 segundos)...
timeout /t 15 /nobreak > nul

echo Abriendo la aplicacion en tu navegador...
start http://localhost:8501

echo.
echo La aplicacion deberia estar disponible en http://localhost:8501
echo.
echo La ventana de Docker Compose se esta ejecutando en segundo plano.
echo Cierra esta ventana cuando termines.
pause
