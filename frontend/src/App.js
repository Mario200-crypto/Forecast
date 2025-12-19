import React, { useState, useEffect } from 'react';
import './App.css';
import ConfigPanel from './components/ConfigPanel';
import DataUpload from './components/DataUpload';
import ForecastChart from './components/ForecastChart';
import api from './services/api';

function App() {
  const [config, setConfig] = useState(null);
  const [selectedSeries, setSelectedSeries] = useState('');
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConfigChange = (newConfig) => {
    setConfig(newConfig);
  };

  const handleSeriesSelected = (seriesId) => {
    setSelectedSeries(seriesId);
  };

  const handleGenerateForecast = async () => {
    if (!selectedSeries) {
      setError('Por favor selecciona una serie primero');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await api.generateForecast(selectedSeries);
      setForecastData(result);
    } catch (err) {
      setError(`Error al generar predicciones: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Dashboard de Predicciones - StatsForecast</h1>
        <p>Sistema interactivo para tunning de parámetros y visualización de predicciones</p>
      </header>

      <main className="App-main">
        <div className="container">
          {/* Panel de carga de datos */}
          <DataUpload
            onDataLoaded={(data) => {
              if (data.series_list && data.series_list.length > 0) {
                setSelectedSeries(data.series_list[0]);
              }
            }}
            onSeriesSelected={handleSeriesSelected}
          />

          {/* Panel de configuración */}
          <ConfigPanel onConfigChange={handleConfigChange} />

          {/* Botón para generar predicciones */}
          {selectedSeries && (
            <div className="forecast-actions">
              <button
                onClick={handleGenerateForecast}
                disabled={loading}
                className="btn-generate"
              >
                {loading ? '⏳ Generando predicciones...' : '🚀 Generar Predicciones'}
              </button>
              {error && <div className="error-message">{error}</div>}
            </div>
          )}

          {/* Gráfica de predicciones */}
          {forecastData && selectedSeries && (
            <ForecastChart
              data={forecastData}
              cutoffDate={forecastData.cutoff_date}
              selectedSeries={selectedSeries}
            />
          )}

          {/* Información adicional */}
          {forecastData && (
            <div className="info-panel">
              <h3>ℹ️ Información</h3>
              <ul>
                <li>
                  <strong>Fecha de corte:</strong>{' '}
                  {new Date(forecastData.cutoff_date).toLocaleDateString()}
                </li>
                <li>
                  <strong>Series procesadas:</strong> {forecastData.series_list.length}
                </li>
                <li>
                  <strong>Modelos evaluados:</strong>{' '}
                  {forecastData.metrics
                    ? new Set(forecastData.metrics.map((m) => m.model)).size
                    : 0}
                </li>
              </ul>
            </div>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>Forecast Dashboard v2.0 - Powered by StatsForecast (Nixtla)</p>
      </footer>
    </div>
  );
}

export default App;

