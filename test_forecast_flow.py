"""
Script para probar el flujo completo de forecasting y encontrar dónde falla
"""
import pandas as pd
import numpy as np
import sys
import traceback

# Simular el código del servicio
csv_path = r"c:\Users\smart\Downloads\demo_series_family_sales.csv"

print("=" * 60)
print("PRUEBA DEL FLUJO COMPLETO DE FORECASTING")
print("=" * 60)

try:
    # 1. Cargar datos (simulando load_data)
    print("\n[PASO 1] Cargando datos...")
    df = pd.read_csv(csv_path)
    df['unique_id'] = df['family'].astype(str)
    df['ds'] = pd.to_datetime(df['date'])
    df['y'] = pd.to_numeric(df['sales'], errors='coerce')
    df = df.dropna(subset=['ds', 'y'])
    df = df.sort_values(['unique_id', 'ds'])
    Y_df = df[['unique_id', 'ds', 'y']].copy()
    print(f"   OK - {len(Y_df)} registros, {Y_df['unique_id'].nunique()} series")

    # 2. Preparar train/test
    print("\n[PASO 2] Preparando train/test...")
    test_weeks = 12
    cutoff_date = Y_df['ds'].max() - pd.Timedelta(weeks=test_weeks)
    Y_train = Y_df[Y_df['ds'] <= cutoff_date].copy()
    Y_test_real = Y_df[Y_df['ds'] > cutoff_date].copy()
    print(f"   OK - Train: {len(Y_train)}, Test: {len(Y_test_real)}")

    # 3. Winsorización
    print("\n[PASO 3] Aplicando winsorización...")
    upper_quantile = 0.80
    
    def winsorize_train_data(group, upper_quantile):
        upper_limit = group['y'].quantile(upper_quantile)
        group['y'] = group['y'].clip(lower=0, upper=upper_limit)
        return group
    
    Y_train_clean = Y_train.groupby('unique_id').apply(
        lambda x: winsorize_train_data(x, upper_quantile)
    ).reset_index(drop=True)
    print(f"   OK - Datos limpiados: {len(Y_train_clean)} registros")

    # 4. Intentar entrenar modelos (sin StatsForecast real, solo verificar datos)
    print("\n[PASO 4] Verificando datos para entrenamiento...")
    print(f"   Series en train: {Y_train_clean['unique_id'].unique().tolist()}")
    for series_id in Y_train_clean['unique_id'].unique():
        series_data = Y_train_clean[Y_train_clean['unique_id'] == series_id]
        print(f"   - Serie '{series_id}': {len(series_data)} registros, "
              f"rango: {series_data['y'].min():.2f} - {series_data['y'].max():.2f}")
    
    # Verificar que no haya problemas obvios
    if Y_train_clean['y'].isna().any():
        print("   ERROR: Hay valores NaN después de winsorización")
        sys.exit(1)
    if (Y_train_clean['y'] < 0).any():
        print("   ERROR: Hay valores negativos después de winsorización")
        sys.exit(1)
    print("   OK - Datos listos para entrenamiento")

    # 5. Simular predicciones (sin StatsForecast real)
    print("\n[PASO 5] Simulando estructura de predicciones...")
    # StatsForecast.predict() retorna un DataFrame con:
    # - unique_id como índice o columna
    # - ds como índice o columna  
    # - Columnas para cada modelo
    
    # Simular estructura esperada
    print("   Estructura esperada de Y_hat:")
    print("   - Debe tener columnas: unique_id, ds, y columnas de modelos")
    print("   - Debe tener predicciones para las fechas de test")
    
    # Verificar fechas de test
    print(f"\n   Fechas en Y_test_real: {len(Y_test_real)}")
    print(f"   Fechas únicas: {Y_test_real['ds'].nunique()}")
    for series_id in Y_test_real['unique_id'].unique():
        test_series = Y_test_real[Y_test_real['unique_id'] == series_id]
        print(f"   - Serie '{series_id}': {len(test_series)} fechas")
        print(f"     Primera: {test_series['ds'].min().date()}, Última: {test_series['ds'].max().date()}")

    # 6. Simular merge (el problema más probable)
    print("\n[PASO 6] Simulando merge de métricas...")
    print("   PROBLEMA POTENCIAL: Si las fechas en Y_hat no coinciden exactamente")
    print("   con las fechas en Y_test_real, el merge fallará o dejará NaN")
    
    # Crear un Y_hat simulado con las mismas fechas
    Y_hat_simulado = Y_test_real[['unique_id', 'ds']].copy()
    Y_hat_simulado['Naive'] = Y_test_real['y'] * 1.1  # Simular predicción
    Y_hat_simulado['Auto_Smoothing'] = Y_test_real['y'] * 0.95
    
    # Intentar merge
    eval_df = Y_test_real.merge(Y_hat_simulado, on=['unique_id', 'ds'], how='left')
    print(f"   OK - Merge exitoso: {len(eval_df)} filas")
    print(f"   Columnas resultantes: {list(eval_df.columns)}")
    
    # Verificar NaN
    nan_count = eval_df.isna().sum().sum()
    if nan_count > 0:
        print(f"   WARNING: {nan_count} valores NaN después del merge")
        print(f"   Esto podría causar problemas en calculate_metrics")
    else:
        print("   OK - No hay NaN después del merge")

    # 7. Simular cálculo de métricas
    print("\n[PASO 7] Simulando cálculo de métricas...")
    model_cols = [c for c in eval_df.columns if c not in ['unique_id', 'ds', 'y']]
    print(f"   Modelos encontrados: {model_cols}")
    
    for model in model_cols:
        eval_df[model] = eval_df[model].clip(lower=0)
        for unique_id in eval_df['unique_id'].unique():
            series_data = eval_df[eval_df['unique_id'] == unique_id]
            if len(series_data) > 0:
                try:
                    mae = np.mean(np.abs(series_data['y'] - series_data[model]))
                    mean_real = series_data['y'].mean()
                    accuracy = (1 - (mae / mean_real)) * 100 if mean_real > 0 else 0.0
                    print(f"   OK - {unique_id}/{model}: MAE={mae:.2f}, Accuracy={accuracy:.1f}%")
                except Exception as e:
                    print(f"   ERROR en {unique_id}/{model}: {str(e)}")
                    print(f"   Series data shape: {series_data.shape}")
                    print(f"   Series data columns: {list(series_data.columns)}")
                    print(f"   Series data dtypes:\n{series_data.dtypes}")
                    print(f"   Series data head:\n{series_data.head()}")

    # 8. Simular conversión a dict
    print("\n[PASO 8] Simulando conversión a dict para JSON...")
    try:
        train_dict = Y_train.to_dict('records')
        print(f"   OK - Train: {len(train_dict)} registros convertidos")
        
        test_dict = Y_test_real.to_dict('records')
        print(f"   OK - Test: {len(test_dict)} registros convertidos")
        
        # Verificar valores problemáticos
        for record in train_dict[:5]:
            for key, value in record.items():
                if pd.isna(value) or np.isinf(value) if isinstance(value, (int, float)) else False:
                    print(f"   WARNING: Valor problemático en train: {key}={value}")
        
    except Exception as e:
        print(f"   ERROR al convertir a dict: {str(e)}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("=" * 60)
    print("El CSV está bien formateado y debería funcionar.")
    print("\nPosibles problemas en el código real:")
    print("1. StatsForecast.predict() puede retornar fechas diferentes a Y_test_real")
    print("2. El merge puede fallar si las fechas no coinciden exactamente")
    print("3. Valores NaN/inf en predicciones pueden romper la serialización JSON")
    print("4. Algunos modelos pueden fallar con muchos valores en 0 (serie B)")
    print("\nRecomendación: Agregar mejor manejo de errores y logging")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR ENCONTRADO: {str(e)}")
    print("\nTraceback completo:")
    traceback.print_exc()
    sys.exit(1)

