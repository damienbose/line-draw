/**
 * Result display component with download options.
 */

import { motion } from 'framer-motion';
import { Sparkles, Download, RefreshCw } from 'lucide-react';
import { getResultDownloadUrl } from '../lib/api';

interface ResultDisplayProps {
  jobId: string;
  imageBase64: string;
  onReset: () => void;
}

export function ResultDisplay({ jobId, imageBase64, onReset }: ResultDisplayProps) {
  const handleDownload = () => {
    window.open(getResultDownloadUrl(jobId), '_blank');
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, type: 'spring' }}
      className="w-full"
    >
      <div className="surface rounded-2xl p-6">
        <div className="text-center mb-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-500/10 mb-4"
          >
            <Sparkles className="w-6 h-6 text-emerald-400" />
          </motion.div>
          <h3 className="text-2xl font-semibold text-zinc-100">Your drawing is ready</h3>
        </div>

        {/* Result image */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="relative rounded-xl overflow-hidden bg-white mb-6"
        >
          <img
            src={`data:image/png;base64,${imageBase64}`}
            alt="Line drawing result"
            className="w-full"
          />
        </motion.div>

        {/* Action buttons */}
        <div className="grid grid-cols-2 gap-4">
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={handleDownload}
            className="
              flex items-center justify-center gap-2
              py-4 rounded-xl font-semibold
              bg-violet-500 hover:bg-violet-400
              text-white
              transition-colors duration-200
            "
          >
            <Download className="w-5 h-5" />
            Download
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={onReset}
            className="
              flex items-center justify-center gap-2
              py-4 rounded-xl font-semibold
              bg-zinc-800 hover:bg-zinc-700
              text-zinc-200
              transition-colors duration-200
            "
          >
            <RefreshCw className="w-5 h-5" />
            New Image
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
