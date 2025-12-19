#!/bin/bash
# Script para iniciar con acceso desde red local (Linux/Mac)

echo "=== Configuración para Acceso desde Red Local ==="

# Obtener IP local
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
else
    # Linux
    ip=$(hostname -I | awk '{print $1}')
fi

if [ -z "$ip" ]; then
    echo "No se pudo encontrar una IP local válida"
    exit 1
fi

echo ""
echo "Tu IP local es: $ip"
echo "Accede desde otros dispositivos en: http://$ip:3000"
echo ""
echo "Asegúrate de que los dispositivos estén en la misma red WiFi"
echo ""

# Configurar variable de entorno
export REACT_APP_API_URL="http://$ip:8000"

echo "Iniciando servicios con API URL: $REACT_APP_API_URL"
echo ""
echo "Presiona Ctrl+C para detener los servicios"
echo ""

# Iniciar docker-compose
docker-compose -f docker-compose.dev.yml up --build

