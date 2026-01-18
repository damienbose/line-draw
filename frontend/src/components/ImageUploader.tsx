/**
 * Image uploader component with drag-and-drop support.
 */

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';

interface ImageUploaderProps {
  onImageSelect: (file: File) => void;
  disabled?: boolean;
}

export function ImageUploader({ onImageSelect, disabled }: ImageUploaderProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onImageSelect(acceptedFiles[0]);
      }
    },
    [onImageSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    },
    maxFiles: 1,
    disabled,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div
        {...getRootProps()}
        className={`
          glass rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-300
          ${isDragActive ? 'scale-105 border-white/40' : 'hover:scale-102'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        <motion.div
          animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <div className="text-6xl mb-4">
            {isDragActive ? '📥' : '🎨'}
          </div>

          <h3 className="text-xl font-semibold text-white mb-2">
            {isDragActive ? 'Drop your image here' : 'Upload an image'}
          </h3>

          <p className="text-white/70">
            Drag and drop an image, or click to select
          </p>

          <p className="text-white/50 text-sm mt-2">
            Supports PNG, JPG, GIF, WebP
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
