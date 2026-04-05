import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FileText, Settings, ChevronRight, Shield, Database, Zap, Loader2 } from 'lucide-react';
import { listRequirements, getRequirement, generateConfiguration } from '../services/api';

interface Service {
  service_type: string;
  service_name: string;
  priority: string;
  description: string;
  required_fields: Array<{ field_name: string; data_type: string; description?: string }>;
  optional_fields: Array<{ field_name: string; data_type: string; description?: string }>;
  constraints: string[];
}

interface Requirement {
  id: string;
  document_id: string;
  project_name: string;
  services: Service[];
  services_count?: number;
  integration_points: any[];
  security_requirements: string[];
  compliance_requirements: string[];
  confidence_score: number;
  created_at: string;
}

export default function Requirements() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [selectedReq, setSelectedReq] = useState<Requirement | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (id) {
      loadRequirement(id);
    } else {
      loadRequirements();
    }
  }, [id]);

  const loadRequirements = async () => {
    try {
      const data = await listRequirements();
      setRequirements(data.requirements || []);
    } catch (error) {
      console.error('Failed to load requirements:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRequirement = async (reqId: string) => {
    try {
      const data = await getRequirement(reqId);
      setSelectedReq(data);
    } catch (error) {
      console.error('Failed to load requirement:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateConfig = async () => {
    if (!selectedReq) return;
    setGenerating(true);
    try {
      const result = await generateConfiguration(selectedReq.id);
      navigate(`/configurations/${result.config_id}`);
    } catch (error) {
      console.error('Failed to generate config:', error);
    } finally {
      setGenerating(false);
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
  if (selectedReq) {
    // Ensure arrays exist (handle null/undefined from API)
    const services = selectedReq.services || [];
    const securityReqs = selectedReq.security_requirements || [];
    const complianceReqs = selectedReq.compliance_requirements || [];
    const confidenceScore = selectedReq.confidence_score || 0;

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
              <Link to="/requirements" className="hover:text-white">Requirements</Link>
              <ChevronRight className="w-4 h-4" />
              <span>{selectedReq.project_name || 'Untitled'}</span>
            </div>
            <h1 className="text-2xl font-bold text-white">{selectedReq.project_name || 'Untitled Project'}</h1>
          </div>
          <button
            onClick={handleGenerateConfig}
            disabled={generating}
            className="btn-primary flex items-center gap-2"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Settings className="w-4 h-4" />
                Generate Configuration
              </>
            )}
          </button>
        </div>

        {/* Confidence Score */}
        <div className="glass-card p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-yellow-400" />
            <span className="text-white">AI Confidence Score</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-48 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-yellow-500 to-green-500"
                style={{ width: `${confidenceScore * 100}%` }}
              />
            </div>
            <span className="text-white font-medium">
              {Math.round(confidenceScore * 100)}%
            </span>
          </div>
        </div>

        {/* Services */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <Database className="w-5 h-5" />
            Extracted Services ({services.length})
          </h2>
          {services.length === 0 ? (
            <p className="text-slate-400 text-center py-8">No services extracted. Try re-parsing the document.</p>
          ) : (
            <div className="space-y-4">
              {services.map((service, index) => {
                const requiredFields = service.required_fields || [];
                const optionalFields = service.optional_fields || [];
                const constraints = service.constraints || [];

                return (
                  <div
                    key={index}
                    className="bg-slate-800/50 rounded-lg p-4 border border-slate-700"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-white font-medium">{service.service_name || 'Unknown Service'}</h3>
                        <p className="text-slate-400 text-sm">{service.description || 'No description'}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`status-badge ${service.priority === 'mandatory' ? 'status-error' :
                          service.priority === 'optional' ? 'status-info' : 'status-warning'
                          }`}>
                          {service.priority || 'unknown'}
                        </span>
                        <span className="status-badge status-info">
                          {service.service_type || 'service'}
                        </span>
                      </div>
                    </div>

                    {/* Fields */}
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div>
                        <p className="text-slate-400 text-xs uppercase mb-2">Required Fields</p>
                        <div className="flex flex-wrap gap-1">
                          {requiredFields.length === 0 ? (
                            <span className="text-slate-500 text-xs">None specified</span>
                          ) : (
                            requiredFields.map((f: any, i) => (
                              <span key={i} className="px-2 py-1 bg-red-500/10 text-red-400 rounded text-xs">
                                {typeof f === 'string' ? f : f.field_name || 'field'}
                              </span>
                            ))
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-slate-400 text-xs uppercase mb-2">Optional Fields</p>
                        <div className="flex flex-wrap gap-1">
                          {optionalFields.length === 0 ? (
                            <span className="text-slate-500 text-xs">None specified</span>
                          ) : (
                            optionalFields.map((f: any, i) => (
                              <span key={i} className="px-2 py-1 bg-slate-600/50 text-slate-300 rounded text-xs">
                                {typeof f === 'string' ? f : f.field_name || 'field'}
                              </span>
                            ))
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Constraints */}
                    {constraints.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-700">
                        <p className="text-slate-400 text-xs uppercase mb-2">Constraints</p>
                        <ul className="list-disc list-inside text-slate-300 text-sm space-y-1">
                          {constraints.map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Security & Compliance */}
        <div className="grid grid-cols-2 gap-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-blue-400" />
              Security Requirements
            </h2>
            {securityReqs.length === 0 ? (
              <p className="text-slate-500 text-sm">No security requirements extracted</p>
            ) : (
              <ul className="space-y-2">
                {securityReqs.map((req, i) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2" />
                    {req}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-400" />
              Compliance Requirements
            </h2>
            {complianceReqs.length === 0 ? (
              <p className="text-slate-500 text-sm">No compliance requirements extracted</p>
            ) : (
              <ul className="space-y-2">
                {complianceReqs.map((req, i) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2" />
                    {req}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    );
  }

  // List View
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Requirements</h1>
        <p className="text-slate-400">AI-extracted requirements from uploaded documents</p>
      </div>

      {requirements.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-white font-medium mb-2">No requirements yet</p>
          <p className="text-slate-400 text-sm mb-4">Upload and parse a document to get started</p>
          <Link to="/upload" className="btn-primary inline-block">
            Upload Document
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {requirements.map((req) => (
            <Link
              key={req.id}
              to={`/requirements/${req.id}`}
              className="glass-card p-4 hover:border-blue-500/50 transition-all"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-medium">{req.project_name}</h3>
                  <p className="text-slate-400 text-sm">
                    {req.services_count || req.services?.length || 0} services extracted • {Math.round(req.confidence_score * 100)}% confidence
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-slate-400" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
