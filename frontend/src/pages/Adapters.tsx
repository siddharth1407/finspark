import { useState, useEffect } from 'react';
import { Puzzle, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { listAdapters, getAdapter } from '../services/api';

interface Adapter {
  adapter_id: string;
  name: string;
  service_type: string;
  version: string;
  description: string;
  auth_types: string[];
  is_active: boolean;
  endpoints?: Array<{ name: string; method: string; path: string; description: string }>;
  field_schema?: any;
}

export default function Adapters() {
  const [adapters, setAdapters] = useState<Adapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedAdapter, setExpandedAdapter] = useState<string | null>(null);
  const [adapterDetails, setAdapterDetails] = useState<Record<string, Adapter>>({});
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    loadAdapters();
  }, []);

  const loadAdapters = async () => {
    try {
      const data = await listAdapters();
      setAdapters(data.adapters || []);
    } catch (error) {
      console.error('Failed to load adapters:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAdapterDetails = async (adapterId: string) => {
    if (adapterDetails[adapterId]) return;

    try {
      const data = await getAdapter(adapterId);
      setAdapterDetails(prev => ({ ...prev, [adapterId]: data }));
    } catch (error) {
      console.error('Failed to load adapter details:', error);
    }
  };

  const toggleAdapter = (adapterId: string) => {
    if (expandedAdapter === adapterId) {
      setExpandedAdapter(null);
    } else {
      setExpandedAdapter(adapterId);
      loadAdapterDetails(adapterId);
    }
  };

  const serviceTypes = ['all', ...new Set(adapters.map(a => a.service_type))];
  const filteredAdapters = filterType === 'all'
    ? adapters
    : adapters.filter(a => a.service_type === filterType);

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
        <h1 className="text-2xl font-bold text-white mb-2">Integration Adapters</h1>
        <p className="text-slate-400">
          Pre-built adapters for KYC, Payment, GST, and Banking services
        </p>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {serviceTypes.map((type) => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${filterType === type
              ? 'bg-blue-600 text-white'
              : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
          >
            {type === 'all' ? 'All' : type.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Adapters List */}
      <div className="space-y-3">
        {filteredAdapters.map((adapter) => {
          const isExpanded = expandedAdapter === adapter.adapter_id;
          const details = adapterDetails[adapter.adapter_id];

          return (
            <div key={adapter.adapter_id} className="glass-card overflow-hidden">
              {/* Header */}
              <button
                onClick={() => toggleAdapter(adapter.adapter_id)}
                className="w-full p-4 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${adapter.service_type === 'kyc' ? 'bg-purple-500/20 text-purple-400' :
                    adapter.service_type === 'payment' ? 'bg-green-500/20 text-green-400' :
                      adapter.service_type === 'gst' ? 'bg-orange-500/20 text-orange-400' :
                        'bg-blue-500/20 text-blue-400'
                    }`}>
                    <Puzzle className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-white font-medium">{adapter.name}</h3>
                    <p className="text-slate-400 text-sm">{adapter.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="status-badge status-info">{adapter.service_type}</span>
                  <span className="text-slate-400 text-sm">v{adapter.version}</span>
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  )}
                </div>
              </button>

              {/* Details */}
              {isExpanded && details && (
                <div className="border-t border-slate-700 p-4 bg-slate-800/30">
                  <div className="grid grid-cols-2 gap-6">
                    {/* Endpoints */}
                    <div>
                      <h4 className="text-white font-medium mb-3">Endpoints</h4>
                      <div className="space-y-2">
                        {details.endpoints?.map((endpoint, i) => (
                          <div key={i} className="flex items-center gap-3">
                            <span className={`px-2 py-0.5 rounded text-xs font-mono ${endpoint.method === 'GET' ? 'bg-green-500/20 text-green-400' :
                              endpoint.method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                                'bg-yellow-500/20 text-yellow-400'
                              }`}>
                              {endpoint.method}
                            </span>
                            <span className="text-slate-300 font-mono text-sm">
                              {endpoint.path}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Auth & Info */}
                    <div>
                      <h4 className="text-white font-medium mb-3">Authentication</h4>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {details.auth_types?.map((auth, i) => (
                          <span key={i} className="px-2 py-1 bg-slate-700 rounded text-slate-300 text-sm">
                            {auth}
                          </span>
                        ))}
                      </div>

                      <h4 className="text-white font-medium mb-3">Field Schema</h4>
                      <div className="text-sm">
                        <p className="text-slate-400 mb-1">
                          Required: {Object.keys(details.field_schema?.required || {}).length} fields
                        </p>
                        <p className="text-slate-400">
                          Optional: {Object.keys(details.field_schema?.optional || {}).length} fields
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Field Schema Preview */}
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <h4 className="text-white font-medium mb-3">Required Fields</h4>
                    <div className="grid grid-cols-3 gap-2">
                      {Object.entries(details.field_schema?.required || {}).map(([field, schema]: [string, any]) => (
                        <div key={field} className="p-2 bg-slate-800 rounded text-sm">
                          <p className="text-white font-mono">{field}</p>
                          <p className="text-slate-400 text-xs">{schema.type}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
