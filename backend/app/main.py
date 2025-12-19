"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import config, forecast

app = FastAPI(
    title="Forecast API",
    description="API para predicciones de series de tiempo con StatsForecast",
    version="2.0.0"
)

# Configurar CORS - Permitir desde cualquier origen para acceso desde red local
import os
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    # En desarrollo, permitir todos los orígenes para acceso desde red local
    allow_origins = ["*"]
else:
    allow_origins = cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins != ["*"] else ["*"],
    allow_credentials=True if allow_origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(config.router)
app.include_router(forecast.router)


@app.get("/")
async def root():
    return {"message": "Forecast API v2.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

