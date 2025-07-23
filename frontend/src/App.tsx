import React, { useState, useEffect } from 'react';
import DashboardCards from './components/DashboardCards';
import PriceChart from './components/PriceChart';
import ModelMetrics from './components/ModelMetrics';
import ActionButtons from './components/ActionButtons';
import LogsPanel from './components/LogsPanel';
import { getPrecoAtual, getPrevisao, getSentimento, getHashrate, getMetricas } from './services/api';
import { treinarModelo, atualizarDados } from './services/api';

const App: React.FC = () => {
  const [preco, setPreco] = useState<string | number>('--');
  const [previsao, setPrevisao] = useState<string | number>('--');
  const [sentimento, setSentimento] = useState<string | number>('--');
  const [hashrate, setHashrate] = useState<string | number>('--');
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [metricas, setMetricas] = useState<any>(null);
  const [loadingMetricas, setLoadingMetricas] = useState(true);
  const [loadingTreinar, setLoadingTreinar] = useState(false);
  const [loadingAtualizar, setLoadingAtualizar] = useState(false);
  const [statusAcao, setStatusAcao] = useState<string | undefined>(undefined);
  const [erroAcao, setErroAcao] = useState<string | undefined>(undefined);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setErro(null);
      try {
        // Preço atual (mock: pega do update_data, mas ideal é endpoint dedicado)
        const precoResp = await getPrecoAtual();
        setPreco(`R$ ${precoResp}`);
        // Previsão do modelo
        const prev = await getPrevisao();
        setPrevisao(prev);
        // Sentimento (mock)
        const sent = await getSentimento();
        setSentimento(sent);
        // Hashrate (mock)
        const hash = await getHashrate();
        setHashrate(hash);
      } catch (e) {
        setErro('Erro ao buscar dados do backend');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const fetchMetricas = async () => {
      setLoadingMetricas(true);
      try {
        const info = await getMetricas();
        setMetricas(info);
      } catch {
        setMetricas(null);
      } finally {
        setLoadingMetricas(false);
      }
    };
    fetchMetricas();
  }, []);

  const handleTreinar = async () => {
    setLoadingTreinar(true);
    setStatusAcao(undefined);
    setErroAcao(undefined);
    try {
      await treinarModelo();
      setStatusAcao('Modelo treinado com sucesso!');
      // Atualiza métricas após treino
      const info = await getMetricas();
      setMetricas(info);
    } catch {
      setErroAcao('Erro ao treinar modelo');
    } finally {
      setLoadingTreinar(false);
    }
  };

  const handleAtualizar = async () => {
    setLoadingAtualizar(true);
    setStatusAcao(undefined);
    setErroAcao(undefined);
    try {
      await atualizarDados();
      setStatusAcao('Dados atualizados!');
      // Atualiza cards após atualização
      const precoResp = await getPrecoAtual();
      setPreco(`R$ ${precoResp}`);
    } catch {
      setErroAcao('Erro ao atualizar dados');
    } finally {
      setLoadingAtualizar(false);
    }
  };

  // Dados mock para o gráfico
  const labels = Array.from({ length: 30 }, (_, i) => `Dia ${i + 1}`);
  const prices = labels.map((_, i) => 240000 + i * 500 + Math.random() * 2000);
  const previsoes = prices.map((p, i) => (i > 25 ? p + 2000 : null)).filter((v) => v !== null) as number[];

  const logsMock = [
    '[2024-07-23 10:00] Previsão: compra | Preço: R$ 250.000',
    '[2024-07-23 09:55] Previsão: neutro | Preço: R$ 249.800',
    '[2024-07-23 09:50] Previsão: venda | Preço: R$ 249.600',
    '[2024-07-23 09:45] Previsão: compra | Preço: R$ 249.400',
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans">
      <header className="p-6 border-b border-gray-800 flex items-center justify-between">
        <h1 className="text-2xl font-bold">IA BTC Dashboard</h1>
        <span className="text-sm text-gray-400">Powered by FastAPI + React</span>
      </header>
      <main className="p-6 max-w-6xl mx-auto">
        {erro && <div className="bg-red-700 text-white p-2 mb-4 rounded">{erro}</div>}
        <DashboardCards
          preco={preco}
          previsao={previsao}
          sentimento={sentimento}
          hashrate={hashrate}
          loading={loading}
        />
        <ActionButtons
          onTreinar={handleTreinar}
          onAtualizar={handleAtualizar}
          loadingTreinar={loadingTreinar}
          loadingAtualizar={loadingAtualizar}
          status={statusAcao}
          erro={erroAcao}
        />
        {/* Gráfico */}
        <div className="bg-gray-800 rounded-lg p-4 shadow mb-6">
          <PriceChart labels={labels} prices={prices} previsoes={previsoes} />
        </div>
        {/* Painel de métricas */}
        <div className="bg-gray-800 rounded-lg p-4 shadow mb-6">
          <ModelMetrics info={metricas} loading={loadingMetricas} />
        </div>
        {/* Painel de logs/resultados */}
        <div className="bg-gray-800 rounded-lg p-4 shadow">
          <LogsPanel logs={logsMock} />
        </div>
      </main>
    </div>
  );
};

export default App; 