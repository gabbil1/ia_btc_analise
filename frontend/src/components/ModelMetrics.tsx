import React from 'react';

interface ModelMetricsProps {
  info: {
    modelo: string;
    tipo: string;
    data_treino: string;
    metricas: Record<string, number>;
  } | null;
  loading?: boolean;
}

const ModelMetrics: React.FC<ModelMetricsProps> = ({ info, loading }) => {
  if (loading) {
    return <div className="animate-pulse h-12 w-full bg-gray-700 rounded" />;
  }
  if (!info) {
    return <div className="text-gray-400">Nenhuma métrica disponível.</div>;
  }
  return (
    <div>
      <div className="flex flex-wrap gap-4 mb-2">
        <span className="bg-gray-700 px-3 py-1 rounded text-sm">Modelo: <b>{info.modelo}</b></span>
        <span className="bg-gray-700 px-3 py-1 rounded text-sm">Tipo: <b>{info.tipo}</b></span>
        <span className="bg-gray-700 px-3 py-1 rounded text-sm">Último treino: <b>{new Date(info.data_treino).toLocaleString('pt-BR')}</b></span>
      </div>
      <div className="flex flex-wrap gap-4">
        {Object.entries(info.metricas).map(([k, v]) => (
          <span key={k} className="bg-gray-800 px-3 py-1 rounded text-sm">
            {k}: <b>{v.toFixed(4)}</b>
          </span>
        ))}
      </div>
    </div>
  );
};

export default ModelMetrics; 