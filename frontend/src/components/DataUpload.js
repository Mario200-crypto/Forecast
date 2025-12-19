import React, { useState } from 'react';
import './DataUpload.css';
import api from '../services/api';

const DataUpload = ({ onDataLoaded, onSeriesSelected }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [seriesList, setSeriesList] = useState([]);
  const [selectedSeries, setSelectedSeries] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('❌ Por favor selecciona un archivo');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const result = await api.uploadData(file);
      setMessage(`✅ ${result.message}. ${result.series_count} series cargadas.`);
      setSeriesList(result.series_list);
      
      if (result.series_list.length > 0) {
        setSelectedSeries(result.series_list[0]);
        if (onSeriesSelected) onSeriesSelected(result.series_list[0]);
      }
      
      if (onDataLoaded) onDataLoaded(result);
    } catch (error) {
      setMessage(`❌ Error: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSeriesChange = (e) => {
    const series = e.target.value;
    setSelectedSeries(series);
    if (onSeriesSelected) onSeriesSelected(series);
  };

  return (
    <div className="data-upload">
      <h2>📁 Cargar Datos</h2>
      
      <div className="upload-section">
        <div className="file-input-wrapper">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            id="file-input"
            className="file-input"
          />
          <label htmlFor="file-input" className="file-label">
            {file ? `📄 ${file.name}` : '📁 Seleccionar archivo CSV'}
          </label>
        </div>
        
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          className="btn-upload"
        >
          {loading ? '⏳ Cargando...' : '⬆️ Subir y Procesar'}
        </button>
      </div>

      {message && <div className="message">{message}</div>}

      {seriesList.length > 0 && (
        <div className="series-selector">
          <label htmlFor="series-select">Seleccionar Serie:</label>
          <select
            id="series-select"
            value={selectedSeries}
            onChange={handleSeriesChange}
            className="series-select"
          >
            {seriesList.map((series) => (
              <option key={series} value={series}>
                {series}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};

export default DataUpload;

