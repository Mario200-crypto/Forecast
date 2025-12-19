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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
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

