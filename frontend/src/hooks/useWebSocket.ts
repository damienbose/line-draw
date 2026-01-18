/**
 * WebSocket hook for real-time job progress updates.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export interface ProgressMessage {
  type: 'progress';
  progress: number;
  current_iteration: number;
  total_iterations: number;
  trajectory_points: number;
}

export interface CompleteMessage {
  type: 'complete';
  status: 'completed';
  image_base64: string;
}

export interface ErrorMessage {
  type: 'error';
  error: string;
}

export interface HeartbeatMessage {
  type: 'heartbeat';
  status: string;
  progress: number;
}

export type WebSocketMessage = ProgressMessage | CompleteMessage | ErrorMessage | HeartbeatMessage;

interface UseWebSocketResult {
  isConnected: boolean;
  progress: number;
  currentIteration: number;
  totalIterations: number;
  trajectoryPoints: number;
  resultImage: string | null;
  error: string | null;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(jobId: string | null): UseWebSocketResult {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [totalIterations, setTotalIterations] = useState(0);
  const [trajectoryPoints, setTrajectoryPoints] = useState(0);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!jobId || wsRef.current) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/ws/jobs/${jobId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        switch (message.type) {
          case 'progress':
            setProgress(message.progress);
            setCurrentIteration(message.current_iteration);
            setTotalIterations(message.total_iterations);
            setTrajectoryPoints(message.trajectory_points);
            break;

          case 'complete':
            setProgress(100);
            setResultImage(message.image_base64);
            break;

          case 'error':
            setError(message.error);
            break;

          case 'heartbeat':
            setProgress(message.progress);
            break;
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onerror = () => {
      setError('WebSocket connection error');
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
    };
  }, [jobId]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    progress,
    currentIteration,
    totalIterations,
    trajectoryPoints,
    resultImage,
    error,
    connect,
    disconnect,
  };
}
