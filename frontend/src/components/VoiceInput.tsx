/**
 * Voice Input Component
 * Use Web Speech API to dictate requirements
 */
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, Loader2 } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  onComplete?: (finalText: string) => void;
  placeholder?: string;
}

export function VoiceInput({ onTranscript, onComplete, placeholder = "Click mic to start speaking..." }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [volume, setVolume] = useState(0);

  useEffect(() => {
    // Check browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false);
    }
  }, []);

  const startListening = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in your browser. Try Chrome.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('');
      setInterimTranscript('');
    };

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript + ' ';
        } else {
          interim += result[0].transcript;
        }
      }

      if (final) {
        setTranscript(prev => prev + final);
        onTranscript(transcript + final);
      }
      setInterimTranscript(interim);

      // Simulate volume from confidence
      const confidence = event.results[event.results.length - 1]?.[0]?.confidence || 0;
      setVolume(confidence * 100);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      if (transcript && onComplete) {
        onComplete(transcript);
      }
    };

    (window as any).currentRecognition = recognition;
    recognition.start();
  }, [transcript, onTranscript, onComplete]);

  const stopListening = useCallback(() => {
    const recognition = (window as any).currentRecognition;
    if (recognition) {
      recognition.stop();
    }
    setIsListening(false);
    if (transcript && onComplete) {
      onComplete(transcript);
    }
  }, [transcript, onComplete]);

  if (!isSupported) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg">
        <p>🎤 Voice input is not supported in your browser. Please use Chrome.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Microphone Button */}
      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={isListening ? stopListening : startListening}
          className={`relative p-6 rounded-full shadow-lg transition-all ${isListening
              ? 'bg-red-500 hover:bg-red-600'
              : 'bg-gradient-to-br from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700'
            }`}
        >
          {isListening ? (
            <Square className="w-8 h-8 text-white" />
          ) : (
            <Mic className="w-8 h-8 text-white" />
          )}

          {/* Pulse animation when listening */}
          {isListening && (
            <>
              <motion.div
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="absolute inset-0 rounded-full bg-red-500"
              />
              <motion.div
                animate={{ scale: [1, 2, 1], opacity: [0.3, 0, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                className="absolute inset-0 rounded-full bg-red-500"
              />
            </>
          )}
        </motion.button>

        <div className="flex-1">
          <p className="font-medium text-gray-700">
            {isListening ? '🔴 Listening... Speak your requirements' : '🎤 Click to start voice input'}
          </p>
          <p className="text-sm text-gray-500">
            {isListening
              ? 'Describe your integration needs. Click stop when done.'
              : placeholder}
          </p>
        </div>

        {/* Volume indicator */}
        {isListening && (
          <div className="flex items-end gap-1 h-8">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                animate={{
                  height: volume > i * 20 ? [8, 20 + i * 4, 8] : 8
                }}
                transition={{ duration: 0.2, repeat: Infinity }}
                className="w-2 bg-indigo-500 rounded-full"
                style={{ minHeight: 8 }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Transcript Display */}
      <AnimatePresence>
        {(transcript || interimTranscript) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gray-50 rounded-xl p-4 border border-gray-200"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-gray-600">📝 Transcription</span>
              {isListening && (
                <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
              )}
            </div>
            <p className="text-gray-800">
              {transcript}
              <span className="text-gray-400 italic">{interimTranscript}</span>
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick phrases */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-500">Quick phrases:</span>
        {[
          'We need KYC verification',
          'Add payment gateway',
          'Integrate GST validation',
          'Must be PCI compliant'
        ].map((phrase) => (
          <button
            key={phrase}
            onClick={() => {
              setTranscript(prev => prev + phrase + '. ');
              onTranscript(transcript + phrase + '. ');
            }}
            className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"
          >
            + {phrase}
          </button>
        ))}
      </div>
    </div>
  );
}

export default VoiceInput;
