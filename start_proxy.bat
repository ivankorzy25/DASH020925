@echo off
echo Verificando el Cloud SQL Auth Proxy...

REM Define el nombre del ejecutable del proxy
set PROXY_EXE=cloud-sql-proxy.exe
set INSTANCE_CONNECTION_NAME=lista-precios-2025:southamerica-east1:lista-precios-sql

REM Verifica si el proxy ya existe
if not exist "%PROXY_EXE%" (
    echo El proxy no se encuentra. Descargando...
    curl -o %PROXY_EXE% https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.10.0/cloud-sql-proxy.x64.exe
    if %errorlevel% neq 0 (
        echo Error al descargar el proxy. Por favor, verifica tu conexion a internet.
        pause
        exit /b
    )
    echo Descarga completa.
) else (
    echo El proxy ya existe.
)

echo.
echo Iniciando el Cloud SQL Auth Proxy...
echo Conectando a: %INSTANCE_CONNECTION_NAME%
echo Puerto local: 3307
echo.
echo ** IMPORTANTE: No cierres esta ventana. Debe permanecer abierta mientras usas el dashboard. **
echo.

REM Inicia el proxy
start "Cloud SQL Auth Proxy" .\%PROXY_EXE% --port 3307 %INSTANCE_CONNECTION_NAME%

echo.
echo El proxy se esta ejecutando en una nueva ventana.
echo Ahora puedes iniciar el servidor de Flask en otra terminal con 'python dashboard.py'.

pause
