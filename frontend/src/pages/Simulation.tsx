import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Play, Check, X, AlertCircle, Loader2 } from 'lucide-react';
import { runSimulation, listConfigurations } from '../services/api';

interface SimulationResult {
  scenario_id: string;
  scenario_name: string;
  adapter: string;
  expected_status: number;
  actual_status: number;
  passed: boolean;
  actual_response: any;
}

interface Simulation {
  simulation_id: string;
  config_id: string;
  status: string;
  summary: {
    scenarios_run: number;
    passed: number;
    failed: number;
    pass_rate: number;
  };
  execution_time_ms: number;
  results: SimulationResult[];
  recommendations: string[];
}

export default function Simulation() {
  const { configId } = useParams();
  const [configurations, setConfigurations] = useState<any[]>([]);
  const [selectedConfigId, setSelectedConfigId] = useState<string>(configId || '');
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadConfigurations();
  }, []);

  useEffect(() => {
    if (configId) {
      setSelectedConfigId(configId);
    }
  }, [configId]);

  const loadConfigurations = async () => {
    try {
      const data = await listConfigurations();
      setConfigurations(data.configurations || []);
    } catch (error) {
      console.error('Failed to load configurations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    if (!selectedConfigId) return;
    setRunning(true);
    setSimulation(null);

    try {
      const result = await runSimulation(selectedConfigId);
      setSimulation(result);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Simulation Engine</h1>
        <p className="text-slate-400">
          Test your integration configuration with mock APIs
        </p>
      </div>

      {/* Config Selection */}
      <div className="glass-card p-6">
        <h2 className="text-white font-medium mb-4">Select Configuration</h2>
        <div className="flex gap-4">
          <select
            value={selectedConfigId}
            onChange={(e) => setSelectedConfigId(e.target.value)}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="">Select a configuration...</option>
            {configurations.map((config) => (
              <option key={config.config_id} value={config.config_id}>
                {config.config_name} (v{config.version})
              </option>
            ))}
          </select>
          <button
            onClick={handleRunSimulation}
            disabled={!selectedConfigId || running}
            className="btn-primary flex items-center gap-2"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Simulation
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {simulation && (
        <>
          {/* Summary */}
          <div className="glass-card p-6">
            <h2 className="text-white font-medium mb-4">Results Summary</h2>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-white">{simulation.summary.scenarios_run}</p>
                <p className="text-slate-400 text-sm">Total Tests</p>
              </div>
              <div className="bg-green-500/10 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-green-400">{simulation.summary.passed}</p>
                <p className="text-slate-400 text-sm">Passed</p>
              </div>
              <div className="bg-red-500/10 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-red-400">{simulation.summary.failed}</p>
                <p className="text-slate-400 text-sm">Failed</p>
              </div>
              <div className="bg-blue-500/10 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-blue-400">{simulation.summary.pass_rate}%</p>
                <p className="text-slate-400 text-sm">Pass Rate</p>
              </div>
            </div>
          </div>

          {/* Test Results */}
          <div className="glass-card p-6">
            <h2 className="text-white font-medium mb-4">Test Results</h2>
            <div className="space-y-3">
              {simulation.results.map((result) => (
                <div
                  key={result.scenario_id}
                  className={`p-4 rounded-lg border ${result.passed
                    ? 'bg-green-500/5 border-green-500/30'
                    : 'bg-red-500/5 border-red-500/30'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {result.passed ? (
                        <Check className="w-5 h-5 text-green-400" />
                      ) : (
                        <X className="w-5 h-5 text-red-400" />
                      )}
                      <div>
                        <p className="text-white font-medium">{result.scenario_name}</p>
                        <p className="text-slate-400 text-sm">{result.adapter}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={result.passed ? 'text-green-400' : 'text-red-400'}>
                        {result.actual_status}
                      </p>
                      <p className="text-slate-400 text-xs">
                        Expected: {result.expected_status}
                      </p>
                    </div>
                  </div>

                  {/* Response Details */}
                  <div className="mt-3 p-3 bg-slate-900 rounded font-mono text-xs overflow-auto">
                    <pre className="text-slate-300">
                      {JSON.stringify(result.actual_response, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {simulation.recommendations.length > 0 && (
            <div className="glass-card p-6 bg-gradient-to-r from-blue-900/20 to-purple-900/20">
              <h2 className="text-white font-medium mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-blue-400" />
                Recommendations
              </h2>
              <ul className="space-y-2">
                {simulation.recommendations.map((rec, i) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {!simulation && !running && (
        <div className="glass-card p-12 text-center">
          <Play className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-white font-medium mb-2">Ready to Test</p>
          <p className="text-slate-400 text-sm">
            Select a configuration and run simulation to test with mock APIs
          </p>
        </div>
      )}
    </div>
  );
}
