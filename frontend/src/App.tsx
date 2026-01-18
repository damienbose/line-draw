import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ImageUploader } from './components/ImageUploader';
import { ParameterControls } from './components/ParameterControls';
import { ProcessingView } from './components/ProcessingView';
import { ResultDisplay } from './components/ResultDisplay';
import { useWebSocket } from './hooks/useWebSocket';
import { uploadImage, startJob, type SimulationParams } from './lib/api';

type AppState = 'upload' | 'configure' | 'processing' | 'result';

function App() {
  const [state, setState] = useState<AppState>('upload');
  const [, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<SimulationParams>({
    blur_sigma: 4.0,
    iterations: 1_500_000,
    start_x: 0.5,
    start_y: 0.5,
  });

  const {
    progress,
    currentIteration,
    totalIterations,
    trajectoryPoints,
    resultImage,
    error: wsError,
    connect,
  } = useWebSocket(jobId);

  // Handle image selection
  const handleImageSelect = useCallback(async (file: File) => {
    setSelectedFile(file);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    try {
      // Upload image
      const response = await uploadImage(file);
      setJobId(response.job_id);
      setState('configure');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload image');
    }
  }, []);

  // Handle start processing
  const handleStart = useCallback(async () => {
    if (!jobId) return;
    setError(null);

    try {
      await startJob(jobId, params);
      setState('processing');
      connect(); // Start WebSocket connection
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing');
    }
  }, [jobId, params, connect]);

  // Handle result completion
  useEffect(() => {
    if (resultImage && state === 'processing') {
      setState('result');
    }
  }, [resultImage, state]);

  // Handle WebSocket error
  useEffect(() => {
    if (wsError) {
      setError(wsError);
    }
  }, [wsError]);

  // Reset to initial state
  const handleReset = useCallback(() => {
    setState('upload');
    setSelectedFile(null);
    setImagePreview('');
    setJobId(null);
    setError(null);
    setParams({
      blur_sigma: 4.0,
      iterations: 1_500_000,
      start_x: 0.5,
      start_y: 0.5,
    });
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
          Line Draw
        </h1>
        <p className="text-white/70">
          Transform your images into beautiful line art
        </p>
      </motion.div>

      {/* Error display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass-dark rounded-xl px-6 py-3 mb-6 text-red-300"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="w-full max-w-2xl">
        <AnimatePresence mode="wait">
          {state === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ImageUploader onImageSelect={handleImageSelect} />
            </motion.div>
          )}

          {state === 'configure' && imagePreview && (
            <motion.div
              key="configure"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ParameterControls
                params={params}
                onChange={setParams}
                onStart={handleStart}
                imagePreview={imagePreview}
              />
            </motion.div>
          )}

          {state === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ProcessingView
                progress={progress}
                currentIteration={currentIteration}
                totalIterations={totalIterations}
                trajectoryPoints={trajectoryPoints}
              />
            </motion.div>
          )}

          {state === 'result' && resultImage && jobId && (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ResultDisplay
                jobId={jobId}
                imageBase64={resultImage}
                onReset={handleReset}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-8 text-white/50 text-sm"
      >
        Physics-based drawing simulation
      </motion.div>
    </div>
  );
}

export default App;
