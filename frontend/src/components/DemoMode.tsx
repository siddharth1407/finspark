/**
 * Demo Mode Component
 * Auto-guided tour that walks through the entire application
 */
import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, RotateCcw, CheckCircle, ArrowRight, Sparkles } from 'lucide-react';

interface DemoStep {
  id: string;
  title: string;
  description: string;
  action: () => Promise<void>;
  duration: number; // seconds
  highlight?: string; // CSS selector to highlight
}

interface DemoModeProps {
  onUpload: () => Promise<any>;
  onParse: (docId: string) => Promise<any>;
  onGenerate: (reqId: string) => Promise<any>;
  onSimulate: (configId: string) => Promise<any>;
  onStepComplete?: (stepId: string, result: any) => void;
}

export function DemoMode({ onUpload, onParse, onGenerate, onSimulate, onStepComplete }: DemoModeProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [stepResults, setStepResults] = useState<Record<string, any>>({});
  const [showCelebration, setShowCelebration] = useState(false);

  const steps: DemoStep[] = [
    {
      id: 'upload',
      title: '📤 Upload Document',
      description: 'Uploading sample Business Requirements Document...',
      action: async () => {
        const result = await onUpload();
        return result;
      },
      duration: 2,
    },
    {
      id: 'parse',
      title: '🧠 AI Analysis',
      description: 'AI is extracting requirements, services, and integrations...',
      action: async () => {
        // This will be called with previous result
        return null; // Placeholder - actual call happens in runDemo
      },
      duration: 5,
    },
    {
      id: 'generate',
      title: '⚙️ Generate Config',
      description: 'Creating production-ready integration configurations...',
      action: async () => {
        return null; // Placeholder - actual call happens in runDemo
      },
      duration: 3,
    },
    {
      id: 'simulate',
      title: '🧪 Run Simulation',
      description: 'Testing integrations with mock APIs...',
      action: async () => {
        return null; // Placeholder - actual call happens in runDemo
      },
      duration: 3,
    },
  ];

  const runDemo = useCallback(async () => {
    setIsRunning(true);
    setIsPaused(false);
    setCurrentStep(0);
    setCompletedSteps([]);
    setStepResults({});
    setShowCelebration(false);

    // Store results locally to avoid stale closure issues
    const results: Record<string, any> = {};

    try {
      // Step 1: Upload
      setCurrentStep(0);
      await new Promise(resolve => setTimeout(resolve, 1000));
      const uploadResult = await onUpload();
      results.upload = uploadResult;
      setStepResults(prev => ({ ...prev, upload: uploadResult }));
      setCompletedSteps(prev => [...prev, 'upload']);
      onStepComplete?.('upload', uploadResult);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Step 2: Parse
      setCurrentStep(1);
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (!results.upload?.document_id) throw new Error('No document to parse');
      const parseResult = await onParse(results.upload.document_id);
      results.parse = parseResult;
      setStepResults(prev => ({ ...prev, parse: parseResult }));
      setCompletedSteps(prev => [...prev, 'parse']);
      onStepComplete?.('parse', parseResult);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Step 3: Generate Config
      setCurrentStep(2);
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (!results.parse?.requirement_id) throw new Error('No requirements to configure');
      const generateResult = await onGenerate(results.parse.requirement_id);
      results.generate = generateResult;
      setStepResults(prev => ({ ...prev, generate: generateResult }));
      setCompletedSteps(prev => [...prev, 'generate']);
      onStepComplete?.('generate', generateResult);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Step 4: Simulate
      setCurrentStep(3);
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (!results.generate?.config_id) throw new Error('No config to simulate');
      const simulateResult = await onSimulate(results.generate.config_id);
      results.simulate = simulateResult;
      setStepResults(prev => ({ ...prev, simulate: simulateResult }));
      setCompletedSteps(prev => [...prev, 'simulate']);
      onStepComplete?.('simulate', simulateResult);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Show celebration
      setShowCelebration(true);
    } catch (error) {
      console.error('Demo failed:', error);
    } finally {
      setIsRunning(false);
    }
  }, [onUpload, onParse, onGenerate, onSimulate, onStepComplete]);

  const resetDemo = () => {
    setIsRunning(false);
    setIsPaused(false);
    setCurrentStep(0);
    setCompletedSteps([]);
    setStepResults({});
    setShowCelebration(false);
  };

  return (
    <div className="space-y-6">
      {/* Demo Control Panel */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-xl p-6 text-white shadow-xl"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Sparkles className="w-6 h-6" />
              One-Click Demo Mode
            </h2>
            <p className="text-sm opacity-80 mt-1">
              Watch AI transform requirements into production-ready integrations
            </p>
          </div>

          <div className="flex gap-2">
            {!isRunning ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={runDemo}
                className="flex items-center gap-2 px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-shadow"
              >
                <Play className="w-5 h-5" />
                Start Demo
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsPaused(!isPaused)}
                className="flex items-center gap-2 px-4 py-3 bg-white/20 rounded-lg font-semibold"
              >
                {isPaused ? <Play className="w-5 h-5" /> : <Pause className="w-5 h-5" />}
              </motion.button>
            )}

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={resetDemo}
              className="flex items-center gap-2 px-4 py-3 bg-white/20 rounded-lg"
            >
              <RotateCcw className="w-5 h-5" />
            </motion.button>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <motion.div
                animate={{
                  scale: currentStep === index && isRunning ? [1, 1.1, 1] : 1,
                  backgroundColor: completedSteps.includes(step.id)
                    ? '#10b981'
                    : currentStep === index
                      ? '#fbbf24'
                      : 'rgba(255,255,255,0.3)'
                }}
                transition={{ duration: 0.5, repeat: currentStep === index && isRunning ? Infinity : 0 }}
                className="w-10 h-10 rounded-full flex items-center justify-center font-bold"
              >
                {completedSteps.includes(step.id) ? (
                  <CheckCircle className="w-6 h-6" />
                ) : (
                  index + 1
                )}
              </motion.div>

              <div className="ml-2 hidden md:block">
                <p className="text-sm font-medium">{step.title}</p>
              </div>

              {index < steps.length - 1 && (
                <ArrowRight className="w-6 h-6 mx-4 opacity-50" />
              )}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Current Step Details */}
      <AnimatePresence mode="wait">
        {isRunning && (
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-indigo-500"
          >
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full"
              />
              <div>
                <h3 className="font-semibold text-lg">{steps[currentStep]?.title}</h3>
                <p className="text-gray-600">{steps[currentStep]?.description}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Celebration */}
      <AnimatePresence>
        {showCelebration && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed inset-0 flex items-center justify-center bg-black/50 z-50"
            onClick={() => setShowCelebration(false)}
          >
            <motion.div
              initial={{ y: 50 }}
              animate={{ y: 0 }}
              className="bg-white rounded-2xl p-8 text-center max-w-md mx-4 shadow-2xl"
            >
              <motion.div
                animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
                transition={{ duration: 0.5 }}
                className="text-6xl mb-4"
              >
                🎉
              </motion.div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Demo Complete!
              </h2>
              <p className="text-gray-600 mb-4">
                AI successfully transformed a requirements document into production-ready
                integration configurations!
              </p>
              <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="font-bold text-green-600">
                    {stepResults.parse?.services_count || 0} Services
                  </p>
                  <p className="text-green-600/70">Extracted</p>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="font-bold text-blue-600">
                    {stepResults.simulate?.summary?.passed || 0}/{stepResults.simulate?.summary?.scenarios_run || 0}
                  </p>
                  <p className="text-blue-600/70">Tests Passed</p>
                </div>
              </div>
              <button
                onClick={() => setShowCelebration(false)}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Explore Results
              </button>
            </motion.div>

            {/* Confetti-like particles */}
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                initial={{
                  x: '50%',
                  y: '50%',
                  scale: 0
                }}
                animate={{
                  x: `${Math.random() * 100}%`,
                  y: `${Math.random() * 100}%`,
                  scale: [0, 1, 0],
                  rotate: Math.random() * 360
                }}
                transition={{
                  duration: 2,
                  delay: Math.random() * 0.5
                }}
                className="fixed w-4 h-4 rounded-full pointer-events-none"
                style={{
                  backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'][i % 5]
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results Summary */}
      {completedSteps.length > 0 && !isRunning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {completedSteps.includes('upload') && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-600 font-medium">✓ Document Uploaded</p>
              <p className="text-sm text-green-600/70">{stepResults.upload?.filename}</p>
            </div>
          )}
          {completedSteps.includes('parse') && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-600 font-medium">✓ {stepResults.parse?.services_count} Services Found</p>
              <p className="text-sm text-blue-600/70">{stepResults.parse?.project_name}</p>
            </div>
          )}
          {completedSteps.includes('generate') && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-purple-600 font-medium">✓ Config Generated</p>
              <p className="text-sm text-purple-600/70">Version {stepResults.generate?.version}</p>
            </div>
          )}
          {completedSteps.includes('simulate') && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <p className="text-orange-600 font-medium">
                ✓ {stepResults.simulate?.summary?.passed || 0}/{stepResults.simulate?.summary?.scenarios_run || 0} Tests Pass
              </p>
              <p className="text-sm text-orange-600/70">
                {Math.round((stepResults.simulate?.summary?.pass_rate || 0))}% Pass Rate
              </p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

export default DemoMode;
