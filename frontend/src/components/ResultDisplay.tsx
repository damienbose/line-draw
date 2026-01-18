/**
 * Result display component with download options.
 */

import { motion } from 'framer-motion';
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
      <div className="glass rounded-2xl p-6">
        <div className="text-center mb-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-block text-5xl mb-4"
          >
            🎉
          </motion.div>
          <h3 className="text-2xl font-bold text-white">Your drawing is ready!</h3>
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
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDownload}
            className="
              py-4 rounded-xl font-semibold
              bg-gradient-to-r from-purple-500 to-pink-500
              text-white shadow-lg
              hover:shadow-xl transition-all duration-300
            "
          >
            Download PNG
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onReset}
            className="
              py-4 rounded-xl font-semibold
              bg-white/10 border border-white/20
              text-white
              hover:bg-white/20 transition-all duration-300
            "
          >
            Create Another
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
