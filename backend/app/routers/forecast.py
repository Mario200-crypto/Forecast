"""
Router para generar predicciones y obtener resultados
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
from ..services.forecast_service import ForecastService

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

# Instancia global del servicio
forecast_service = ForecastService()


class ForecastRequest(BaseModel):
    """Modelo para solicitar predicciones"""
    series_id: Optional[str] = None  # Si es None, procesa todas las series


@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """Sube y carga un archivo CSV con datos de ventas"""
    try:
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Cargar datos
        df = forecast_service.load_data(tmp_path)
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        return {
            "message": "Datos cargados exitosamente",
            "series_count": df['unique_id'].nunique(),
            "total_records": len(df),
            "date_range": {
                "min": df['ds'].min().isoformat(),
                "max": df['ds'].max().isoformat()
            },
            "series_list": df['unique_id'].unique().tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al cargar datos: {str(e)}")


@router.get("/series")
async def get_series():
    """Obtiene la lista de series disponibles"""
    if forecast_service.Y_df is None:
        raise HTTPException(status_code=400, detail="No hay datos cargados")
    
    series_list = forecast_service.Y_df['unique_id'].unique().tolist()
    return {"series": series_list}


@router.get("/series/{series_id}")
async def get_series_data(series_id: str):
    """Obtiene los datos de una serie específica"""
    try:
        return forecast_service.get_series_data(series_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/predict")
async def generate_forecast(request: ForecastRequest = None):
    """
    Genera predicciones completas con los modelos entrenados
    
    Si series_id es None, procesa todas las series disponibles
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Solicitud de predicción recibida")
        result = forecast_service.generate_full_forecast()
        
        # Si se especifica una serie, filtrar resultados
        if request and request.series_id:
            series_id = request.series_id
            logger.info(f"Filtrando resultados para serie: {series_id}")
            result['train'] = [r for r in result['train'] if str(r.get('unique_id')) == str(series_id)]
            result['test_real'] = [r for r in result['test_real'] if str(r.get('unique_id')) == str(series_id)]
            result['predictions'] = [r for r in result['predictions'] if str(r.get('unique_id')) == str(series_id)]
            result['future'] = [r for r in result['future'] if str(r.get('unique_id')) == str(series_id)]
            result['metrics'] = [m for m in result['metrics'] if str(m.get('series_id')) == str(series_id)]
        
        logger.info("Predicción completada exitosamente")
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al generar predicciones: {str(e)}")


@router.get("/metrics")
async def get_metrics():
    """Obtiene las métricas de los últimos modelos entrenados"""
    # Esto requeriría almacenar las métricas en el servicio
    # Por ahora, necesitarías generar el forecast primero
    return {"message": "Genera predicciones primero usando /api/forecast/predict"}

