"""
Servicio de forecasting adaptado del notebook Nixtla_forecast_v2
"""
import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from statsforecast import StatsForecast
from statsforecast.models import (
    Naive, 
    SimpleExponentialSmoothing, 
    Holt, 
    AutoETS,
    WindowAverage,
    AutoARIMA
)
# RandomWalkWithDrift se importa dinámicamente en train_models() por compatibilidad

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        try:
            logger.info(f"Cargando datos desde {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"CSV cargado: {len(df)} filas, columnas: {list(df.columns)}")
            
            # Convertir a formato StatsForecast: unique_id, ds, y
            if id_col not in df.columns:
                # Si no hay id_col, crear uno basado en otras columnas
                if 'family' in df.columns:
                    df['unique_id'] = df['family'].astype(str)
                    logger.info("Usando columna 'family' como identificador")
                else:
                    df['unique_id'] = 'SERIES_1'
                    logger.info("No se encontró identificador, creando serie única 'SERIES_1'")
            else:
                df['unique_id'] = df[id_col].astype(str)
                logger.info(f"Usando columna '{id_col}' como identificador")
                
            # Verificar que existan las columnas necesarias
            if date_col not in df.columns:
                raise ValueError(f"Columna de fecha '{date_col}' no encontrada. Columnas disponibles: {list(df.columns)}")
            if value_col not in df.columns:
                raise ValueError(f"Columna de valores '{value_col}' no encontrada. Columnas disponibles: {list(df.columns)}")
            
            df['ds'] = pd.to_datetime(df[date_col], errors='coerce')
            df['y'] = pd.to_numeric(df[value_col], errors='coerce')
            
            # Eliminar valores nulos
            initial_count = len(df)
            df = df.dropna(subset=['ds', 'y'])
            removed_count = initial_count - len(df)
            if removed_count > 0:
                logger.warning(f"Se eliminaron {removed_count} filas con valores nulos")
            
            if len(df) == 0:
                raise ValueError("No quedaron datos válidos después de la limpieza")
            
            # Ordenar
            df = df.sort_values(['unique_id', 'ds'])
            
            self.Y_df = df[['unique_id', 'ds', 'y']].copy()
            logger.info(f"Datos procesados: {len(self.Y_df)} registros, {self.Y_df['unique_id'].nunique()} series")
            return self.Y_df
            
        except Exception as e:
            logger.error(f"Error al cargar datos: {str(e)}", exc_info=True)
            raise ValueError(f"Error al cargar datos: {str(e)}")
    
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
        try:
            logger.info(f"Entrenando modelos con {len(Y_train_clean)} registros")
            
            # Verificar que tenemos datos suficientes
            if len(Y_train_clean) == 0:
                raise ValueError("No hay datos para entrenar los modelos")
            
            # Verificar que tenemos las columnas necesarias
            required_cols = ['unique_id', 'ds', 'y']
            missing_cols = [col for col in required_cols if col not in Y_train_clean.columns]
            if missing_cols:
                raise ValueError(f"Faltan columnas requeridas: {missing_cols}")
            
            ventanas_a_probar = [2, 3, 4, 6, 8]
            
            # Intentar importar RandomWalkWithDrift, si falla usar RWD
            try:
                from statsforecast.models import RandomWalkWithDrift
                rwd_model = RandomWalkWithDrift()
            except ImportError:
                try:
                    from statsforecast.models import RWD
                    rwd_model = RWD()
                except ImportError:
                    logger.warning("No se pudo importar RandomWalkWithDrift/RWD, omitiendo este modelo")
                    rwd_model = None
            
            models = [
                Naive(),
                AutoETS(model='ZZN', season_length=1, alias='Auto_Smoothing'),
                *[WindowAverage(window_size=w, alias=f"MovAvg_{w}") for w in ventanas_a_probar],
            ]
            
            # Agregar RWD si está disponible
            if rwd_model is not None:
                models.append(rwd_model)
            
            models.append(AutoARIMA())
            
            logger.info(f"Configurando StatsForecast con {len(models)} modelos")
            self.sf = StatsForecast(
                models=models,
                freq='W-MON',
                n_jobs=-1
            )
            
            logger.info("Iniciando entrenamiento...")
            self.sf.fit(df=Y_train_clean)
            logger.info("Entrenamiento completado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al entrenar modelos: {str(e)}", exc_info=True)
            raise ValueError(f"Error al entrenar modelos: {str(e)}")
    
    def predict(self, horizon: Optional[int] = None) -> pd.DataFrame:
        """
        Genera predicciones con los modelos entrenados
        
        Args:
            horizon: Horizonte de predicción (usa conf['horizon'] si no se especifica)
            
        Returns:
            DataFrame con predicciones en formato: unique_id, ds, modelo1, modelo2, ...
        """
        if self.sf is None:
            raise ValueError("Los modelos no han sido entrenados. Entrena primero.")
        
        try:
            h = horizon or self.conf['horizon']
            logger.info(f"Generando predicciones con horizonte h={h}")
            
            # StatsForecast.predict() retorna un DataFrame
            Y_hat = self.sf.predict(h=h)
            
            # Asegurar que tenemos las columnas correctas
            if Y_hat is None or len(Y_hat) == 0:
                raise ValueError("StatsForecast no retornó predicciones")
            
            logger.info(f"Formato inicial de Y_hat: index={type(Y_hat.index)}, columns={list(Y_hat.columns)}")
            
            # Siempre resetear el índice para asegurar que tenemos columnas
            # StatsForecast puede retornar MultiIndex con unique_id y ds
            Y_hat = Y_hat.reset_index()
            
            logger.info(f"Después de reset_index: columns={list(Y_hat.columns)}")
            
            # Verificar que tenemos unique_id y ds
            if 'unique_id' not in Y_hat.columns:
                # Buscar en el índice
                if hasattr(Y_hat.index, 'names') and 'unique_id' in Y_hat.index.names:
                    Y_hat = Y_hat.reset_index(level='unique_id')
                else:
                    # Si no está, puede que StatsForecast use otro nombre
                    # Buscar columnas que puedan ser el identificador
                    possible_id_cols = [c for c in Y_hat.columns if 'id' in c.lower() or c == 'series_id']
                    if possible_id_cols:
                        Y_hat = Y_hat.rename(columns={possible_id_cols[0]: 'unique_id'})
                    else:
                        raise ValueError(f"No se pudo encontrar 'unique_id' en las predicciones. Columnas: {list(Y_hat.columns)}")
            
            if 'ds' not in Y_hat.columns:
                # Buscar columnas de fecha
                possible_date_cols = [c for c in Y_hat.columns if 'date' in c.lower() or c == 'timestamp']
                if possible_date_cols:
                    Y_hat = Y_hat.rename(columns={possible_date_cols[0]: 'ds'})
                else:
                    raise ValueError(f"No se pudo encontrar 'ds' en las predicciones. Columnas: {list(Y_hat.columns)}")
            
            # Asegurar que ds sea datetime
            if not pd.api.types.is_datetime64_any_dtype(Y_hat['ds']):
                Y_hat['ds'] = pd.to_datetime(Y_hat['ds'], errors='coerce')
            
            # Asegurar que unique_id sea string
            Y_hat['unique_id'] = Y_hat['unique_id'].astype(str)
            
            # Reemplazar valores infinitos y NaN con 0 en columnas de modelos
            model_cols = [c for c in Y_hat.columns if c not in ['unique_id', 'ds']]
            for col in model_cols:
                Y_hat[col] = Y_hat[col].replace([np.inf, -np.inf], np.nan)
                Y_hat[col] = Y_hat[col].fillna(0)
                Y_hat[col] = Y_hat[col].clip(lower=0)  # Asegurar no negativos
            
            logger.info(f"Predicciones generadas: {len(Y_hat)} filas, {len(model_cols)} modelos")
            logger.info(f"Columnas finales: {list(Y_hat.columns)}")
            return Y_hat
            
        except Exception as e:
            logger.error(f"Error al generar predicciones: {str(e)}", exc_info=True)
            raise ValueError(f"Error al generar predicciones: {str(e)}")
    
    def _clean_dataframe_for_json(self, df: pd.DataFrame) -> List[Dict]:
        """
        Limpia un DataFrame para convertirlo a JSON de forma segura
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            Lista de diccionarios
        """
        df_clean = df.copy()
        
        # Convertir fechas a string ISO
        if 'ds' in df_clean.columns:
            df_clean['ds'] = pd.to_datetime(df_clean['ds']).dt.strftime('%Y-%m-%d')
        
        # Reemplazar NaN e infinitos en columnas numéricas
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
            df_clean[col] = df_clean[col].fillna(0)
        
        # Convertir a dict
        records = df_clean.to_dict('records')
        
        # Asegurar que todos los valores sean serializables
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, (np.integer, np.floating)):
                    record[key] = float(value) if np.isfinite(value) else 0.0
                elif isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
        
        return records
    
    def generate_full_forecast(self) -> Dict:
        """
        Genera el forecast completo: entrenamiento, validación y proyección futura
        
        Returns:
            Diccionario con todos los resultados y métricas
        """
        try:
            logger.info("Iniciando generación de forecast completo...")
            
            # 1. Preparar datos
            logger.info("Paso 1/7: Preparando train/test split...")
            Y_train, Y_test_real, cutoff_date = self.prepare_train_test()
            logger.info(f"Train: {len(Y_train)} registros, Test: {len(Y_test_real)} registros")
            
            # 2. Winsorización del train
            logger.info("Paso 2/7: Aplicando winsorización...")
            Y_train_clean = Y_train.groupby('unique_id', group_keys=False).apply(
                lambda x: self.winsorize_train_data(x, self.conf['upper_quantile'])
            ).reset_index(drop=True)
            
            # 3. Entrenar modelos
            logger.info("Paso 3/7: Entrenando modelos...")
            self.train_models(Y_train_clean)
            
            # 4. Predecir para validación
            logger.info("Paso 4/7: Generando predicciones de validación...")
            Y_hat = self.predict(h=self.conf['test_weeks'])
            
            # 5. Calcular métricas
            logger.info("Paso 5/7: Calculando métricas...")
            metrics = self.calculate_metrics(Y_test_real, Y_hat)
            
            # 6. Re-entrenar con datos completos y predecir futuro
            logger.info("Paso 6/7: Re-entrenando con datos completos y prediciendo futuro...")
            Y_full_clean = self.Y_df.groupby('unique_id', group_keys=False).apply(
                lambda x: self.winsorize_train_data(x, self.conf['upper_quantile'])
            ).reset_index(drop=True)
            
            self.sf.fit(df=Y_full_clean)
            Y_future = self.predict(h=self.conf['horizon'])
            
            # 7. Preparar datos para visualización
            logger.info("Paso 7/7: Preparando datos para visualización...")
            result = {
                'train': self._clean_dataframe_for_json(Y_train),
                'test_real': self._clean_dataframe_for_json(Y_test_real),
                'predictions': self._clean_dataframe_for_json(Y_hat),
                'future': self._clean_dataframe_for_json(Y_future),
                'metrics': metrics,
                'cutoff_date': cutoff_date.isoformat() if isinstance(cutoff_date, pd.Timestamp) else str(cutoff_date),
                'series_list': [str(s) for s in self.Y_df['unique_id'].unique().tolist()]
            }
            
            logger.info("Forecast generado exitosamente")
            return result
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            # Imprimir directamente para logs de Docker
            print(f"ERROR EN generate_full_forecast: {error_msg}")
            print(f"TRACEBACK:\n{error_trace}")
            logger.error(f"Error en generate_full_forecast: {error_msg}\n{error_trace}")
            raise ValueError(f"Error al generar forecast: {error_msg}")
    
    def calculate_metrics(self, Y_test_real: pd.DataFrame, Y_hat: pd.DataFrame) -> List[Dict]:
        """
        Calcula métricas de precisión para cada modelo y serie
        
        Returns:
            Lista de diccionarios con métricas por modelo y serie
        """
        try:
            logger.info("Calculando métricas...")
            
            # Asegurar que las fechas sean comparables (mismo tipo)
            Y_test_real = Y_test_real.copy()
            Y_hat = Y_hat.copy()
            
            # Convertir fechas a mismo formato si es necesario
            if not pd.api.types.is_datetime64_any_dtype(Y_test_real['ds']):
                Y_test_real['ds'] = pd.to_datetime(Y_test_real['ds'])
            if not pd.api.types.is_datetime64_any_dtype(Y_hat['ds']):
                Y_hat['ds'] = pd.to_datetime(Y_hat['ds'])
            
            # Normalizar fechas a mismo timezone si es necesario
            Y_test_real['ds'] = pd.to_datetime(Y_test_real['ds']).dt.normalize()
            Y_hat['ds'] = pd.to_datetime(Y_hat['ds']).dt.normalize()
            
            # Unir predicciones con datos reales
            # Usar 'outer' para ver todas las fechas, luego filtrar
            eval_df = Y_test_real.merge(Y_hat, on=['unique_id', 'ds'], how='left', suffixes=('', '_pred'))
            
            # Si hay columnas duplicadas, manejar
            if 'y_pred' in eval_df.columns:
                eval_df = eval_df.drop(columns=['y_pred'])
            
            # Identificar columnas de modelos (excluir metadatos)
            model_cols = [c for c in eval_df.columns if c not in ['unique_id', 'ds', 'y']]
            
            if len(model_cols) == 0:
                logger.warning("No se encontraron columnas de modelos en las predicciones")
                return []
            
            logger.info(f"Modelos encontrados: {model_cols}")
            
            metrics = []
            
            for model in model_cols:
                # Reemplazar NaN e infinitos
                eval_df[model] = eval_df[model].replace([np.inf, -np.inf], np.nan)
                eval_df[model] = eval_df[model].fillna(0)
                eval_df[model] = eval_df[model].clip(lower=0)
                
                # Calcular MAE por serie
                for unique_id in eval_df['unique_id'].unique():
                    series_data = eval_df[eval_df['unique_id'] == unique_id].copy()
                    
                    # Filtrar solo filas donde tenemos tanto datos reales como predicciones
                    series_data = series_data.dropna(subset=['y', model])
                    
                    if len(series_data) == 0:
                        logger.warning(f"No hay datos válidos para calcular métricas de {unique_id}/{model}")
                        continue
                    
                    try:
                        mae = np.mean(np.abs(series_data['y'] - series_data[model]))
                        mean_real = series_data['y'].mean()
                        
                        # Manejar caso donde mean_real es 0
                        if mean_real == 0:
                            accuracy = 0.0
                        else:
                            accuracy = (1 - (mae / mean_real)) * 100
                        
                        # Asegurar que accuracy esté en rango válido
                        accuracy = max(0.0, min(100.0, accuracy))
                        
                        metrics.append({
                            'series_id': str(unique_id),
                            'model': str(model),
                            'mae': float(mae) if not (np.isnan(mae) or np.isinf(mae)) else 0.0,
                            'accuracy': float(accuracy),
                            'mean_real': float(mean_real) if not (np.isnan(mean_real) or np.isinf(mean_real)) else 0.0,
                            'decision': 'PREDECIR' if accuracy >= self.conf['min_accuracy'] else 'NO_PREDECIR'
                        })
                    except Exception as e:
                        logger.warning(f"Error calculando métricas para {unique_id}/{model}: {str(e)}")
                        continue
            
            logger.info(f"Métricas calculadas: {len(metrics)} resultados")
            return metrics
            
        except Exception as e:
            logger.error(f"Error al calcular métricas: {str(e)}", exc_info=True)
            raise ValueError(f"Error al calcular métricas: {str(e)}")
    
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

