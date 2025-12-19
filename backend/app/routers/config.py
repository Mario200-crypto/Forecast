"""
Router para gestionar la configuración de parámetros
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from ..services.forecast_service import ForecastService

router = APIRouter(prefix="/api/config", tags=["config"])

# Instancia global del servicio (en producción usarías dependency injection)
forecast_service = ForecastService()


class ConfigUpdate(BaseModel):
    """Modelo para actualizar configuración"""
    test_weeks: Optional[int] = None
    horizon: Optional[int] = None
    zero_threshold: Optional[float] = None
    cv_threshold: Optional[int] = None
    min_accuracy: Optional[float] = None
    upper_quantile: Optional[float] = None
    report_save_mode: Optional[str] = None


@router.get("/")
async def get_config():
    """Obtiene la configuración actual"""
    return forecast_service.get_config()


@router.put("/")
async def update_config(config: ConfigUpdate):
    """Actualiza la configuración con nuevos parámetros"""
    update_dict = config.dict(exclude_unset=True)
    forecast_service.update_config(update_dict)
    return {
        "message": "Configuración actualizada exitosamente",
        "config": forecast_service.get_config()
    }


@router.post("/reset")
async def reset_config():
    """Restaura la configuración a valores por defecto"""
    forecast_service.conf = {
        "test_weeks": 12,
        "horizon": 12,
        "zero_threshold": 0.50,
        "cv_threshold": 10,
        "min_accuracy": 60.0,
        "upper_quantile": 0.80,
        "input_path": None,
        "output_path_report": None,
        "output_path_graphs": None,
        "report_save_mode": 'overwrite'
    }
    return {
        "message": "Configuración restaurada a valores por defecto",
        "config": forecast_service.get_config()
    }

