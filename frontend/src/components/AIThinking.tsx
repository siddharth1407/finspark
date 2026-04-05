/**
 * AI Thinking Visualization Component
 * Shows live AI processing with typing animation and entity extraction
 */
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Sparkles, CheckCircle } from 'lucide-react';

interface AIThinkingProps {
  isProcessing: boolean;
  stage: 'idle' | 'reading' | 'analyzing' | 'extracting' | 'complete';
  entities?: ExtractedEntity[];
  confidenceScore?: number;
  onComplete?: () => void;
}

interface ExtractedEntity {
  type: string;
  name: string;
  confidence: number;
}

const stageMessages = {
  idle: '',
  reading: 'Reading document contents...',
  analyzing: 'Analyzing requirements with AI...',
  extracting: 'Extracting services and integrations...',
  complete: 'Analysis complete!'
};

const stageIcons = {
  idle: null,
  reading: '📄',
  analyzing: '🧠',
  extracting: '⚡',
  complete: '✅'
};

export function AIThinking({ isProcessing, stage, entities = [], confidenceScore = 0, onComplete }: AIThinkingProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [visibleEntities, setVisibleEntities] = useState<ExtractedEntity[]>([]);

  // Typing animation for stage message
  useEffect(() => {
    const message = stageMessages[stage];
    if (!message) {
      setDisplayedText('');
      return;
    }

    let index = 0;
    setDisplayedText('');

    const interval = setInterval(() => {
      if (index < message.length) {
        setDisplayedText(message.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 30);

    return () => clearInterval(interval);
  }, [stage]);

  // Reveal entities one by one
  useEffect(() => {
    if (stage !== 'extracting' && stage !== 'complete') {
      setVisibleEntities([]);
      return;
    }

    let index = 0;
    const interval = setInterval(() => {
      if (index < entities.length) {
        setVisibleEntities(entities.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
        if (stage === 'complete' && onComplete) {
          setTimeout(onComplete, 500);
        }
      }
    }, 300);

    return () => clearInterval(interval);
  }, [entities, stage, onComplete]);

  if (!isProcessing && stage === 'idle') return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 rounded-xl p-6 text-white shadow-2xl"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <motion.div
          animate={{ rotate: isProcessing ? 360 : 0 }}
          transition={{ duration: 2, repeat: isProcessing ? Infinity : 0, ease: "linear" }}
        >
          <Brain className="w-8 h-8 text-cyan-400" />
        </motion.div>
        <div>
          <h3 className="font-bold text-lg">AI Processing</h3>
          <p className="text-sm text-gray-300">Powered by HuggingFace LLM</p>
        </div>
        {isProcessing && (
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="ml-auto"
          >
            <Sparkles className="w-6 h-6 text-yellow-400" />
          </motion.div>
        )}
      </div>

      {/* Stage Message with Typing Effect */}
      <div className="bg-black/30 rounded-lg p-4 mb-4 min-h-[60px] font-mono">
        <span className="text-2xl mr-2">{stageIcons[stage]}</span>
        <span className="text-cyan-300">{displayedText}</span>
        {isProcessing && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="inline-block w-2 h-5 bg-cyan-400 ml-1"
          />
        )}
      </div>

      {/* Extracted Entities */}
      <AnimatePresence>
        {visibleEntities.length > 0 && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            className="space-y-2"
          >
            <h4 className="text-sm font-semibold text-gray-300 mb-2">
              Discovered Services:
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {visibleEntities.map((entity, index) => (
                <motion.div
                  key={`${entity.type}-${index}`}
                  initial={{ opacity: 0, x: -20, scale: 0.8 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  className="bg-white/10 backdrop-blur rounded-lg p-3 flex items-center gap-2"
                >
                  <div className={`w-3 h-3 rounded-full ${entity.type === 'kyc' ? 'bg-green-400' :
                      entity.type === 'payment' ? 'bg-blue-400' :
                        entity.type === 'gst' ? 'bg-yellow-400' :
                          'bg-purple-400'
                    }`} />
                  <div className="flex-1">
                    <p className="font-medium text-sm">{entity.name}</p>
                    <p className="text-xs text-gray-400">{entity.type.toUpperCase()}</p>
                  </div>
                  <span className="text-xs text-cyan-400">
                    {Math.round(entity.confidence * 100)}%
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confidence Score */}
      {stage === 'complete' && confidenceScore > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 pt-4 border-t border-white/20"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-300">Overall Confidence</span>
            <span className="text-lg font-bold text-cyan-400">
              {Math.round(confidenceScore * 100)}%
            </span>
          </div>
          <div className="h-2 bg-black/30 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${confidenceScore * 100}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-cyan-400 to-green-400"
            />
          </div>
        </motion.div>
      )}

      {/* Completion Check */}
      {stage === 'complete' && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="flex items-center justify-center mt-4 text-green-400"
        >
          <CheckCircle className="w-6 h-6 mr-2" />
          <span className="font-semibold">Analysis Complete!</span>
        </motion.div>
      )}
    </motion.div>
  );
}

export default AIThinking;
