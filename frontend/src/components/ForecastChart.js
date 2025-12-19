import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import './ForecastChart.css';

const ForecastChart = ({ data, cutoffDate, selectedSeries }) => {
  // Preparar datos para el gráfico
  const chartData = useMemo(() => {
    if (!data || !data.train || !data.predictions) return [];

    // Combinar train, test_real y predictions
    const trainData = data.train
      .filter((d) => d.unique_id === selectedSeries)
      .map((d) => ({
        date: new Date(d.ds).toISOString().split('T')[0],
        timestamp: new Date(d.ds).getTime(),
        type: 'train',
        value: d.y,
        unique_id: d.unique_id,
      }));

    const testData = data.test_real
      .filter((d) => d.unique_id === selectedSeries)
      .map((d) => ({
        date: new Date(d.ds).toISOString().split('T')[0],
        timestamp: new Date(d.ds).getTime(),
        type: 'test',
        value: d.y,
        unique_id: d.unique_id,
      }));

    // Obtener predicciones de todos los modelos
    const predictions = data.predictions.filter((d) => d.unique_id === selectedSeries);
    const futurePredictions = data.future?.filter((d) => d.unique_id === selectedSeries) || [];

    // Identificar columnas de modelos (excluyendo metadatos)
    const modelCols = predictions.length > 0
      ? Object.keys(predictions[0]).filter(
          (k) => !['unique_id', 'ds', 'y', 'index'].includes(k)
        )
      : [];

    // Combinar todos los datos por fecha
    const dateMap = new Map();

    // Agregar datos de entrenamiento
    trainData.forEach((d) => {
      if (!dateMap.has(d.date)) {
        dateMap.set(d.date, { date: d.date, timestamp: d.timestamp });
      }
      dateMap.get(d.date).train = d.value;
    });

    // Agregar datos de test
    testData.forEach((d) => {
      if (!dateMap.has(d.date)) {
        dateMap.set(d.date, { date: d.date, timestamp: d.timestamp });
      }
      dateMap.get(d.date).test = d.value;
    });

    // Agregar predicciones de validación
    predictions.forEach((pred) => {
      const date = new Date(pred.ds).toISOString().split('T')[0];
      if (!dateMap.has(date)) {
        dateMap.set(date, { date, timestamp: new Date(pred.ds).getTime() });
      }
      modelCols.forEach((model) => {
        dateMap.get(date)[`${model}_val`] = pred[model];
      });
    });

    // Agregar predicciones futuras
    futurePredictions.forEach((pred) => {
      const date = new Date(pred.ds).toISOString().split('T')[0];
      if (!dateMap.has(date)) {
        dateMap.set(date, { date, timestamp: new Date(pred.ds).getTime() });
      }
      modelCols.forEach((model) => {
        dateMap.get(date)[`${model}_future`] = pred[model];
      });
    });

    // Convertir a array y ordenar
    return Array.from(dateMap.values()).sort((a, b) => a.timestamp - b.timestamp);
  }, [data, selectedSeries]);

  // Obtener métricas para la serie seleccionada
  const metrics = useMemo(() => {
    if (!data || !data.metrics) return [];
    return data.metrics.filter((m) => m.series_id === selectedSeries);
  }, [data, selectedSeries]);

  // Colores para los modelos
  const modelColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52BE80',
  ];

  // Identificar modelos disponibles
  const modelCols = useMemo(() => {
    if (!data || !data.predictions || data.predictions.length === 0) return [];
    const firstPred = data.predictions.find((p) => p.unique_id === selectedSeries);
    if (!firstPred) return [];
    return Object.keys(firstPred).filter(
      (k) => !['unique_id', 'ds', 'y', 'index'].includes(k)
    );
  }, [data, selectedSeries]);

  if (chartData.length === 0) {
    return (
      <div className="chart-container">
        <div className="chart-placeholder">
          <p>📊 Carga datos y genera predicciones para ver el gráfico</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3>📈 Predicciones: {selectedSeries}</h3>
        {metrics.length > 0 && (
          <div className="metrics-summary">
            Mejor modelo: {metrics.sort((a, b) => b.accuracy - a.accuracy)[0]?.model} (
            {metrics.sort((a, b) => b.accuracy - a.accuracy)[0]?.accuracy.toFixed(1)}%)
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={500}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)' }}
            labelStyle={{ fontWeight: 'bold' }}
          />
          <Legend />

          {/* Línea de corte Train/Test */}
          {cutoffDate && (
            <ReferenceLine
              x={new Date(cutoffDate).toISOString().split('T')[0]}
              stroke="#4CAF50"
              strokeDasharray="5 5"
              label={{ value: 'Corte Train/Test', position: 'top' }}
            />
          )}

          {/* Datos de entrenamiento */}
          <Line
            type="monotone"
            dataKey="train"
            stroke="#2196F3"
            strokeWidth={2}
            dot={false}
            name="Historia (Train)"
            connectNulls
          />

          {/* Datos de test real */}
          <Line
            type="monotone"
            dataKey="test"
            stroke="#000000"
            strokeWidth={3}
            dot={false}
            name="Test Real (Target)"
            connectNulls
          />

          {/* Predicciones de validación (líneas punteadas) */}
          {modelCols.map((model, idx) => {
            const color = modelColors[idx % modelColors.length];
            return (
              <Line
                key={`${model}_val`}
                type="monotone"
                dataKey={`${model}_val`}
                stroke={color}
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name={`${model} (Validación)`}
                connectNulls
              />
            );
          })}

          {/* Predicciones futuras (líneas punteadas más gruesas) */}
          {modelCols.map((model, idx) => {
            const color = modelColors[idx % modelColors.length];
            return (
              <Line
                key={`${model}_future`}
                type="monotone"
                dataKey={`${model}_future`}
                stroke={color}
                strokeWidth={2.5}
                strokeDasharray="8 4"
                dot={{ r: 3 }}
                name={`${model} (Futuro)`}
                connectNulls
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>

      {/* Tabla de métricas */}
      {metrics.length > 0 && (
        <div className="metrics-table">
          <h4>📊 Métricas por Modelo</h4>
          <table>
            <thead>
              <tr>
                <th>Modelo</th>
                <th>Accuracy (%)</th>
                <th>MAE</th>
                <th>Decisión</th>
              </tr>
            </thead>
            <tbody>
              {metrics
                .sort((a, b) => b.accuracy - a.accuracy)
                .map((metric, idx) => (
                  <tr key={idx}>
                    <td>{metric.model}</td>
                    <td>{metric.accuracy.toFixed(2)}</td>
                    <td>{metric.mae.toFixed(2)}</td>
                    <td>
                      <span
                        className={`decision ${
                          metric.decision === 'PREDECIR' ? 'predict' : 'no-predict'
                        }`}
                      >
                        {metric.decision}
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ForecastChart;

