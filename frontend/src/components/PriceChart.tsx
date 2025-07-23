import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface PriceChartProps {
  labels: string[];
  prices: number[];
  previsoes?: number[];
}

const PriceChart: React.FC<PriceChartProps> = ({ labels, prices, previsoes }) => {
  const data = {
    labels,
    datasets: [
      {
        label: 'Preço BTC',
        data: prices,
        borderColor: '#fbbf24',
        backgroundColor: 'rgba(251,191,36,0.1)',
        tension: 0.2,
      },
      previsoes && {
        label: 'Previsão',
        data: previsoes,
        borderColor: '#34d399',
        backgroundColor: 'rgba(52,211,153,0.1)',
        borderDash: [5, 5],
        tension: 0.2,
      },
    ].filter(Boolean),
  };
  const options = {
    responsive: true,
    plugins: {
      legend: { display: true, labels: { color: '#fff' } },
      title: { display: false },
    },
    scales: {
      x: { ticks: { color: '#fff' } },
      y: { ticks: { color: '#fff' } },
    },
  };
  return <Line data={data} options={options} />;
};

export default PriceChart; 