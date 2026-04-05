import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Upload,
  FileText,
  Settings,
  Play,
  ArrowRight,
  CheckCircle,
  Sparkles,
  Zap
} from 'lucide-react';
import { listDocuments, listRequirements, listConfigurations, listSimulations, uploadDocument, parseRequirements, generateConfig, runSimulation } from '../services/api';
import { DemoMode, IntegrationFlow } from '../components';

interface Stats {
  documents: number;
  requirements: number;
  configurations: number;
  simulations: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    documents: 0,
    requirements: 0,
    configurations: 0,
    simulations: 0
  });
  const [loading, setLoading] = useState(true);
  const [showDemo, setShowDemo] = useState(false);
  const [demoResults, setDemoResults] = useState<any>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [docs, reqs, configs, sims] = await Promise.all([
        listDocuments(),
        listRequirements(),
        listConfigurations(),
        listSimulations()
      ]);
      setStats({
        documents: docs.count || 0,
        requirements: reqs.count || 0,
        configurations: configs.count || 0,
        simulations: sims.count || 0
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  // Demo mode handlers
  const handleDemoUpload = async () => {
    const response = await fetch('/demo_data/sample_brd.txt');
    const text = await response.text();
    const blob = new Blob([text], { type: 'text/plain' });
    const file = new File([blob], 'sample_brd.txt', { type: 'text/plain' });
    return await uploadDocument(file, 'tenant_demo', 'brd');
  };

  const handleDemoParse = async (docId: string) => {
    const result = await parseRequirements(docId, 'tenant_demo');
    setDemoResults((prev: any) => ({ ...prev, parse: result }));
    return result;
  };

  const handleDemoGenerate = async (reqId: string) => {
    const result = await generateConfig(reqId, 'tenant_demo');
    return result;
  };

  const handleDemoSimulate = async (configId: string) => {
    const result = await runSimulation(configId, 'tenant_demo');
    return result;
  };

  const workflow = [
    {
      step: 1,
      title: 'Upload Document',
      description: 'Upload BRD, SOW, or API spec',
      icon: Upload,
      link: '/upload',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      step: 2,
      title: 'Parse Requirements',
      description: 'AI extracts services & fields',
      icon: FileText,
      link: '/requirements',
      color: 'from-purple-500 to-pink-500'
    },
    {
      step: 3,
      title: 'Generate Config',
      description: 'Auto-generate mappings',
      icon: Settings,
      link: '/configurations',
      color: 'from-orange-500 to-red-500'
    },
    {
      step: 4,
      title: 'Run Simulation',
      description: 'Test with mock APIs',
      icon: Play,
      link: '/simulation',
      color: 'from-green-500 to-emerald-500'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header with Demo Button */}
      <div className="flex items-start justify-between">
        <div>
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold text-white mb-2 flex items-center gap-3"
          >
            <Sparkles className="w-8 h-8 text-yellow-400" />
            SyncBridge AI
          </motion.h1>
          <p className="text-slate-400">
            AI-powered integration configuration engine - transform requirements into production-ready configs.
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowDemo(!showDemo)}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-indigo-500/30 transition-all"
        >
          <Zap className="w-5 h-5" />
          {showDemo ? 'Hide Demo' : '🎬 One-Click Demo'}
        </motion.button>
      </div>

      {/* Demo Mode Section */}
      {showDemo && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <DemoMode
            onUpload={handleDemoUpload}
            onParse={handleDemoParse}
            onGenerate={handleDemoGenerate}
            onSimulate={handleDemoSimulate}
            onStepComplete={(step, result) => {
              console.log(`Step ${step} complete:`, result);
              loadStats(); // Refresh stats
            }}
          />
        </motion.div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Documents', value: stats.documents, icon: Upload, color: 'blue' },
          { label: 'Requirements', value: stats.requirements, icon: FileText, color: 'purple' },
          { label: 'Configurations', value: stats.configurations, icon: Settings, color: 'orange' },
          { label: 'Simulations', value: stats.simulations, icon: Play, color: 'green' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            className="glass-card p-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">{stat.label}</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {loading ? '...' : stat.value}
                </p>
              </div>
              <stat.icon className={`w-8 h-8 text-${stat.color}-400 opacity-50`} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Integration Flow Visualization */}
      {demoResults?.parse?.services && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-card p-6"
        >
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            📊 Integration Flow Diagram
          </h2>
          <IntegrationFlow
            services={demoResults.parse.services}
            projectName={demoResults.parse.project_name}
          />
        </motion.div>
      )}

      {/* Workflow */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Workflow</h2>
        <div className="flex items-center justify-between">
          {workflow.map((item, index) => (
            <motion.div
              key={item.step}
              className="flex items-center"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.15 }}
            >
              <Link
                to={item.link}
                className="group flex flex-col items-center text-center hover:transform hover:scale-105 transition-all"
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${item.color} flex items-center justify-center mb-3 group-hover:shadow-lg`}
                >
                  <item.icon className="w-8 h-8 text-white" />
                </motion.div>
                <h3 className="text-white font-medium mb-1">{item.title}</h3>
                <p className="text-slate-400 text-xs max-w-[120px]">{item.description}</p>
              </Link>
              {index < workflow.length - 1 && (
                <ArrowRight className="w-6 h-6 text-slate-600 mx-4" />
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Quick Start</h2>
          <div className="space-y-3">
            <Link to="/upload" className="btn-primary w-full flex items-center justify-center gap-2">
              <Upload className="w-4 h-4" />
              Upload New Document
            </Link>
            <Link to="/adapters" className="btn-secondary w-full flex items-center justify-center gap-2">
              View Available Adapters
            </Link>
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold text-white mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">API Server</span>
              <span className="status-badge status-success flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Online
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">AI Pipeline</span>
              <span className="status-badge status-success flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> HuggingFace Ready
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Adapters Loaded</span>
              <span className="status-badge status-info">6 Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Features Highlight */}
      <motion.div
        className="glass-card p-6 bg-gradient-to-r from-blue-900/20 to-purple-900/20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <h2 className="text-xl font-semibold text-white mb-4">🧠 AI-Powered Features</h2>
        <div className="grid grid-cols-3 gap-4">
          <motion.div
            className="p-4 bg-slate-800/50 rounded-lg"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <h3 className="text-white font-medium mb-2">Document Understanding</h3>
            <p className="text-slate-400 text-sm">
              LLM extracts services, fields, and integrations from natural language requirements.
            </p>
          </motion.div>
          <motion.div
            className="p-4 bg-slate-800/50 rounded-lg"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <h3 className="text-white font-medium mb-2">Smart Field Mapping</h3>
            <p className="text-slate-400 text-sm">
              AI matches source fields to target schemas using semantic understanding.
            </p>
          </motion.div>
          <motion.div
            className="p-4 bg-slate-800/50 rounded-lg"
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <h3 className="text-white font-medium mb-2">Auto Test Generation</h3>
            <p className="text-slate-400 text-sm">
              Automatically generates test scenarios for happy paths and edge cases.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
