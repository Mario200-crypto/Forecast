"""
Script de diagnóstico para analizar el CSV y ver qué espera el código
"""
import pandas as pd
import numpy as np

# Cargar el CSV
csv_path = r"c:\Users\smart\Downloads\demo_series_family_sales.csv"
df = pd.read_csv(csv_path)

print("=" * 60)
print("ANÁLISIS DEL CSV")
print("=" * 60)

print(f"\n1. COLUMNAS EN EL CSV:")
print(f"   {list(df.columns)}")

print(f"\n2. FORMATO DE DATOS:")
print(f"   Total de filas: {len(df)}")
print(f"   Filas con valores nulos: {df.isnull().sum().sum()}")

print(f"\n3. SERIES ÚNICAS (family):")
series = df['family'].unique()
print(f"   Series encontradas: {series}")
print(f"   Total de series: {len(series)}")

for s in series:
    count = len(df[df['family'] == s])
    zeros = len(df[(df['family'] == s) & (df['sales'] == 0)])
    print(f"   - Serie '{s}': {count} registros, {zeros} ceros ({zeros/count*100:.1f}%)")

print(f"\n4. RANGO DE FECHAS:")
df['date'] = pd.to_datetime(df['date'])
print(f"   Fecha mínima: {df['date'].min()}")
print(f"   Fecha máxima: {df['date'].max()}")
print(f"   Total de semanas: {(df['date'].max() - df['date'].min()).days / 7:.1f}")

print(f"\n5. VALORES DE SALES:")
print(f"   Mínimo: {df['sales'].min()}")
print(f"   Máximo: {df['sales'].max()}")
print(f"   Media: {df['sales'].mean():.2f}")
print(f"   Valores en 0: {len(df[df['sales'] == 0])} ({len(df[df['sales'] == 0])/len(df)*100:.1f}%)")

print(f"\n6. SIMULACIÓN DE LO QUE HACE EL CÓDIGO:")
print("   " + "-" * 56)

# Simular load_data
df_test = df.copy()
df_test['unique_id'] = df_test['family'].astype(str)
df_test['ds'] = pd.to_datetime(df_test['date'])
df_test['y'] = pd.to_numeric(df_test['sales'], errors='coerce')
df_test = df_test.dropna(subset=['ds', 'y'])
df_test = df_test.sort_values(['unique_id', 'ds'])
df_final = df_test[['unique_id', 'ds', 'y']].copy()

print(f"   [OK] Despues de load_data:")
print(f"      - Total registros: {len(df_final)}")
print(f"      - Series: {df_final['unique_id'].unique().tolist()}")

# Simular prepare_train_test con test_weeks=12
test_weeks = 12
cutoff_date = df_final['ds'].max() - pd.Timedelta(weeks=test_weeks)
Y_train = df_final[df_final['ds'] <= cutoff_date].copy()
Y_test_real = df_final[df_final['ds'] > cutoff_date].copy()

print(f"\n   [OK] Despues de prepare_train_test (test_weeks={test_weeks}):")
print(f"      - Fecha de corte: {cutoff_date.date()}")
print(f"      - Train: {len(Y_train)} registros")
print(f"      - Test: {len(Y_test_real)} registros")

# Verificar por serie
print(f"\n   Por serie:")
for series_id in df_final['unique_id'].unique():
    train_series = Y_train[Y_train['unique_id'] == series_id]
    test_series = Y_test_real[Y_test_real['unique_id'] == series_id]
    print(f"      - Serie '{series_id}':")
    print(f"        Train: {len(train_series)} registros")
    print(f"        Test: {len(test_series)} registros")
    if len(train_series) > 0:
        print(f"        Train - Ceros: {len(train_series[train_series['y'] == 0])} ({len(train_series[train_series['y'] == 0])/len(train_series)*100:.1f}%)")
    if len(test_series) > 0:
        print(f"        Test - Ceros: {len(test_series[test_series['y'] == 0])} ({len(test_series[test_series['y'] == 0])/len(test_series)*100:.1f}%)")

# Verificar frecuencia semanal
print(f"\n7. VERIFICACIÓN DE FRECUENCIA SEMANAL:")
first_date = df_final['ds'].min()
print(f"   Primera fecha: {first_date} ({first_date.strftime('%A')})")
if first_date.weekday() == 0:
    print(f"   [OK] Es lunes - compatible con freq='W-MON'")
else:
    print(f"   [WARNING] No es lunes - podria haber problemas con freq='W-MON'")

# Verificar si hay gaps en las fechas
print(f"\n8. VERIFICACIÓN DE GAPS EN FECHAS:")
for series_id in df_final['unique_id'].unique():
    series_data = df_final[df_final['unique_id'] == series_id].sort_values('ds')
    dates = series_data['ds'].tolist()
    expected_weeks = (dates[-1] - dates[0]).days / 7
    actual_weeks = len(dates)
    gaps = expected_weeks - actual_weeks + 1
    print(f"   Serie '{series_id}': {actual_weeks} registros, {gaps:.0f} semanas esperadas, {gaps:.0f} gaps")

print("\n" + "=" * 60)
print("POSIBLES PROBLEMAS IDENTIFICADOS:")
print("=" * 60)

# Problema 1: Muchos ceros
total_zeros = len(df_final[df_final['y'] == 0])
if total_zeros > len(df_final) * 0.3:
    print(f"[PROBLEMA 1] Muchos valores en 0 ({total_zeros}, {total_zeros/len(df_final)*100:.1f}%)")
    print("   Esto puede causar problemas en algunos modelos de forecasting")
else:
    print(f"[OK] Valores en 0: {total_zeros} ({total_zeros/len(df_final)*100:.1f}%) - Aceptable")

# Problema 2: Datos insuficientes después del split
for series_id in df_final['unique_id'].unique():
    train_series = Y_train[Y_train['unique_id'] == series_id]
    if len(train_series) < 20:
        print(f"[PROBLEMA 2] Serie '{series_id}' tiene pocos datos de entrenamiento ({len(train_series)} registros)")
        print("   Se recomiendan al menos 20-30 semanas para entrenar modelos")
    else:
        print(f"[OK] Serie '{series_id}': {len(train_series)} registros de entrenamiento - Suficiente")

# Problema 3: Test vacío
for series_id in df_final['unique_id'].unique():
    test_series = Y_test_real[Y_test_real['unique_id'] == series_id]
    if len(test_series) == 0:
        print(f"[PROBLEMA 3] Serie '{series_id}' no tiene datos de test despues del split")
        print("   Reduce test_weeks o agrega mas datos historicos")
    else:
        print(f"[OK] Serie '{series_id}': {len(test_series)} registros de test")

print("\n" + "=" * 60)

