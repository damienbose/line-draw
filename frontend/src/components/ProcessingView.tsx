/**
 * Processing view with progress bar and animation.
 */

import { motion } from 'framer-motion';

interface ProcessingViewProps {
  progress: number;
  currentIteration: number;
  totalIterations: number;
  trajectoryPoints: number;
}

export function ProcessingView({
  progress,
  currentIteration,
  totalIterations,
  trajectoryPoints,
}: ProcessingViewProps) {
  const formatNumber = (num: number) => {
    if (num >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(2)}M`;
    }
    if (num >= 1_000) {
      return `${(num / 1_000).toFixed(1)}K`;
    }
    return num.toString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div className="glass rounded-2xl p-8 text-center">
        {/* Animated ball */}
        <div className="relative h-32 mb-8 overflow-hidden">
          <motion.div
            className="absolute w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 shadow-lg"
            animate={{
              x: [0, 100, 200, 150, 50, 0],
              y: [0, 30, 10, 60, 20, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{
              left: 'calc(50% - 16px)',
              top: 'calc(50% - 16px)',
            }}
          />

          {/* Trail effect */}
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-4 h-4 rounded-full bg-purple-400/30"
              animate={{
                x: [0, 100, 200, 150, 50, 0],
                y: [0, 30, 10, 60, 20, 0],
                scale: [0.5, 0.3, 0.2],
                opacity: [0.5, 0.3, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: (i + 1) * 0.1,
              }}
              style={{
                left: 'calc(50% - 8px)',
                top: 'calc(50% - 8px)',
              }}
            />
          ))}
        </div>

        <h3 className="text-2xl font-bold text-white mb-4">
          Creating your drawing...
        </h3>

        {/* Progress bar */}
        <div className="relative h-4 bg-white/10 rounded-full overflow-hidden mb-4">
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500"
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 animate-pulse" />
        </div>

        <p className="text-white text-xl font-semibold mb-6">
          {progress.toFixed(1)}%
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="glass-dark rounded-xl p-3">
            <p className="text-white/60 text-xs">Iterations</p>
            <p className="text-white font-semibold">
              {formatNumber(currentIteration)} / {formatNumber(totalIterations)}
            </p>
          </div>
          <div className="glass-dark rounded-xl p-3">
            <p className="text-white/60 text-xs">Points Drawn</p>
            <p className="text-white font-semibold">
              {formatNumber(trajectoryPoints)}
            </p>
          </div>
          <div className="glass-dark rounded-xl p-3">
            <p className="text-white/60 text-xs">Status</p>
            <p className="text-green-400 font-semibold">Drawing</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
