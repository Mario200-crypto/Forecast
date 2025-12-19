# 📋 Instrucciones Paso a Paso

## 🚀 Inicio Rápido

### Opción 1: Con Docker (Recomendado)

1. **Asegúrate de tener Docker y Docker Compose instalados**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Ejecuta el proyecto en modo desarrollo** (con hot-reload):
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Abre tu navegador**:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

### Opción 2: Sin Docker (Desarrollo Local)

#### Backend

1. **Crea un entorno virtual**:
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activa el entorno virtual**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Instala dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta el servidor**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend

1. **Instala dependencias**:
   ```bash
   cd frontend
   npm install
   ```

2. **Ejecuta la aplicación**:
   ```bash
   REACT_APP_API_URL=http://localhost:8000 npm start
   ```

## 📊 Cómo Usar la Aplicación

### Paso 1: Preparar tus Datos

Tu archivo CSV debe tener al menos estas columnas:
- `date`: Fecha en formato YYYY-MM-DD
- `sales` o `y`: Valores numéricos de la serie temporal
- (Opcional) `id` o `family`: Identificador de la serie

**Ejemplo de CSV:**
```csv
date,sales,family
2024-01-01,100.5,BEVERAGES
2024-01-08,120.3,BEVERAGES
2024-01-15,95.2,BEVERAGES
2024-01-22,110.8,BEVERAGES
```

### Paso 2: Cargar Datos

1. Abre http://localhost:3000
2. En la sección "📁 Cargar Datos":
   - Haz clic en "📁 Seleccionar archivo CSV"
   - Elige tu archivo CSV
   - Haz clic en "⬆️ Subir y Procesar"
3. Espera a que se carguen los datos
4. Selecciona la serie que quieres analizar del dropdown

### Paso 3: Tunear Parámetros

En la sección "⚙️ Configuración de Parámetros", ajusta los valores:

- **Test Weeks**: Semanas para validación (recomendado: 10-16)
- **Horizon**: Semanas a predecir (recomendado: 12-16)
- **Zero Threshold**: Filtro de ceros (0-1, default: 0.50)
- **CV Threshold**: Coeficiente de variación (default: 10)
- **Min Accuracy**: Precisión mínima requerida % (default: 60.0)
- **Upper Quantile**: Límite para winsorización (0.5-1, default: 0.80)

**💡 Tip**: Empieza con los valores por defecto y ajusta según necesites.

Haz clic en "💾 Guardar Configuración" para aplicar los cambios.

### Paso 4: Generar Predicciones

1. Haz clic en "🚀 Generar Predicciones"
2. Espera a que se entrenen los modelos (puede tomar unos segundos)
3. La gráfica se actualizará automáticamente

### Paso 5: Interpretar Resultados

**En la gráfica verás:**
- **Línea azul**: Datos históricos (entrenamiento)
- **Línea negra gruesa**: Datos reales de test (para validación)
- **Líneas punteadas de colores**: Predicciones de cada modelo
  - Líneas más finas: Predicciones de validación
  - Líneas más gruesas: Predicciones futuras
- **Línea verde vertical**: Fecha de corte entre train/test

**En la tabla de métricas:**
- **Accuracy**: Porcentaje de precisión (mayor es mejor)
- **MAE**: Error absoluto medio (menor es mejor)
- **Decisión**: PREDECIR si el modelo es útil, NO_PREDECIR si no

## 🔧 Solución de Problemas

### Error: "No hay datos cargados"
- Asegúrate de haber subido un archivo CSV válido
- Verifica que el CSV tenga las columnas correctas

### Error: "Los modelos no han sido entrenados"
- Primero carga datos
- Luego genera predicciones

### Frontend no se conecta al backend
- Verifica que ambos servicios estén corriendo
- Revisa los logs: `docker-compose logs -f`
- Asegúrate de que la URL del API sea correcta

### Las predicciones tardan mucho
- Reduce el número de semanas en "Test Weeks" y "Horizon"
- Reduce el número de series si tienes muchas

### La gráfica no se muestra
- Verifica que hayas generado predicciones primero
- Revisa la consola del navegador para errores

## 📝 Notas Importantes

1. **Formato de fechas**: Las fechas deben estar en formato YYYY-MM-DD
2. **Frecuencia**: El sistema asume datos semanales (W-MON)
3. **Datos faltantes**: Los valores nulos se eliminan automáticamente
4. **Múltiples series**: Si tu CSV tiene múltiples series (por ejemplo, diferentes familias), cada una se procesará por separado

## 🎯 Próximos Pasos

1. Experimenta con diferentes parámetros para ver cómo afectan las predicciones
2. Compara diferentes modelos para encontrar el mejor para tu serie
3. Ajusta el "Min Accuracy" según tus necesidades de negocio
4. Usa las predicciones futuras para planificación

## 💻 Desarrollo

### Estructura del Código

- **Backend**: Lógica de forecasting adaptada del notebook original
- **Frontend**: Interfaz React con controles interactivos
- **API**: Endpoints RESTful para comunicación entre frontend y backend

### Agregar Nuevos Modelos

Para agregar nuevos modelos, edita `backend/app/services/forecast_service.py` en el método `train_models()`.

### Personalizar la UI

Los componentes React están en `frontend/src/components/`. Puedes modificar los estilos en los archivos `.css` correspondientes.

