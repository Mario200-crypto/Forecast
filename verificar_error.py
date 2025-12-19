"""
Script para verificar qué está pasando con el error
"""
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("DIAGNÓSTICO DEL ERROR")
print("=" * 60)

# 1. Verificar que el backend esté corriendo
print("\n1. Verificando conexión con backend...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend está corriendo")
    else:
        print(f"   ❌ Backend responde con código: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ No se puede conectar al backend: {str(e)}")
    print("   Asegúrate de que el backend esté corriendo en http://localhost:8000")
    exit(1)

# 2. Verificar estado del servicio
print("\n2. Verificando estado del servicio...")
try:
    response = requests.get(f"{API_URL}/api/forecast/debug/status", timeout=5)
    if response.status_code == 200:
        status = response.json()
        print(f"   Datos cargados: {status.get('data_loaded', False)}")
        print(f"   Cantidad de datos: {status.get('data_count', 0)}")
        print(f"   Series: {status.get('series_count', 0)}")
        print(f"   Modelos entrenados: {status.get('models_trained', False)}")
        
        if not status.get('data_loaded', False):
            print("\n   ⚠️  PROBLEMA: No hay datos cargados")
            print("   Necesitas subir un CSV primero usando /api/forecast/upload")
    else:
        print(f"   ❌ Error al obtener estado: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# 3. Intentar generar predicciones y capturar el error
print("\n3. Intentando generar predicciones...")
try:
    response = requests.post(
        f"{API_URL}/api/forecast/predict",
        json={"series_id": None},
        timeout=30
    )
    
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Predicciones generadas exitosamente")
        data = response.json()
        print(f"   Series: {data.get('series_list', [])}")
        print(f"   Métricas: {len(data.get('metrics', []))} resultados")
    else:
        print(f"   ❌ Error {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Mensaje de error: {error_data.get('detail', 'Sin detalle')}")
        except:
            print(f"   Respuesta: {response.text[:500]}")
            
except requests.exceptions.Timeout:
    print("   ⏱️  Timeout - El proceso está tomando mucho tiempo")
except Exception as e:
    print(f"   ❌ Error de conexión: {str(e)}")

print("\n" + "=" * 60)

