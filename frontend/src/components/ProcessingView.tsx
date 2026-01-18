/**
 * Processing view with progress bar and abstract particle animation.
 */

import { motion } from 'framer-motion';
import { useMemo } from 'react';

interface ProcessingViewProps {
  progress: number;
  currentIteration: number;
  totalIterations: number;
  trajectoryPoints: number;
}

// Generate particle positions with subtle drifting animation
const particles = Array.from({ length: 12 }, (_, i) => ({
  id: i,
  initialX: 20 + Math.random() * 60,
  initialY: 20 + Math.random() * 60,
  delay: i * 0.15,
  duration: 3 + Math.random() * 2,
}));

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

  // Generate connecting lines between nearby particles
  const lines = useMemo(() => {
    const result: { x1: number; y1: number; x2: number; y2: number; key: string }[] = [];
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].initialX - particles[j].initialX;
        const dy = particles[i].initialY - particles[j].initialY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 30) {
          result.push({
            x1: particles[i].initialX,
            y1: particles[i].initialY,
            x2: particles[j].initialX,
            y2: particles[j].initialY,
            key: `${i}-${j}`,
          });
        }
      }
    }
    return result;
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div className="surface rounded-2xl p-8 text-center">
        {/* Abstract particle animation */}
        <div className="relative h-32 mb-8 overflow-hidden">
          {/* SVG for connecting lines */}
          <svg className="absolute inset-0 w-full h-full">
            {lines.map((line) => (
              <motion.line
                key={line.key}
                x1={`${line.x1}%`}
                y1={`${line.y1}%`}
                x2={`${line.x2}%`}
                y2={`${line.y2}%`}
                stroke="rgba(139, 92, 246, 0.15)"
                strokeWidth="1"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.1, 0.3, 0.1] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              />
            ))}
          </svg>

          {/* Particles */}
          {particles.map((particle) => (
            <motion.div
              key={particle.id}
              className="absolute w-1.5 h-1.5 bg-violet-400 rounded-full"
              style={{
                left: `${particle.initialX}%`,
                top: `${particle.initialY}%`,
              }}
              animate={{
                x: [0, 8, -5, 3, 0],
                y: [0, -6, 4, -3, 0],
                opacity: [0.6, 1, 0.7, 0.9, 0.6],
              }}
              transition={{
                duration: particle.duration,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: particle.delay,
              }}
            />
          ))}
        </div>

        <h3 className="text-2xl font-semibold text-zinc-100 mb-4">
          Creating your drawing...
        </h3>

        {/* Progress bar */}
        <div className="relative h-1.5 bg-zinc-800 rounded-full overflow-hidden mb-4">
          <motion.div
            className="absolute inset-y-0 left-0 bg-violet-500 rounded-full"
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          />
        </div>

        <p className="text-zinc-200 text-xl font-semibold mb-6">
          {progress.toFixed(1)}%
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="surface-elevated rounded-xl p-3">
            <p className="text-zinc-500 text-xs">Iterations</p>
            <p className="text-zinc-200 font-semibold">
              {formatNumber(currentIteration)} / {formatNumber(totalIterations)}
            </p>
          </div>
          <div className="surface-elevated rounded-xl p-3">
            <p className="text-zinc-500 text-xs">Points Drawn</p>
            <p className="text-zinc-200 font-semibold">
              {formatNumber(trajectoryPoints)}
            </p>
          </div>
          <div className="surface-elevated rounded-xl p-3">
            <p className="text-zinc-500 text-xs">Status</p>
            <p className="text-emerald-400 font-semibold">Drawing</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
