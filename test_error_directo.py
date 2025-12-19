"""
Script para probar directamente el endpoint y ver el error completo
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

print("=" * 60)
print("PRUEBA DIRECTA DEL ENDPOINT /api/forecast/predict")
print("=" * 60)

try:
    print("\nEnviando petición POST a /api/forecast/predict...")
    response = requests.post(
        f"{API_URL}/api/forecast/predict",
        json={"series_id": None},
        timeout=60
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("\n✅ ÉXITO - Predicciones generadas")
        data = response.json()
        print(f"Series: {data.get('series_list', [])}")
        print(f"Métricas: {len(data.get('metrics', []))} resultados")
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print("\nRespuesta completa:")
        print("-" * 60)
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
            if 'detail' in error_data:
                print(f"\n🔴 MENSAJE DE ERROR:")
                print(error_data['detail'])
        except:
            print(response.text)
        print("-" * 60)
        
except requests.exceptions.Timeout:
    print("\n⏱️  TIMEOUT - El proceso está tomando más de 60 segundos")
    print("Esto puede indicar que el entrenamiento está tardando mucho")
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR DE CONEXIÓN")
    print("El backend no está corriendo o no es accesible en http://localhost:8000")
    print("Asegúrate de que docker-compose esté corriendo")
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

