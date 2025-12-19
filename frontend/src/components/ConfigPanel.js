import React, { useState, useEffect } from 'react';
import './ConfigPanel.css';
import api from '../services/api';

const ConfigPanel = ({ onConfigChange }) => {
  const [config, setConfig] = useState({
    test_weeks: 12,
    horizon: 12,
    zero_threshold: 0.50,
    cv_threshold: 10,
    min_accuracy: 60.0,
    upper_quantile: 0.80,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await api.getConfig();
      setConfig(data);
      if (onConfigChange) onConfigChange(data);
    } catch (error) {
      console.error('Error al cargar configuración:', error);
    }
  };

  const handleChange = (key, value) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage('');
    try {
      await api.updateConfig(config);
      setMessage('✅ Configuración guardada exitosamente');
      if (onConfigChange) onConfigChange(config);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('❌ Error al guardar configuración');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (window.confirm('¿Restaurar configuración a valores por defecto?')) {
      setLoading(true);
      try {
        const data = await api.resetConfig();
        setConfig(data.config);
        setMessage('✅ Configuración restaurada');
        if (onConfigChange) onConfigChange(data.config);
        setTimeout(() => setMessage(''), 3000);
      } catch (error) {
        setMessage('❌ Error al restaurar configuración');
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="config-panel">
      <h2>⚙️ Configuración de Parámetros</h2>
      
      <div className="config-grid">
        <div className="config-item">
          <label>
            Test Weeks (Semanas de validación)
            <span className="tooltip">ℹ️ Semanas usadas para validar el modelo</span>
          </label>
          <input
            type="number"
            min="1"
            max="52"
            value={config.test_weeks}
            onChange={(e) => handleChange('test_weeks', parseInt(e.target.value))}
          />
        </div>

        <div className="config-item">
          <label>
            Horizon (Horizonte de predicción)
            <span className="tooltip">ℹ️ Semanas a predecir a futuro</span>
          </label>
          <input
            type="number"
            min="1"
            max="52"
            value={config.horizon}
            onChange={(e) => handleChange('horizon', parseInt(e.target.value))}
          />
        </div>

        <div className="config-item">
          <label>
            Zero Threshold
            <span className="tooltip">ℹ️ Filtro de ceros (opcional)</span>
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={config.zero_threshold}
            onChange={(e) => handleChange('zero_threshold', parseFloat(e.target.value))}
          />
        </div>

        <div className="config-item">
          <label>
            CV Threshold (Coeficiente de variación)
            <span className="tooltip">ℹ️ Filtro de coeficiente de variación</span>
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={config.cv_threshold}
            onChange={(e) => handleChange('cv_threshold', parseInt(e.target.value))}
          />
        </div>

        <div className="config-item">
          <label>
            Min Accuracy (%)
            <span className="tooltip">ℹ️ Umbral mínimo de precisión para considerar útil el modelo</span>
          </label>
          <input
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={config.min_accuracy}
            onChange={(e) => handleChange('min_accuracy', parseFloat(e.target.value))}
          />
        </div>

        <div className="config-item">
          <label>
            Upper Quantile (Winsorización)
            <span className="tooltip">ℹ️ Límite superior para eliminar outliers (0-1)</span>
          </label>
          <input
            type="number"
            min="0.5"
            max="1"
            step="0.01"
            value={config.upper_quantile}
            onChange={(e) => handleChange('upper_quantile', parseFloat(e.target.value))}
          />
        </div>
      </div>

      <div className="config-actions">
        <button onClick={handleSave} disabled={loading} className="btn-primary">
          {loading ? 'Guardando...' : '💾 Guardar Configuración'}
        </button>
        <button onClick={handleReset} disabled={loading} className="btn-secondary">
          🔄 Restaurar Valores por Defecto
        </button>
      </div>

      {message && <div className="message">{message}</div>}
    </div>
  );
};

export default ConfigPanel;

