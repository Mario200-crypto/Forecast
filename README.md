# Forecast Dashboard

Dashboard interactivo para prediccion de series de tiempo usando StatsForecast.

## Arquitectura

```
forecast_app/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Aplicacion principal
│   │   ├── routers/        # Endpoints de la API
│   │   └── services/       # Logica de negocio (forecasting)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React App
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── services/       # Cliente API
│   │   └── App.js          # Componente principal
│   ├── Dockerfile
│   └── package.json
├── data/                   # Datos CSV
├── docker-compose.yml      # Produccion
└── docker-compose.dev.yml  # Desarrollo
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

1. Abre http://localhost:3000
2. Sube el archivo `train.csv` de Kaggle
3. Selecciona una familia de producto
4. Ajusta la fecha de corte (linea roja en el grafico)
5. Selecciona el horizonte de prediccion
6. Haz clic en "Generar Prediccion"
7. Visualiza las predicciones de los diferentes modelos
8. Compara metricas (Accuracy, MAE) para cada modelo

## API Endpoints

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/data/upload` | Subir archivo CSV |
| POST | `/api/data/load` | Cargar datos existentes |
| GET | `/api/forecast/series` | Listar series disponibles |
| GET | `/api/forecast/date-range` | Obtener rango de fechas |
| POST | `/api/forecast/predict` | Generar predicciones |

### Ejemplo de prediccion

```bash
curl -X POST http://localhost:8000/api/forecast/predict \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "BEVERAGES",
    "cutoff_date": "2017-06-01",
    "horizon": 12
  }'
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

El archivo `train.csv` debe tener estas columnas:

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| id | int | Identificador unico |
| date | string | Fecha (YYYY-MM-DD) |
| store_nbr | int | Numero de tienda |
| family | string | Familia de producto |
| sales | float | Ventas |
| onpromotion | int | Items en promocion |

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
