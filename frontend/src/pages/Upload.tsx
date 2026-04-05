import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload as UploadIcon, X, CheckCircle, Loader2, Mic, Sparkles } from 'lucide-react';
import { uploadDocument, parseRequirements } from '../services/api';
import { AIThinking, VoiceInput } from '../components';

interface UploadedDoc {
  id: string;
  filename: string;
  preview: string;
}

interface ExtractedEntity {
  type: string;
  name: string;
  confidence: number;
}

export default function Upload() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [uploadedDoc, setUploadedDoc] = useState<UploadedDoc | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [documentType, setDocumentType] = useState('brd');
  const [showVoiceInput, setShowVoiceInput] = useState(false);
  const [, setVoiceText] = useState('');

  // AI Thinking state
  const [aiStage, setAiStage] = useState<'idle' | 'reading' | 'analyzing' | 'extracting' | 'complete'>('idle');
  const [extractedEntities, setExtractedEntities] = useState<ExtractedEntity[]>([]);
  const [confidenceScore, setConfidenceScore] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setError(null);
    setUploading(true);

    try {
      const result = await uploadDocument(file, 'tenant_demo', documentType);
      setUploadedDoc({
        id: result.document_id,
        filename: result.filename,
        preview: result.preview
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [documentType]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  const handleParse = async () => {
    if (!uploadedDoc) return;

    setParsing(true);
    setError(null);
    setAiStage('reading');
    setExtractedEntities([]);

    try {
      // Stage 1: Reading
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAiStage('analyzing');

      // Stage 2: Analyzing
      await new Promise(resolve => setTimeout(resolve, 1500));
      setAiStage('extracting');

      // Actually call the API
      const result = await parseRequirements(uploadedDoc.id);

      // Stage 3: Extract entities for visualization
      if (result.services) {
        const entities = result.services.map((s: any) => ({
          type: s.service_type,
          name: s.service_name,
          confidence: 0.85 + Math.random() * 0.15
        }));
        setExtractedEntities(entities);
        setConfidenceScore(result.confidence_score || 0.9);
      }

      // Stage 4: Complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAiStage('complete');

      // Navigate after a short delay
      setTimeout(() => {
        navigate(`/requirements/${result.requirement_id}`);
      }, 1500);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Parsing failed');
      setAiStage('idle');
    } finally {
      setParsing(false);
    }
  };

  const handleVoiceComplete = async (text: string) => {
    // Create a text file from voice input
    const blob = new Blob([text], { type: 'text/plain' });
    const file = new File([blob], 'voice_requirements.txt', { type: 'text/plain' });

    setUploading(true);
    try {
      const result = await uploadDocument(file, 'tenant_demo', documentType);
      setUploadedDoc({
        id: result.document_id,
        filename: 'voice_requirements.txt',
        preview: text.substring(0, 500) + (text.length > 500 ? '...' : '')
      });
      setShowVoiceInput(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const resetUpload = () => {
    setUploadedDoc(null);
    setError(null);
    setAiStage('idle');
    setExtractedEntities([]);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-yellow-400" />
          Upload Document
        </h1>
        <p className="text-slate-400">
          Upload a BRD, SOW, or API specification to begin the integration configuration process.
        </p>
      </motion.div>

      {/* Input Mode Toggle */}
      <div className="flex gap-4">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowVoiceInput(false)}
          className={`flex-1 p-4 rounded-xl flex items-center justify-center gap-3 transition-all ${!showVoiceInput
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
              : 'glass-card text-slate-400 hover:text-white'
            }`}
        >
          <UploadIcon className="w-5 h-5" />
          Upload File
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowVoiceInput(true)}
          className={`flex-1 p-4 rounded-xl flex items-center justify-center gap-3 transition-all ${showVoiceInput
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
              : 'glass-card text-slate-400 hover:text-white'
            }`}
        >
          <Mic className="w-5 h-5" />
          Voice Input
        </motion.button>
      </div>

      {/* Voice Input Section */}
      <AnimatePresence>
        {showVoiceInput && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="glass-card p-6"
          >
            <h3 className="text-white font-medium mb-4">🎤 Dictate Your Requirements</h3>
            <VoiceInput
              onTranscript={setVoiceText}
              onComplete={handleVoiceComplete}
              placeholder="Describe your integration needs..."
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document Type Selection */}
      <motion.div
        className="glass-card p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Document Type
        </label>
        <div className="flex gap-4">
          {[
            { value: 'brd', label: 'Business Requirements (BRD)' },
            { value: 'sow', label: 'Statement of Work (SOW)' },
            { value: 'api_spec', label: 'API Specification' }
          ].map((type) => (
            <motion.label
              key={type.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg cursor-pointer transition-all ${documentType === type.value
                ? 'bg-blue-600/20 border border-blue-500/50 text-blue-400'
                : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'
                }`}
            >
              <input
                type="radio"
                name="documentType"
                value={type.value}
                checked={documentType === type.value}
                onChange={(e) => setDocumentType(e.target.value)}
                className="hidden"
              />
              <span>{type.label}</span>
            </motion.label>
          ))}
        </div>
      </motion.div>

      {/* Upload Zone (only show if not using voice) */}
      {!showVoiceInput && !uploadedDoc && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div
            {...getRootProps()}
            className={`glass-card p-12 border-2 border-dashed transition-all cursor-pointer ${isDragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-slate-600 hover:border-slate-500'
              }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center text-center">
              {uploading ? (
                <>
                  <Loader2 className="w-12 h-12 text-blue-400 animate-spin mb-4" />
                  <p className="text-white font-medium">Uploading...</p>
                </>
              ) : (
                <>
                  <motion.div
                    animate={{ y: [0, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <UploadIcon className="w-12 h-12 text-slate-400 mb-4" />
                </motion.div>
                <p className="text-white font-medium mb-2">
                  {isDragActive ? 'Drop the file here' : 'Drag & drop your document'}
                </p>
                <p className="text-slate-400 text-sm">
                  or click to browse (PDF, TXT, DOCX)
                </p>
              </>
            )}
          </div>
          </div>
        </motion.div>
      )}

      {/* Uploaded Document */}
      {uploadedDoc && (
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <motion.div
                className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring" }}
              >
                <CheckCircle className="w-5 h-5 text-green-400" />
              </motion.div>
              <div>
                <p className="text-white font-medium">{uploadedDoc.filename}</p>
                <p className="text-slate-400 text-sm">Document uploaded successfully</p>
              </div>
            </div>
            <button
              onClick={resetUpload}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          </div>

          {/* Preview */}
          <div className="bg-slate-900 rounded-lg p-4 mb-6">
            <p className="text-slate-400 text-sm mb-2">Document Preview:</p>
            <p className="text-slate-300 text-sm whitespace-pre-wrap font-mono">
              {uploadedDoc.preview}
            </p>
          </div>

          {/* AI Thinking Visualization */}
          <AnimatePresence>
            {aiStage !== 'idle' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mb-6"
              >
                <AIThinking
                  isProcessing={parsing}
                  stage={aiStage}
                  entities={extractedEntities}
                  confidenceScore={confidenceScore}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Parse Button */}
          {aiStage === 'idle' && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleParse}
              disabled={parsing}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {parsing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Parsing with AI...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Extract Requirements with AI
                </>
              )}
            </motion.button>
          )}
        </motion.div>
      )}

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-red-500/10 border border-red-500/50 rounded-lg p-4"
          >
            <p className="text-red-400">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Info Box */}
      <motion.div
        className="glass-card p-6 bg-gradient-to-r from-blue-900/20 to-purple-900/20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-white font-medium mb-2">🧠 What happens next?</h3>
        <ol className="list-decimal list-inside text-slate-400 space-y-1 text-sm">
          <li>Your document is parsed and text is extracted</li>
          <li>AI analyzes the content to identify integration requirements</li>
          <li>Services, APIs, and data fields are automatically extracted</li>
          <li>You can review and refine before generating configurations</li>
        </ol>
      </motion.div>
    </div>
  );
}
