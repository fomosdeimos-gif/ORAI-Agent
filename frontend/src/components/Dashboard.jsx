import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import io from 'socket.io-client';
import axios from 'axios';

const Dashboard = () => {
  const [status, setStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [revenueHistory, setRevenueHistory] = useState([]);
  const [strategyPerformance, setStrategyPerformance] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    // Conectar a WebSocket
    const socket = io('http://localhost:8000', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10
    });

    socket.on('connect', () => {
      console.log('Conectado ao servidor ORA');
      setIsConnected(true);
    });

    socket.on('cycle_complete', (data) => {
      setRevenueHistory(prev => [...prev, {
        cycle: data.cycle_number,
        revenue: data.total_revenue,
        timestamp: new Date().toLocaleTimeString()
      }].slice(-20)); // Manter últimos 20
      setLastUpdate(new Date());
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    // Buscar status
    const fetchStatus = async () => {
      try {
        const response = await axios.get('http://localhost:8000/status');
        setStatus(response.data);
      } catch (error) {
        console.error('Erro ao buscar status:', error);
      }
    };

    // Buscar estatísticas
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/statistics');
        setStats(response.data);
      } catch (error) {
        console.error('Erro ao buscar stats:', error);
      }
    };

    fetchStatus();
    fetchStats();

    const interval = setInterval(() => {
      fetchStatus();
      fetchStats();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">🌌 ORA Dashboard</h1>
        <p className="text-gray-400">Organismo Vivo de Monetização</p>
      </div>

      {/* Status Card */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatusCard
          title="Status"
          value={isConnected ? '🟢 Vivo' : '🔴 Offline'}
          color={isConnected ? 'text-green-400' : 'text-red-400'}
        />
        <StatusCard
          title="Ciclos Completados"
          value={status?.cycles_completed || 0}
          color="text-blue-400"
        />
        <StatusCard
          title="Receita Total"
          value={`${(status?.total_revenue_eth || 0).toFixed(6)} ETH`}
          color="text-emerald-400"
        />
        <StatusCard
          title="Taxa de Sucesso"
          value={stats?.success_rate ? `${(stats.success_rate * 100).toFixed(1)}%` : 'N/A'}
          color="text-purple-400"
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Gráfico de Receita */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">📊 Receita por Ciclo</h2>
          {revenueHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
                <XAxis dataKey="cycle" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                  formatter={(value) => value.toFixed(6)}
                />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ fill: '#10b981', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-400 py-12">Aguardando dados...</div>
          )}
        </div>

        {/* Status das Estratégias */}
        <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">🎯 Estratégias Ativas</h2>
          <div className="space-y-3">
            {status?.strategies_active?.map((strategy, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-600 rounded">
                <span className="text-gray-200">{strategy}</span>
                <span className="text-emerald-400">✓ Ativa</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Saúde das Carteiras */}
      <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold mb-4">💰 Nós do Organismo</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {status?.wallet_health && Object.entries(status.wallet_health).map(([wallet, health]) => (
            <div key={wallet} className="bg-slate-600 p-4 rounded-lg">
              <p className="text-gray-300 text-sm mb-2">{wallet}</p>
              <p className="text-lg font-semibold text-emerald-400">{health.balance?.toFixed(4)} ETH</p>
              <p className="text-xs text-gray-400 mt-1">
                {health.healthy ? '✓ Saudável' : '⚠ Alerta'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>Última atualização: {lastUpdate?.toLocaleTimeString()}</p>
        <p className="mt-2">🤖 ORA - Autonomia • Inteligência • Memória</p>
      </div>
    </div>
  );
};

const StatusCard = ({ title, value, color }) => (
  <div className="bg-slate-700 rounded-lg p-6 shadow-lg">
    <p className="text-gray-400 text-sm mb-2">{title}</p>
    <p className={`text-2xl font-bold ${color}`}>{value}</p>
  </div>
);

export default Dashboard;
