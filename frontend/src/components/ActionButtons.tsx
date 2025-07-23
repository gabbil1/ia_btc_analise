import React from 'react';

interface ActionButtonsProps {
  onTreinar: () => void;
  onAtualizar: () => void;
  loadingTreinar: boolean;
  loadingAtualizar: boolean;
  status?: string;
  erro?: string;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
  onTreinar,
  onAtualizar,
  loadingTreinar,
  loadingAtualizar,
  status,
  erro,
}) => (
  <div className="flex flex-wrap gap-4 mb-6 items-center">
    <button
      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded disabled:opacity-50"
      onClick={onTreinar}
      disabled={loadingTreinar || loadingAtualizar}
    >
      {loadingTreinar ? 'Treinando...' : 'Treinar modelo'}
    </button>
    <button
      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50"
      onClick={onAtualizar}
      disabled={loadingAtualizar || loadingTreinar}
    >
      {loadingAtualizar ? 'Atualizando...' : 'Atualizar dados'}
    </button>
    {status && <span className="text-green-400 ml-4">{status}</span>}
    {erro && <span className="text-red-400 ml-4">{erro}</span>}
  </div>
);

export default ActionButtons; 