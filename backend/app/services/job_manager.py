"""
Job manager for handling simulation jobs.
"""

import uuid
import asyncio
import logging
import queue
from typing import Optional
from dataclasses import dataclass, field
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

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
    # Use thread-safe queue.Queue instead of asyncio.Queue
    # because _run_simulation_sync runs in a thread pool executor
    websocket_queue: queue.Queue = field(default_factory=queue.Queue)


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
        logger.info(f"run_job called for job_id={job_id}")
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        if job.image is None:
            logger.error(f"Job {job_id} has no image")
            job.status = JobStatus.FAILED
            job.error = "No image uploaded"
            return

        job.params = params
        job.status = JobStatus.PROCESSING
        logger.info(f"Job {job_id} status set to PROCESSING, iterations={params.iterations}")

        try:
            # Create simulation config from params
            config = SimulationConfig(
                blur_sigma=params.blur_sigma,
                iterations=params.iterations,
                start_x=params.start_x,
                start_y=params.start_y,
            )

            # Run simulation in a thread pool to avoid blocking
            logger.info(f"Job {job_id} starting simulation in thread pool")
            loop = asyncio.get_event_loop()
            trajectory = await loop.run_in_executor(
                None,
                lambda: self._run_simulation_sync(job, config)
            )
            logger.info(f"Job {job_id} simulation completed, trajectory={'present' if trajectory is not None else 'None'}")

            if trajectory is not None:
                job.trajectory = trajectory

                # Render the result image
                logger.info(f"Job {job_id} rendering result image")
                job.result_image = render_trajectory_to_image(trajectory)

                job.status = JobStatus.COMPLETED
                job.progress = 100.0
                logger.info(f"Job {job_id} status set to COMPLETED")

                # Send completion message to websocket (thread-safe queue)
                job.websocket_queue.put({
                    "type": "complete",
                    "status": "completed",
                    "image_base64": image_to_base64(job.result_image)
                })
            else:
                job.status = JobStatus.FAILED
                job.error = "Simulation produced no output"
                logger.error(f"Job {job_id} failed: simulation produced no output")
                # Send error message so frontend knows
                job.websocket_queue.put({
                    "type": "error",
                    "error": "Simulation produced no output"
                })

        except Exception as e:
            logger.exception(f"Job {job_id} failed with exception")
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.websocket_queue.put({
                "type": "error",
                "error": str(e)
            })

    def _run_simulation_sync(self, job: Job, config: SimulationConfig) -> Optional[np.ndarray]:
        """Synchronous simulation runner for thread pool."""
        logger.info(f"_run_simulation_sync started for job {job.id}")
        trajectory = None

        for result in run_simulation(job.image, config):
            if isinstance(result, SimulationProgress):
                job.progress = result.progress_percent

                # Queue progress update (thread-safe queue.Queue)
                try:
                    job.websocket_queue.put_nowait({
                        "type": "progress",
                        "progress": result.progress_percent,
                        "current_iteration": result.current_iteration,
                        "total_iterations": result.total_iterations,
                        "trajectory_points": result.trajectory_points
                    })
                except queue.Full:
                    pass  # Skip if queue is full

            elif isinstance(result, np.ndarray):
                logger.info(f"Job {job.id} received final trajectory with {len(result)} points")
                trajectory = result

        logger.info(f"_run_simulation_sync completed for job {job.id}")
        return trajectory

    def get_result_image_base64(self, job_id: str) -> Optional[str]:
        """Get the result image as base64."""
        job = self.jobs.get(job_id)
        if job and job.result_image:
            return image_to_base64(job.result_image)
        return None


# Global job manager instance
job_manager = JobManager()
