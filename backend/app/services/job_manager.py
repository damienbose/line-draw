"""
Job manager for handling simulation jobs.
"""

import uuid
import asyncio
from typing import Optional
from dataclasses import dataclass, field
from PIL import Image
import numpy as np

from app.models.schemas import JobStatus, SimulationParams
from app.core.simulation import SimulationConfig, SimulationProgress, run_simulation
from app.core.drawing import render_trajectory_to_image, image_to_base64


@dataclass
class Job:
    id: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    params: Optional[SimulationParams] = None
    image: Optional[Image.Image] = None
    trajectory: Optional[np.ndarray] = None
    result_image: Optional[Image.Image] = None
    error: Optional[str] = None
    websocket_queue: asyncio.Queue = field(default_factory=asyncio.Queue)


class JobManager:
    """Manages simulation jobs."""

    def __init__(self):
        self.jobs: dict[str, Job] = {}

    def create_job(self, image: Image.Image) -> str:
        """Create a new job with an uploaded image."""
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, image=image)
        self.jobs[job_id] = job
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self.jobs.get(job_id)

    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False

    async def run_job(self, job_id: str, params: SimulationParams) -> None:
        """Run the simulation for a job."""
        job = self.jobs.get(job_id)
        if not job:
            return

        if job.image is None:
            job.status = JobStatus.FAILED
            job.error = "No image uploaded"
            return

        job.params = params
        job.status = JobStatus.PROCESSING

        try:
            # Create simulation config from params
            config = SimulationConfig(
                blur_sigma=params.blur_sigma,
                iterations=params.iterations,
                start_x=params.start_x,
                start_y=params.start_y,
            )

            # Run simulation in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            trajectory = await loop.run_in_executor(
                None,
                lambda: self._run_simulation_sync(job, config)
            )

            if trajectory is not None:
                job.trajectory = trajectory

                # Render the result image
                job.result_image = render_trajectory_to_image(trajectory)

                job.status = JobStatus.COMPLETED
                job.progress = 100.0

                # Send completion message to websocket
                await job.websocket_queue.put({
                    "type": "complete",
                    "status": "completed",
                    "image_base64": image_to_base64(job.result_image)
                })
            else:
                job.status = JobStatus.FAILED
                job.error = "Simulation produced no output"

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            await job.websocket_queue.put({
                "type": "error",
                "error": str(e)
            })

    def _run_simulation_sync(self, job: Job, config: SimulationConfig) -> Optional[np.ndarray]:
        """Synchronous simulation runner for thread pool."""
        trajectory = None

        for result in run_simulation(job.image, config):
            if isinstance(result, SimulationProgress):
                job.progress = result.progress_percent

                # Queue progress update (non-blocking)
                try:
                    job.websocket_queue.put_nowait({
                        "type": "progress",
                        "progress": result.progress_percent,
                        "current_iteration": result.current_iteration,
                        "total_iterations": result.total_iterations,
                        "trajectory_points": result.trajectory_points
                    })
                except asyncio.QueueFull:
                    pass  # Skip if queue is full

            elif isinstance(result, np.ndarray):
                trajectory = result

        return trajectory

    def get_result_image_base64(self, job_id: str) -> Optional[str]:
        """Get the result image as base64."""
        job = self.jobs.get(job_id)
        if job and job.result_image:
            return image_to_base64(job.result_image)
        return None


# Global job manager instance
job_manager = JobManager()
