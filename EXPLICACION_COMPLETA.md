# 🎓 Explicación Completa del Sistema

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ ConfigPanel  │  │ DataUpload   │  │ ForecastChart│ │
│  │ (Tunear      │  │ (Subir CSV)  │  │ (Gráficas)   │ │
│  │  Parámetros) │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP Requests
                        │ (fetch/axios)
┌───────────────────────▼─────────────────────────────────┐
│                 BACKEND (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ /api/config/ │  │ /api/forecast │  │ ForecastService││
│  │ (Parámetros) │  │ (Predicciones)│  │ (Lógica ML)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Operación Completo

### Paso 1: Usuario Sube Datos CSV
```
Usuario → Frontend (DataUpload.js)
    ↓
Sube archivo CSV
    ↓
Frontend → POST /api/forecast/upload
    ↓
Backend (forecast_service.py)
    ↓
Carga CSV con pandas
    ↓
Convierte a formato StatsForecast (unique_id, ds, y)
    ↓
Almacena en memoria (self.Y_df)
    ↓
Retorna: lista de series disponibles
```

### Paso 2: Usuario Tunea Parámetros
```
Usuario → Frontend (ConfigPanel.js)
    ↓
Ajusta sliders/inputs:
  - test_weeks: 12
  - horizon: 12
  - min_accuracy: 60.0
  - etc...
    ↓
Click "Guardar Configuración"
    ↓
Frontend → PUT /api/config/
    ↓
Backend actualiza self.conf en ForecastService
    ↓
Retorna: configuración actualizada
```

### Paso 3: Usuario Genera Predicciones
```
Usuario → Click "Generar Predicciones"
    ↓
Frontend → POST /api/forecast/predict
    ↓
Backend (forecast_service.py.generate_full_forecast())
    ↓
┌─────────────────────────────────────────┐
│ 1. PREPARAR DATOS                       │
│    - Divide en Train/Test               │
│    - Fecha de corte = max_date - test_weeks│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. LIMPIEZA (Winsorización)             │
│    - Aplica upper_quantile              │
│    - Elimina outliers                   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 3. ENTRENAR MODELOS                    │
│    - Naive                              │
│    - AutoETS                            │
│    - Moving Average (2,3,4,6,8)         │
│    - Random Walk with Drift             │
│    - AutoARIMA                          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 4. PREDECIR (Validación)                │
│    - Predice test_weeks hacia adelante   │
│    - Compara con datos reales de test   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 5. CALCULAR MÉTRICAS                    │
│    - MAE (Error Absoluto Medio)         │
│    - Accuracy = 1 - (MAE / Media)       │
│    - Decisión: PREDECIR si accuracy >= min_accuracy│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 6. RE-ENTRENAR CON TODO EL HISTORIAL   │
│    - Usa todos los datos (train + test) │
│    - Limpia con winsorización           │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 7. PREDECIR FUTURO                      │
│    - Predice horizon semanas adelante   │
│    - Estas son las predicciones reales  │
└─────────────────────────────────────────┘
    ↓
Retorna JSON con:
  - train: datos históricos
  - test_real: datos reales de validación
  - predictions: predicciones de validación (líneas punteadas)
  - future: predicciones futuras (líneas punteadas gruesas)
  - metrics: Accuracy, MAE por modelo
  - cutoff_date: fecha de corte
```

### Paso 4: Visualización
```
Backend retorna datos → Frontend
    ↓
ForecastChart.js procesa datos:
    ↓
┌─────────────────────────────────────────┐
│ 1. Combina train + test + predictions  │
│ 2. Agrupa por fecha                     │
│ 3. Prepara formato para Recharts        │
└─────────────────────────────────────────┘
    ↓
Recharts renderiza:
  - Línea azul: train
  - Línea negra: test_real
  - Líneas punteadas: predicciones de cada modelo
  - Línea verde vertical: cutoff_date
    ↓
Tabla de métricas muestra:
  - Accuracy por modelo
  - MAE por modelo
  - Decisión (PREDECIR/NO_PREDECIR)
```

## 🎯 Componentes Clave Explicados

### 1. ForecastService (Backend)
**Ubicación**: `backend/app/services/forecast_service.py`

**Responsabilidades**:
- Mantener el diccionario `CONF` (parámetros configurables)
- Cargar y procesar datos CSV
- Entrenar modelos de StatsForecast
- Generar predicciones
- Calcular métricas

**Métodos principales**:
- `load_data()`: Carga CSV y convierte a formato StatsForecast
- `update_config()`: Actualiza parámetros del diccionario CONF
- `generate_full_forecast()`: Proceso completo de predicción
- `calculate_metrics()`: Calcula Accuracy y MAE

### 2. ConfigPanel (Frontend)
**Ubicación**: `frontend/src/components/ConfigPanel.js`

**Qué hace**:
- Muestra inputs para cada parámetro del diccionario CONF
- Permite ajustar valores
- Guarda cambios en el backend
- Restaura valores por defecto

**Parámetros que puedes tunear**:
```javascript
{
  test_weeks: 12,        // Semanas para validación
  horizon: 12,            // Semanas a predecir
  zero_threshold: 0.50,   // Filtro de ceros
  cv_threshold: 10,       // Coeficiente de variación
  min_accuracy: 60.0,     // Precisión mínima (%)
  upper_quantile: 0.80    // Winsorización (0-1)
}
```

### 3. ForecastChart (Frontend)
**Ubicación**: `frontend/src/components/ForecastChart.js`

**Qué hace**:
- Recibe datos del backend (train, test, predictions, future)
- Combina todo en un formato para gráficas
- Renderiza con Recharts:
  - Líneas sólidas para datos reales
  - Líneas punteadas para predicciones
  - Diferentes colores por modelo
- Muestra tabla de métricas

### 4. API Endpoints

#### GET `/api/config/`
Obtiene la configuración actual del diccionario CONF

#### PUT `/api/config/`
Actualiza parámetros. Ejemplo:
```json
{
  "test_weeks": 14,
  "horizon": 16,
  "min_accuracy": 70.0
}
```

#### POST `/api/forecast/upload`
Sube archivo CSV y lo procesa

#### POST `/api/forecast/predict`
Genera predicciones completas. Puede recibir:
```json
{
  "series_id": "BEVERAGES"  // Opcional, si no se envía procesa todas
}
```

## 🚀 Cómo Correr Todo

### Opción 1: Con Docker (MÁS FÁCIL) ⭐

```bash
# 1. Asegúrate de estar en la carpeta del proyecto
cd Forecast_nixtla-main

# 2. Ejecuta con Docker Compose (modo desarrollo con hot-reload)
docker-compose -f docker-compose.dev.yml up --build

# Esto hará:
# - Construir imágenes de backend y frontend
# - Iniciar ambos servicios
# - Backend en http://localhost:8000
# - Frontend en http://localhost:3000
```

**Ventajas**:
- ✅ Todo automático
- ✅ Hot-reload (cambios se reflejan automáticamente)
- ✅ No necesitas instalar Python/Node manualmente

### Opción 2: Sin Docker (Desarrollo Local)

#### Terminal 1 - Backend
```bash
# 1. Ve a la carpeta backend
cd backend

# 2. Crea entorno virtual
python -m venv venv

# 3. Activa entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instala dependencias
pip install -r requirements.txt

# 5. Ejecuta servidor
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend
```bash
# 1. Ve a la carpeta frontend
cd frontend

# 2. Instala dependencias
npm install

# 3. Ejecuta aplicación
REACT_APP_API_URL=http://localhost:8000 npm start
```

## 📊 Flujo de Uso Completo

### 1. Iniciar Servicios
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 2. Abrir Navegador
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs (documentación interactiva)

### 3. Cargar Datos
1. En la interfaz, sección "📁 Cargar Datos"
2. Click "📁 Seleccionar archivo CSV"
3. Elige tu archivo (debe tener columnas: `date`, `sales` o `y`)
4. Click "⬆️ Subir y Procesar"
5. Selecciona una serie del dropdown

### 4. Ajustar Parámetros
1. En "⚙️ Configuración de Parámetros"
2. Ajusta los valores que quieras:
   - Test Weeks: cuántas semanas usar para validar
   - Horizon: cuántas semanas predecir
   - Min Accuracy: precisión mínima requerida
   - etc.
3. Click "💾 Guardar Configuración"

### 5. Generar Predicciones
1. Click "🚀 Generar Predicciones"
2. Espera 10-30 segundos (entrenando modelos)
3. La gráfica se actualiza automáticamente

### 6. Interpretar Resultados
- **Línea azul**: Datos históricos (entrenamiento)
- **Línea negra gruesa**: Datos reales de test
- **Líneas punteadas**: Predicciones de cada modelo
- **Línea verde vertical**: Fecha de corte train/test
- **Tabla abajo**: Métricas (Accuracy, MAE) por modelo

## 🔍 Estructura de Archivos

```
Forecast_nixtla-main/
│
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── main.py             # Aplicación principal
│   │   ├── routers/
│   │   │   ├── config.py        # Endpoints de configuración
│   │   │   └── forecast.py      # Endpoints de predicciones
│   │   └── services/
│   │       └── forecast_service.py  # Lógica de ML (del notebook)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # React App
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConfigPanel.js   # Panel de parámetros
│   │   │   ├── ForecastChart.js # Gráficas
│   │   │   └── DataUpload.js    # Carga de archivos
│   │   ├── services/
│   │   │   └── api.js           # Cliente HTTP
│   │   ├── App.js               # Componente principal
│   │   └── index.js
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml           # Producción
├── docker-compose.dev.yml       # Desarrollo
└── README.md
```

## 🎓 Conceptos Clave

### Diccionario CONF
Es el objeto de configuración que controla todo el proceso:
- `test_weeks`: Cuántas semanas usar para validar modelos
- `horizon`: Cuántas semanas predecir a futuro
- `min_accuracy`: Precisión mínima para considerar útil un modelo
- `upper_quantile`: Límite para eliminar outliers (winsorización)

### Winsorización
Proceso de limpieza de datos que elimina valores extremos (outliers) recortándolos al percentil especificado.

### Train/Test Split
- **Train**: Datos históricos para entrenar modelos
- **Test**: Datos reales para validar qué tan bien funcionan
- **Cutoff Date**: Fecha que separa train de test

### Predicciones
- **Validación**: Predicciones sobre el test set (para evaluar)
- **Futuro**: Predicciones reales hacia adelante (para usar)

## 🐛 Troubleshooting

### Error: "No hay datos cargados"
- Asegúrate de haber subido un CSV primero

### Error: "Module not found"
- Instala dependencias: `pip install -r requirements.txt` (backend)
- O: `npm install` (frontend)

### Frontend no conecta
- Verifica que backend esté corriendo en puerto 8000
- Revisa CORS en `backend/app/main.py`

### Gráficas no se muestran
- Genera predicciones primero
- Revisa consola del navegador (F12)

## ✨ Características Especiales

1. **Tiempo Real**: Las gráficas se actualizan automáticamente
2. **Múltiples Modelos**: Compara 5+ modelos simultáneamente
3. **Métricas Automáticas**: Calcula Accuracy y MAE por modelo
4. **Interfaz Intuitiva**: Todo desde el navegador, sin código

## 🎯 Resumen Ultra-Rápido

1. **Ejecuta**: `docker-compose -f docker-compose.dev.yml up --build`
2. **Abre**: http://localhost:3000
3. **Sube CSV**: Con columnas `date` y `sales`
4. **Ajusta parámetros**: En el panel de configuración
5. **Genera predicciones**: Click en el botón
6. **Ve resultados**: En la gráfica y tabla de métricas

¡Eso es todo! 🚀

