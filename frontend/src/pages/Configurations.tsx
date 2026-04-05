import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Settings, Play, ChevronRight, ArrowLeftRight, Check, X, Loader2 } from 'lucide-react';
import { listConfigurations, getConfiguration } from '../services/api';

interface FieldMapping {
  source_field: string;
  target_field: string;
  transformation?: string;
  is_required: boolean;
  validation_rules: string[];
}

interface AdapterConfig {
  adapter_id: string;
  adapter_name: string;
  version: string;
  service_type: string;
  field_mappings: FieldMapping[];
  mapping_confidence: number;
}

interface Configuration {
  config_id: string;
  config_name: string;
  version: string;
  status: string;
  adapters: AdapterConfig[];
  validation: {
    is_valid: boolean;
    validation_score: number;
    issues: Array<{ severity: string; message: string }>;
    recommendations: string[];
  };
  created_at: string;
}

export default function Configurations() {
  const { id } = useParams();
  const [configurations, setConfigurations] = useState<any[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<Configuration | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'mappings' | 'json' | 'validation'>('mappings');

  useEffect(() => {
    if (id) {
      loadConfiguration(id);
    } else {
      loadConfigurations();
    }
  }, [id]);

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

  const loadConfiguration = async (configId: string) => {
    try {
      const data = await getConfiguration(configId);
      setSelectedConfig(data);
    } catch (error) {
      console.error('Failed to load configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
      </div>
    );
  }

  // Detail View
  if (selectedConfig) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
              <Link to="/configurations" className="hover:text-white">Configurations</Link>
              <ChevronRight className="w-4 h-4" />
              <span>{selectedConfig.config_name}</span>
            </div>
            <h1 className="text-2xl font-bold text-white">{selectedConfig.config_name}</h1>
            <div className="flex items-center gap-3 mt-2">
              <span className="status-badge status-info">v{selectedConfig.version}</span>
              <span className={`status-badge ${selectedConfig.status === 'validated' ? 'status-success' :
                selectedConfig.status === 'draft' ? 'status-warning' : 'status-info'
                }`}>
                {selectedConfig.status}
              </span>
            </div>
          </div>
          <Link
            to={`/simulation/${selectedConfig.config_id}`}
            className="btn-primary flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            Run Simulation
          </Link>
        </div>

        {/* Validation Summary */}
        {selectedConfig.validation && (
          <div className={`glass-card p-4 flex items-center justify-between ${selectedConfig.validation.is_valid ? 'border-green-500/30' : 'border-yellow-500/30'
            }`}>
            <div className="flex items-center gap-3">
              {selectedConfig.validation.is_valid ? (
                <Check className="w-5 h-5 text-green-400" />
              ) : (
                <X className="w-5 h-5 text-yellow-400" />
              )}
              <span className="text-white">
                Validation: {Math.round(selectedConfig.validation.validation_score * 100)}% score
              </span>
            </div>
            {selectedConfig.validation.issues.length > 0 && (
              <span className="text-yellow-400 text-sm">
                {selectedConfig.validation.issues.length} issues found
              </span>
            )}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 border-b border-slate-700">
          {(['mappings', 'json', 'validation'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium transition-colors ${activeTab === tab
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-white'
                }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'mappings' && (
          <div className="space-y-6">
            {selectedConfig.adapters.map((adapter, idx) => (
              <div key={idx} className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-white font-medium">{adapter.adapter_name}</h3>
                    <p className="text-slate-400 text-sm">
                      {adapter.adapter_id} • v{adapter.version}
                    </p>
                  </div>
                  <span className="status-badge status-info">{adapter.service_type}</span>
                </div>

                {/* Mapping Confidence */}
                <div className="flex items-center gap-3 mb-4 p-3 bg-slate-800/50 rounded-lg">
                  <span className="text-slate-400 text-sm">Mapping Confidence:</span>
                  <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-green-500"
                      style={{ width: `${adapter.mapping_confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-white text-sm font-medium">
                    {Math.round(adapter.mapping_confidence * 100)}%
                  </span>
                </div>

                {/* Field Mappings Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-slate-400 border-b border-slate-700">
                        <th className="text-left py-2">Source Field</th>
                        <th className="text-center py-2">→</th>
                        <th className="text-left py-2">Target Field</th>
                        <th className="text-left py-2">Transform</th>
                        <th className="text-left py-2">Required</th>
                      </tr>
                    </thead>
                    <tbody>
                      {adapter.field_mappings.map((mapping, i) => (
                        <tr key={i} className="border-b border-slate-800">
                          <td className="py-2 text-white font-mono">{mapping.source_field}</td>
                          <td className="py-2 text-center">
                            <ArrowLeftRight className="w-4 h-4 text-blue-400 inline" />
                          </td>
                          <td className="py-2 text-green-400 font-mono">{mapping.target_field}</td>
                          <td className="py-2 text-slate-400 font-mono text-xs">
                            {mapping.transformation || '-'}
                          </td>
                          <td className="py-2">
                            {mapping.is_required ? (
                              <span className="status-badge status-error">Required</span>
                            ) : (
                              <span className="status-badge status-info">Optional</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'json' && (
          <div className="glass-card p-6">
            <pre className="text-sm text-slate-300 overflow-auto max-h-[600px] font-mono">
              {JSON.stringify(selectedConfig, null, 2)}
            </pre>
          </div>
        )}

        {activeTab === 'validation' && selectedConfig.validation && (
          <div className="space-y-4">
            {/* Issues */}
            {selectedConfig.validation.issues.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="text-white font-medium mb-4">Issues</h3>
                <div className="space-y-2">
                  {selectedConfig.validation.issues.map((issue, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded-lg ${issue.severity === 'error' ? 'bg-red-500/10 border border-red-500/30' :
                        issue.severity === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                          'bg-blue-500/10 border border-blue-500/30'
                        }`}
                    >
                      <span className={`text-sm ${issue.severity === 'error' ? 'text-red-400' :
                        issue.severity === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                        }`}>
                        [{issue.severity.toUpperCase()}] {issue.message}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div className="glass-card p-6">
              <h3 className="text-white font-medium mb-4">Recommendations</h3>
              <ul className="space-y-2">
                {selectedConfig.validation.recommendations.map((rec, i) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    );
  }

  // List View
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Configurations</h1>
        <p className="text-slate-400">Generated integration configurations</p>
      </div>

      {configurations.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Settings className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-white font-medium mb-2">No configurations yet</p>
          <p className="text-slate-400 text-sm mb-4">Generate a configuration from extracted requirements</p>
          <Link to="/requirements" className="btn-primary inline-block">
            View Requirements
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {configurations.map((config) => (
            <Link
              key={config.config_id}
              to={`/configurations/${config.config_id}`}
              className="glass-card p-4 hover:border-blue-500/50 transition-all"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-medium">{config.config_name}</h3>
                  <p className="text-slate-400 text-sm">
                    v{config.version} • {config.adapters_count} adapters
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`status-badge ${config.status === 'validated' ? 'status-success' :
                    config.status === 'draft' ? 'status-warning' : 'status-info'
                    }`}>
                    {config.status}
                  </span>
                  <ChevronRight className="w-5 h-5 text-slate-400" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
