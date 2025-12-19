# 🌐 Cómo Hacer la Interfaz Accesible desde Otros Dispositivos

## 📱 Opción 1: Acceso desde Red Local (Misma WiFi)

### Paso 1: Encontrar tu IP Local

**Windows:**
```bash
ipconfig
```
Busca "IPv4 Address" (ejemplo: 192.168.1.100)

**Linux/Mac:**
```bash
ifconfig
# o
ip addr show
```

### Paso 2: Actualizar Configuración

1. **Edita `docker-compose.network.yml`**:
   - Reemplaza `TU_IP_AQUI` con tu IP local
   - Ejemplo: `REACT_APP_API_URL=http://192.168.1.100:8000`

2. **Ejecuta con la nueva configuración**:
```bash
docker-compose -f docker-compose.network.yml up --build
```

3. **Accede desde otros dispositivos**:
   - En tu teléfono/tablet/otra PC, abre el navegador
   - Ve a: `http://TU_IP:3000`
   - Ejemplo: `http://192.168.1.100:3000`

### ⚠️ Importante
- Todos los dispositivos deben estar en la misma red WiFi
- Asegúrate de que el firewall permita conexiones en los puertos 3000 y 8000

## 🌍 Opción 2: Hacerlo Público (Acceso desde Internet)

### Usando ngrok (Recomendado para pruebas)

1. **Instala ngrok**:
   - Descarga de: https://ngrok.com/download
   - O con chocolatey: `choco install ngrok`

2. **Inicia tu aplicación normalmente**:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

3. **En otra terminal, crea túnel para el frontend**:
```bash
ngrok http 3000
```

4. **Crea túnel para el backend** (otra terminal):
```bash
ngrok http 8000
```

5. **Actualiza el frontend para usar la URL de ngrok del backend**:
   - Copia la URL de ngrok del backend (ejemplo: `https://abc123.ngrok.io`)
   - Edita `docker-compose.dev.yml`:
     ```yaml
     environment:
       - REACT_APP_API_URL=https://abc123.ngrok.io
     ```
   - Reinicia: `docker-compose -f docker-compose.dev.yml up`

6. **Accede desde cualquier lugar**:
   - Usa la URL de ngrok del frontend (ejemplo: `https://xyz789.ngrok.io`)

### Usando Cloudflare Tunnel (Gratis y sin límites)

1. **Instala cloudflared**:
   ```bash
   # Windows: descarga de https://github.com/cloudflare/cloudflared/releases
   # O con chocolatey: choco install cloudflared
   ```

2. **Crea túnel para frontend**:
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```

3. **Crea túnel para backend**:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```

## 🚀 Opción 3: Desplegar en un Servidor (Producción)

### Usando servicios gratuitos:

1. **Render.com** (Backend + Frontend):
   - Conecta tu repositorio de GitHub
   - Render despliega automáticamente
   - URL pública automática

2. **Vercel** (Frontend) + **Railway** (Backend):
   - Vercel para React (gratis)
   - Railway para FastAPI (tier gratuito disponible)

3. **Heroku** (Ambos):
   - Despliegue directo desde GitHub
   - URL pública automática

### Configuración para Producción

1. **Actualiza `docker-compose.yml`** para producción:
```yaml
environment:
  - REACT_APP_API_URL=https://tu-backend-url.com
```

2. **Actualiza CORS en `backend/app/main.py`**:
```python
allow_origins = ["https://tu-frontend-url.com"]
```

## 🔧 Configuración Rápida para Red Local

### Script Automático (Windows PowerShell)

Crea un archivo `start-network.ps1`:

```powershell
# Obtener IP local
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress | Select-Object -First 1

Write-Host "Tu IP local es: $ip" -ForegroundColor Green
Write-Host "Accede desde otros dispositivos en: http://$ip:3000" -ForegroundColor Yellow

# Actualizar docker-compose
$content = Get-Content docker-compose.network.yml -Raw
$content = $content -replace 'TU_IP_AQUI', $ip
Set-Content docker-compose.network.yml -Value $content

# Iniciar servicios
docker-compose -f docker-compose.network.yml up --build
```

Ejecuta:
```powershell
.\start-network.ps1
```

## 📝 Resumen de URLs

| Escenario | Frontend URL | Backend URL |
|-----------|--------------|-------------|
| **Local** | http://localhost:3000 | http://localhost:8000 |
| **Red Local** | http://TU_IP:3000 | http://TU_IP:8000 |
| **Público (ngrok)** | https://xyz.ngrok.io | https://abc.ngrok.io |
| **Producción** | https://tu-dominio.com | https://api.tu-dominio.com |

## ⚠️ Consideraciones de Seguridad

1. **Solo para desarrollo**: No uses `CORS_ORIGINS=*` en producción
2. **Autenticación**: Agrega autenticación si lo haces público
3. **HTTPS**: Usa HTTPS en producción (ngrok lo proporciona automáticamente)
4. **Firewall**: Asegúrate de configurar el firewall correctamente

## 🎯 Recomendación

- **Desarrollo/Pruebas**: Usa ngrok (fácil y rápido)
- **Demostración temporal**: Usa ngrok o Cloudflare Tunnel
- **Producción real**: Despliega en Render, Vercel, o similar

