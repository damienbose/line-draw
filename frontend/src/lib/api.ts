/**
 * API client for the line-draw backend.
 */

const API_BASE = '/api';

export interface SimulationParams {
  blur_sigma: number;
  iterations: number;
  start_x: number;
  start_y: number;
}

export interface UploadResponse {
  job_id: string;
  message: string;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  result_url?: string;
  error?: string;
}

export async function uploadImage(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/images/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload image');
  }

  return response.json();
}

export async function startJob(jobId: string, params: SimulationParams): Promise<void> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ params }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start job');
  }
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get job status');
  }

  return response.json();
}

export async function getJobResultBase64(jobId: string): Promise<string> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}/result/base64`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get result');
  }

  const data = await response.json();
  return data.image_base64;
}

export function getResultDownloadUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/result`;
}
