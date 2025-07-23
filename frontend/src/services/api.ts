import axios from 'axios';

const api = axios.create({
  baseURL: '/',
});

export const getPrecoAtual = async () => {
  // Pega o último preço do BTC da Binance
  // Ideal: endpoint dedicado no backend. Por enquanto, retorna mock.
  return 250000; // valor mock em reais
};

export const getPrevisao = async () => {
  const resp = await api.post('/api/predict', {
    modelo: 'randomforest',
    tipo: 'classificacao',
  });
  return resp.data.previsao;
};

export const getSentimento = async () => {
  // O sentimento já é integrado ao modelo, mas pode ser exposto em endpoint futuro
  // Por enquanto, retorna mock
  return 'positivo';
};

export const getHashrate = async () => {
  // O hashrate já é integrado ao modelo, mas pode ser exposto em endpoint futuro
  // Por enquanto, retorna mock
  return '500 EH/s';
};

export const getMetricas = async () => {
  const resp = await api.get('/api/model_info');
  return resp.data.info;
};

export const treinarModelo = async () => {
  const resp = await api.post('/api/train', {
    modelo: 'randomforest',
    tipo: 'classificacao',
  });
  return resp.data.metricas;
};

export const atualizarDados = async () => {
  const resp = await api.post('/api/update_data');
  return resp.data;
}; 