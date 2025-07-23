import React from 'react';

interface LogsPanelProps {
  logs: string[];
}

const LogsPanel: React.FC<LogsPanelProps> = ({ logs }) => (
  <div className="h-40 overflow-y-auto text-sm font-mono bg-gray-900 rounded p-2 border border-gray-800">
    {logs.length === 0 ? (
      <span className="text-gray-500">Nenhum log disponível.</span>
    ) : (
      logs.map((log, i) => <div key={i} className="mb-1">{log}</div>)
    )}
  </div>
);

export default LogsPanel; 