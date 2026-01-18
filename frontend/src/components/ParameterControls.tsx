/**
 * Parameter controls for simulation settings.
 */

import { motion } from 'framer-motion';
import type { SimulationParams } from '../lib/api';

interface ParameterControlsProps {
  params: SimulationParams;
  onChange: (params: SimulationParams) => void;
  onStart: () => void;
  imagePreview: string;
  disabled?: boolean;
}

export function ParameterControls({
  params,
  onChange,
  onStart,
  imagePreview,
  disabled,
}: ParameterControlsProps) {
  const updateParam = <K extends keyof SimulationParams>(
    key: K,
    value: SimulationParams[K]
  ) => {
    onChange({ ...params, [key]: value });
  };

  const formatIterations = (value: number) => {
    if (value >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(1)}M`;
    }
    if (value >= 1_000) {
      return `${(value / 1_000).toFixed(0)}K`;
    }
    return value.toString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div className="surface rounded-2xl p-6">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Image preview */}
          <div className="relative">
            <img
              src={imagePreview}
              alt="Preview"
              className="w-full aspect-square object-cover rounded-xl"
            />

            {/* Start position indicator */}
            <motion.div
              className="absolute w-3 h-3 bg-violet-500 rounded-full shadow-[0_0_12px_rgba(139,92,246,0.6)]"
              style={{
                left: `calc(${params.start_x * 100}% - 6px)`,
                top: `calc(${params.start_y * 100}% - 6px)`,
              }}
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
            />

            <p className="text-zinc-500 text-xs text-center mt-2">
              Click to set starting position
            </p>

            {/* Click handler for position */}
            <div
              className="absolute inset-0 cursor-crosshair rounded-xl"
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width;
                const y = (e.clientY - rect.top) / rect.height;
                updateParam('start_x', Math.max(0, Math.min(1, x)));
                updateParam('start_y', Math.max(0, Math.min(1, y)));
              }}
            />
          </div>

          {/* Controls */}
          <div className="space-y-6">
            {/* Blur Sigma */}
            <div>
              <label className="text-zinc-300 text-sm font-medium flex justify-between">
                <span>Blur Intensity</span>
                <span className="text-zinc-500">{params.blur_sigma.toFixed(1)}</span>
              </label>
              <input
                type="range"
                min="1"
                max="20"
                step="0.5"
                value={params.blur_sigma}
                onChange={(e) => updateParam('blur_sigma', parseFloat(e.target.value))}
                className="w-full mt-2"
                disabled={disabled}
              />
              <p className="text-zinc-500 text-xs mt-1">
                Higher values create smoother, more abstract lines
              </p>
            </div>

            {/* Iterations */}
            <div>
              <label className="text-zinc-300 text-sm font-medium flex justify-between">
                <span>Detail Level</span>
                <span className="text-zinc-500">{formatIterations(params.iterations)}</span>
              </label>
              <input
                type="range"
                min="100000"
                max="3000000"
                step="100000"
                value={params.iterations}
                onChange={(e) => updateParam('iterations', parseInt(e.target.value))}
                className="w-full mt-2"
                disabled={disabled}
              />
              <p className="text-zinc-500 text-xs mt-1">
                More iterations = more detail (takes longer)
              </p>
            </div>

            {/* Start Position */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-zinc-300 text-sm font-medium flex justify-between">
                  <span>Start X</span>
                  <span className="text-zinc-500">{(params.start_x * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={params.start_x}
                  onChange={(e) => updateParam('start_x', parseFloat(e.target.value))}
                  className="w-full mt-2"
                  disabled={disabled}
                />
              </div>
              <div>
                <label className="text-zinc-300 text-sm font-medium flex justify-between">
                  <span>Start Y</span>
                  <span className="text-zinc-500">{(params.start_y * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={params.start_y}
                  onChange={(e) => updateParam('start_y', parseFloat(e.target.value))}
                  className="w-full mt-2"
                  disabled={disabled}
                />
              </div>
            </div>

            {/* Start Button */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={onStart}
              disabled={disabled}
              className={`
                w-full py-4 rounded-xl font-semibold text-lg
                bg-violet-500 hover:bg-violet-400
                text-white
                transition-colors duration-200
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {disabled ? 'Processing...' : 'Start Drawing'}
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
