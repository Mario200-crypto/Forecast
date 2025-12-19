/**
 * Cliente API para comunicarse con el backend
 */
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  /**
   * Obtiene la configuración actual
   */
  async getConfig() {
    const response = await fetch(`${API_URL}/api/config/`);
    if (!response.ok) throw new Error('Error al obtener configuración');
    return response.json();
  }

  /**
   * Actualiza la configuración
   */
  async updateConfig(config) {
    const response = await fetch(`${API_URL}/api/config/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Error al actualizar configuración');
    return response.json();
  }

  /**
   * Restaura la configuración a valores por defecto
   */
  async resetConfig() {
    const response = await fetch(`${API_URL}/api/config/reset`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Error al restaurar configuración');
    return response.json();
  }

  /**
   * Sube un archivo CSV
   */
  async uploadData(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/forecast/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Error al subir archivo');
    return response.json();
  }

  /**
   * Obtiene la lista de series disponibles
   */
  async getSeries() {
    const response = await fetch(`${API_URL}/api/forecast/series`);
    if (!response.ok) throw new Error('Error al obtener series');
    return response.json();
  }

  /**
   * Obtiene datos de una serie específica
   */
  async getSeriesData(seriesId) {
    const response = await fetch(`${API_URL}/api/forecast/series/${seriesId}`);
    if (!response.ok) throw new Error('Error al obtener datos de la serie');
    return response.json();
  }

  /**
   * Genera predicciones
   */
  async generateForecast(seriesId = null) {
    const response = await fetch(`${API_URL}/api/forecast/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ series_id: seriesId }),
    });
    
    if (!response.ok) {
      // Intentar extraer el mensaje de error del backend
      let errorMessage = 'Error al generar predicciones';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        // Si no se puede parsear el JSON, usar el status text
        errorMessage = response.statusText || 'Error al generar predicciones';
      }
      throw new Error(errorMessage);
    }
    
    return response.json();
  }
}

export default new ApiService();

