"""
Servicio de forecasting adaptado del notebook Nixtla_forecast_v2
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from statsforecast import StatsForecast
from statsforecast.models import (
    Naive, 
    SimpleExponentialSmoothing, 
    Holt, 
    AutoETS,
    WindowAverage,
    RandomWalkWithDrift,
    AutoARIMA
)


class ForecastService:
    """Servicio para generar predicciones usando StatsForecast"""
    
    def __init__(self):
        self.conf = {
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
        self.df_full = None
        self.Y_df = None
        self.sf = None
        
    def update_config(self, config: Dict):
        """Actualiza la configuración con nuevos parámetros"""
        self.conf.update(config)
        
    def get_config(self) -> Dict:
        """Retorna la configuración actual"""
        return self.conf.copy()
    
    def load_data(self, file_path: str, date_col: str = 'date', 
                  value_col: str = 'sales', id_col: str = 'id'):
        """
        Carga datos desde un archivo CSV y los convierte al formato requerido
        
        Args:
            file_path: Ruta al archivo CSV
            date_col: Nombre de la columna de fecha
            value_col: Nombre de la columna de valores (ventas)
            id_col: Nombre de la columna de identificador único
        """
        df = pd.read_csv(file_path)
        
        # Convertir a formato StatsForecast: unique_id, ds, y
        if id_col not in df.columns:
            # Si no hay id_col, crear uno basado en otras columnas
            if 'family' in df.columns:
                df['unique_id'] = df['family'].astype(str)
            else:
                df['unique_id'] = 'SERIES_1'
        else:
            df['unique_id'] = df[id_col].astype(str)
            
        df['ds'] = pd.to_datetime(df[date_col])
        df['y'] = pd.to_numeric(df[value_col], errors='coerce')
        
        # Eliminar valores nulos
        df = df.dropna(subset=['ds', 'y'])
        
        # Ordenar
        df = df.sort_values(['unique_id', 'ds'])
        
        self.Y_df = df[['unique_id', 'ds', 'y']].copy()
        return self.Y_df
    
    def winsorize_train_data(self, group: pd.DataFrame, upper_quantile: float) -> pd.DataFrame:
        """Aplica winsorización a los datos de entrenamiento"""
        upper_limit = group['y'].quantile(upper_quantile)
        group['y'] = group['y'].clip(lower=0, upper=upper_limit)
        return group
    
    def prepare_train_test(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
        """
        Divide los datos en train y test según la configuración
        
        Returns:
            Tuple de (Y_train, Y_test_real, cutoff_date)
        """
        if self.Y_df is None or len(self.Y_df) == 0:
            raise ValueError("No hay datos cargados. Carga datos primero.")
        
        # Definir punto de corte
        cutoff_date = self.Y_df['ds'].max() - pd.Timedelta(weeks=self.conf['test_weeks'])
        
        # Separación estricta
        Y_train = self.Y_df[self.Y_df['ds'] <= cutoff_date].copy()
        Y_test_real = self.Y_df[self.Y_df['ds'] > cutoff_date].copy()
        
        return Y_train, Y_test_real, cutoff_date
    
    def train_models(self, Y_train_clean: pd.DataFrame):
        """Entrena los modelos de forecasting"""
        ventanas_a_probar = [2, 3, 4, 6, 8]
        
        models = [
            Naive(),
            AutoETS(model='ZZN', season_length=1, alias='Auto_Smoothing'),
            *[WindowAverage(window_size=w, alias=f"MovAvg_{w}") for w in ventanas_a_probar],
            RandomWalkWithDrift(),
            AutoARIMA()
        ]
        
        self.sf = StatsForecast(
            models=models,
            freq='W-MON',
            n_jobs=-1
        )
        
        self.sf.fit(df=Y_train_clean)
    
    def predict(self, horizon: Optional[int] = None) -> pd.DataFrame:
        """
        Genera predicciones con los modelos entrenados
        
        Args:
            horizon: Horizonte de predicción (usa conf['horizon'] si no se especifica)
            
        Returns:
            DataFrame con predicciones
        """
        if self.sf is None:
            raise ValueError("Los modelos no han sido entrenados. Entrena primero.")
        
        h = horizon or self.conf['horizon']
        Y_hat = self.sf.predict(h=h)
        return Y_hat.reset_index()
    
    def generate_full_forecast(self) -> Dict:
        """
        Genera el forecast completo: entrenamiento, validación y proyección futura
        
        Returns:
            Diccionario con todos los resultados y métricas
        """
        # 1. Preparar datos
        Y_train, Y_test_real, cutoff_date = self.prepare_train_test()
        
        # 2. Winsorización del train
        Y_train_clean = Y_train.groupby('unique_id').apply(
            lambda x: self.winsorize_train_data(x, self.conf['upper_quantile'])
        ).reset_index(drop=True)
        
        # 3. Entrenar modelos
        self.train_models(Y_train_clean)
        
        # 4. Predecir para validación
        Y_hat = self.predict(h=self.conf['test_weeks'])
        
        # 5. Calcular métricas
        metrics = self.calculate_metrics(Y_test_real, Y_hat)
        
        # 6. Re-entrenar con datos completos y predecir futuro
        Y_full_clean = self.Y_df.groupby('unique_id').apply(
            lambda x: self.winsorize_train_data(x, self.conf['upper_quantile'])
        ).reset_index(drop=True)
        
        self.sf.fit(df=Y_full_clean)
        Y_future = self.predict(h=self.conf['horizon'])
        
        # 7. Preparar datos para visualización
        result = {
            'train': Y_train.to_dict('records'),
            'test_real': Y_test_real.to_dict('records'),
            'predictions': Y_hat.to_dict('records'),
            'future': Y_future.to_dict('records'),
            'metrics': metrics,
            'cutoff_date': cutoff_date.isoformat(),
            'series_list': self.Y_df['unique_id'].unique().tolist()
        }
        
        return result
    
    def calculate_metrics(self, Y_test_real: pd.DataFrame, Y_hat: pd.DataFrame) -> List[Dict]:
        """
        Calcula métricas de precisión para cada modelo y serie
        
        Returns:
            Lista de diccionarios con métricas por modelo y serie
        """
        # Unir predicciones con datos reales
        eval_df = Y_test_real.merge(Y_hat, on=['unique_id', 'ds'], how='left')
        
        # Identificar columnas de modelos
        model_cols = [c for c in eval_df.columns if c not in ['unique_id', 'ds', 'y']]
        
        metrics = []
        
        for model in model_cols:
            # Clipping a 0
            eval_df[model] = eval_df[model].clip(lower=0)
            
            # Calcular MAE por serie
            for unique_id in eval_df['unique_id'].unique():
                series_data = eval_df[eval_df['unique_id'] == unique_id]
                
                if len(series_data) > 0:
                    mae = np.mean(np.abs(series_data['y'] - series_data[model]))
                    mean_real = series_data['y'].mean()
                    
                    accuracy = (1 - (mae / mean_real)) * 100 if mean_real > 0 else 0.0
                    
                    metrics.append({
                        'series_id': unique_id,
                        'model': model,
                        'mae': float(mae),
                        'accuracy': float(accuracy),
                        'mean_real': float(mean_real),
                        'decision': 'PREDECIR' if accuracy >= self.conf['min_accuracy'] else 'NO_PREDECIR'
                    })
        
        return metrics
    
    def get_series_data(self, series_id: str) -> Dict:
        """
        Obtiene todos los datos y predicciones para una serie específica
        
        Returns:
            Diccionario con datos de la serie
        """
        if self.Y_df is None:
            raise ValueError("No hay datos cargados.")
        
        series_data = self.Y_df[self.Y_df['unique_id'] == series_id].copy()
        
        return {
            'series_id': series_id,
            'data': series_data.to_dict('records'),
            'date_range': {
                'min': series_data['ds'].min().isoformat(),
                'max': series_data['ds'].max().isoformat()
            }
        }

