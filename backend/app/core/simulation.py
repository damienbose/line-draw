"""
Physics simulation for line drawing.
Wraps img_pipeline functions to provide interface for job_manager.
"""
import numpy as np
from PIL import Image
from typing import Generator
from dataclasses import dataclass

from app.core.img_pipeline import (
    process_image,
    get_grads_np,
    run_simulation as run_physics_simulation,
)


@dataclass
class SimulationConfig:
    blur_sigma: float = 4.0  # Note: not used, kept for API compatibility
    iterations: int = 1_500_000
    start_x: float = 0.5
    start_y: float = 0.5
    initial_velocity: float = 1e-5  # Note: not used


@dataclass
class SimulationProgress:
    current_iteration: int
    total_iterations: int
    progress_percent: float
    trajectory_points: int


def run_simulation(
    image: Image.Image,
    config: SimulationConfig,
) -> Generator[SimulationProgress | np.ndarray, None, None]:
    """
    Run simulation matching the notebook workflow.
    Yields SimulationProgress during simulation, final trajectory when complete.
    """
    # Process image to surface
    surface = process_image(image)

    # Get gradients
    gradient_x, gradient_y = get_grads_np(surface)

    # Run simulation
    start_coords = np.array([config.start_x, config.start_y])

    for result in run_physics_simulation(
        gradient_x, gradient_y, start_coords, surface, config.iterations
    ):
        if isinstance(result, dict):
            # Progress update
            yield SimulationProgress(**result)
        else:
            # Final result (positions, velocities tuple)
            positions, velocities = result
            yield positions
