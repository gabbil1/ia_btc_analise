import React from 'react';

interface CardProps {
  label: string;
  value: string | number;
  loading?: boolean;
  color?: string;
}

const Card: React.FC<CardProps> = ({ label, value, loading, color }) => (
  <div className={`bg-gray-800 rounded-lg p-4 shadow flex flex-col items-center ${color || ''}`}>
    <span className="text-sm text-gray-400 mb-1">{label}</span>
    {loading ? (
      <div className="animate-pulse h-6 w-16 bg-gray-700 rounded" />
    ) : (
      <span className="text-2xl font-bold">{value}</span>
    )}
  </div>
);

interface DashboardCardsProps {
  preco: string | number;
  previsao: string | number;
  sentimento: string | number;
  hashrate: string | number;
  loading?: boolean;
}

const DashboardCards: React.FC<DashboardCardsProps> = ({ preco, previsao, sentimento, hashrate, loading }) => (
  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <Card label="Preço atual" value={preco} loading={loading} color="text-yellow-400" />
    <Card label="Previsão do modelo" value={previsao} loading={loading} color="text-green-400" />
    <Card label="Sentimento do mercado" value={sentimento} loading={loading} color="text-blue-400" />
    <Card label="Hashrate" value={hashrate} loading={loading} color="text-purple-400" />
  </div>
);

export default DashboardCards; 