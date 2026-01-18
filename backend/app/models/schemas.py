"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationParams(BaseModel):
    blur_sigma: float = Field(default=4.0, ge=1.0, le=20.0, description="Gaussian blur sigma")
    iterations: int = Field(default=1_500_000, ge=10000, le=5_000_000, description="Number of simulation iterations")
    start_x: float = Field(default=0.5, ge=0.0, le=1.0, description="Starting X position (0-1)")
    start_y: float = Field(default=0.5, ge=0.0, le=1.0, description="Starting Y position (0-1)")


class UploadResponse(BaseModel):
    job_id: str
    message: str = "Image uploaded successfully"


class StartJobRequest(BaseModel):
    params: SimulationParams = Field(default_factory=SimulationParams)


class StartJobResponse(BaseModel):
    status: JobStatus
    message: str = "Processing started"


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    result_url: Optional[str] = None
    error: Optional[str] = None


class ProgressMessage(BaseModel):
    """WebSocket message for progress updates."""
    progress: float
    current_iteration: int
    total_iterations: int
    trajectory_points: int


class ResultMessage(BaseModel):
    """WebSocket message when processing is complete."""
    status: JobStatus
    result_url: str
    image_base64: Optional[str] = None
