# Forecast Dashboard

Dashboard interactivo para prediccion de series de tiempo usando StatsForecast.

## Arquitectura

```
Forecast_nixtla-main/
├── backend/                      # API FastAPI
│   ├── app/
│   │   ├── main.py              # Aplicación principal
│   │   ├── routers/             # Endpoints de la API
│   │   │   ├── config.py        # Endpoints para tunning de parámetros
│   │   │   └── forecast.py      # Endpoints para predicciones
│   │   └── services/            # Lógica de negocio
│   │       └── forecast_service.py  # Servicio adaptado del notebook
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                     # React App
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   │   ├── ConfigPanel.js   # Panel de tunning de parámetros
│   │   │   ├── ForecastChart.js # Gráficas con Recharts
│   │   │   └── DataUpload.js    # Carga de archivos
│   │   ├── services/
│   │   │   └── api.js           # Cliente API
│   │   ├── App.js               # Componente principal
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── data/                         # Datos CSV (opcional)
├── docker-compose.yml            # Producción
├── docker-compose.dev.yml        # Desarrollo (hot-reload)
├── Nixtla_forecast_v2 (1).ipynb # Notebook original
└── README.md
```

## Tecnologias

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 18 + Recharts
- **Forecasting**: StatsForecast (Nixtla)
- **Contenedores**: Docker + Docker Compose

## Requisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- Dataset: [Kaggle Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data)

## Inicio Rapido

### 1. Clonar y preparar

```bash
cd forecast_app
```

### 2. Ejecutar en desarrollo (con hot-reload)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Ejecutar en produccion

```bash
docker-compose up --build -d
```

### 4. Acceder a la aplicacion

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Uso

### Flujo Principal

1. **Abre la aplicación**: http://localhost:3000
2. **Carga tus datos**: Sube un archivo CSV con datos de series de tiempo
   - El CSV debe tener columnas: `date` (fecha), `sales` o `y` (valores), y opcionalmente `id` o `family` (identificador de serie)
3. **Selecciona una serie**: Elige la serie que quieres analizar del dropdown
4. **Tunea los parámetros**: Ajusta los parámetros del diccionario `CONF`:
   - **Test Weeks**: Semanas usadas para validación (backtesting)
   - **Horizon**: Semanas a predecir a futuro
   - **Zero Threshold**: Filtro de ceros (0-1)
   - **CV Threshold**: Filtro de coeficiente de variación
   - **Min Accuracy**: Umbral mínimo de precisión para considerar útil el modelo (%)
   - **Upper Quantile**: Límite superior para winsorización (eliminar outliers, 0.5-1)
5. **Guarda la configuración**: Haz clic en "💾 Guardar Configuración"
6. **Genera predicciones**: Haz clic en "🚀 Generar Predicciones"
7. **Visualiza resultados**: 
   - **Línea azul**: Historia (datos de entrenamiento)
   - **Línea negra gruesa**: Test Real (datos reales para validación)
   - **Líneas punteadas**: Predicciones de cada modelo (validación y futuro)
   - **Línea verde vertical**: Fecha de corte entre train/test
8. **Compara métricas**: Revisa la tabla de métricas (Accuracy, MAE) para cada modelo

### Características Principales

- ✅ **Tunning gráfico de parámetros**: Ajusta todos los parámetros del diccionario `CONF` desde la interfaz
- ✅ **Visualización en tiempo real**: Las gráficas se actualizan automáticamente al generar nuevas predicciones
- ✅ **Múltiples modelos**: Compara Naive, AutoETS, Moving Average, RWD, AutoARIMA
- ✅ **Métricas detalladas**: Accuracy, MAE y decisión (PREDECIR/NO_PREDECIR) por modelo
- ✅ **Predicciones futuras**: Visualiza tanto validación como proyecciones futuras

## API Endpoints

### Configuración

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/config/` | Obtiene la configuración actual |
| PUT | `/api/config/` | Actualiza parámetros del diccionario CONF |
| POST | `/api/config/reset` | Restaura configuración a valores por defecto |

### Forecasting

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/forecast/upload` | Sube y carga archivo CSV |
| GET | `/api/forecast/series` | Lista series disponibles |
| GET | `/api/forecast/series/{series_id}` | Obtiene datos de una serie específica |
| POST | `/api/forecast/predict` | Genera predicciones completas (entrenamiento + validación + futuro) |

### Ejemplos de Uso

#### Actualizar configuración

```bash
curl -X PUT http://localhost:8000/api/config/ \
  -H "Content-Type: application/json" \
  -d '{
    "test_weeks": 14,
    "horizon": 16,
    "min_accuracy": 70.0,
    "upper_quantile": 0.85
  }'
```

#### Generar predicciones

```bash
curl -X POST http://localhost:8000/api/forecast/predict \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "SERIES_1"
  }'
```

#### Subir datos

```bash
curl -X POST http://localhost:8000/api/forecast/upload \
  -F "file=@data/train.csv"
```

## Modelos de Forecasting

- **Naive**: Ultimo valor observado
- **Auto_Smoothing**: AutoETS (suavizado exponencial automatico)
- **MovAvg_N**: Promedio movil de N periodos
- **RWD**: Random Walk con Drift
- **AutoARIMA**: ARIMA con seleccion automatica de parametros

## Desarrollo Local (sin Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

## Estructura de Datos

El archivo CSV debe tener al menos estas columnas:

| Columna | Tipo | Descripción | Requerido |
|---------|------|-------------|-----------|
| date | string | Fecha (YYYY-MM-DD) | ✅ Sí |
| sales o y | float | Valores de la serie temporal | ✅ Sí |
| id o family | string/int | Identificador único de la serie | ⚠️ Opcional* |

\* Si no hay columna de identificador, se creará una serie única llamada "SERIES_1"

**Ejemplo de formato:**
```csv
date,sales,family
2024-01-01,100.5,BEVERAGES
2024-01-08,120.3,BEVERAGES
2024-01-15,95.2,BEVERAGES
```

El sistema automáticamente:
- Convierte las fechas al formato correcto
- Agrupa por `unique_id` (derivado de `id`, `family` o generado automáticamente)
- Ordena cronológicamente
- Elimina valores nulos

## Variables de Entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| REACT_APP_API_URL | http://localhost:8000 | URL del backend |

## Troubleshooting

### Error: No hay datos cargados
- Sube el archivo `train.csv` usando el boton de carga

### Error: Datos insuficientes
- Selecciona una fecha de corte que deje al menos 10 semanas de entrenamiento

### Frontend no conecta con backend
- Verifica que ambos contenedores esten corriendo
- Revisa los logs: `docker-compose logs -f`

## Licencia

MIT
# Forecast
