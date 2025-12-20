#  Resumen - Dashboard de Predicciones

## ¿Qué Hicimos?

Generamos un código de forecasting  y posteriormente lo convertimos en un **sistema web completo** con interfaz gráfica para tunear parámetros y visualizar predicciones.
---

## Arquitectura 
```
Frontend (React) ←→ Backend (FastAPI) ←→ StatsForecast (ML)
     UI              API REST             5 Modelos
```

**3 componentes principales**:
- **Frontend**: Interfaz gráfica (React + Recharts)
- **Backend**: API que procesa datos y genera predicciones (FastAPI)
- **Motor ML**: Entrena modelos y genera predicciones (StatsForecast)

---

## Funcionalidades 

1. ✅ **Tunear parámetros visualmente** - Panel con controles para cada parámetro
2. ✅ **Cargar datos CSV** - Drag & drop, validación automática
3. ✅ **Generar predicciones** - Entrena 5 modelos simultáneamente
4. ✅ **Visualizar resultados** - Gráficas interactivas con todos los modelos
5. ✅ **Comparar métricas** - Tabla con Accuracy y MAE por modelo

---

## Flujo Completo 

1. Usuario sube CSV → Backend valida y procesa
2. Usuario ajusta parámetros → Backend actualiza configuración
3. Usuario genera predicciones → Backend:
   - Divide datos (train/test)
   - Limpia outliers (winsorización)
   - Entrena 5 modelos
   - Calcula métricas
   - Genera predicciones futuras
4. Frontend muestra gráficas y métricas

---

## Modelos Implementados

1. Naive
2. AutoETS (Suavizado exponencial)
3. Moving Average (5 variantes)
4. Random Walk with Drift
5. AutoARIMA

**Todos se comparan automáticamente** para encontrar el mejor.

---

## Tecnologías

- **Backend**: FastAPI (Python)
- **Frontend**: React + Recharts
- **ML**: StatsForecast (Nixtla)
- **Deployment**: Docker + Docker Compose

---

## Valor Agregado

| Antes (Notebook) | Ahora (Sistema) |
|------------------|-----------------|
| Editar código | Interfaz gráfica |
| Gráficas estáticas | Gráficas interactivas |
| Comparación manual | Métricas automáticas |
| Requiere Python | Cualquiera puede usar |

---

## Cómo Correr

### Ejecutar en desarrollo (con hot-reload)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Ejecutar en produccion

```bash
docker-compose up --build -d
```

### Acceder a la aplicacion

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health


##  Estructura del Código

```
backend/
  ├── app/
  │   ├── main.py              # Aplicación FastAPI
  │   ├── routers/             # Endpoints API
  │   │   ├── config.py        # Gestión parámetros
  │   │   └── forecast.py      # Predicciones
  │   └── services/
  │       └── forecast_service.py  # Lógica ML

frontend/
  ├── src/
  │   ├── components/          # Componentes React
  │   │   ├── ConfigPanel.js   # Tunning parámetros
  │   │   ├── ForecastChart.js # Gráficas
  │   │   └── DataUpload.js    # Carga CSV
  │   └── services/
  │       └── api.js           # Cliente HTTP
```

---

## Conceptos Clave

- **Forecasting**: Predicción de valores futuros basada en patrones históricos
- **Cross-Validation**: Dividir datos en train/test para evaluar modelos
- **Winsorización**: Eliminar outliers que afectan el entrenamiento
- **API RESTful**: Comunicación entre frontend y backend usando HTTP
- **Docker**: Empaquetado de la aplicación para deployment fácil

---

