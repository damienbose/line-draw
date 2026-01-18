"""
Physics simulation for line drawing.
Refactored from experiments/utils.py - treats an image as a 3D surface
and simulates a ball rolling down it to produce line art from the trajectory.
"""

import numpy as np
from PIL import Image, ImageFilter
from typing import Generator
from dataclasses import dataclass


# Physics constants
G = -1e-6  # Gravity constant (negative because lower = "downhill")


@dataclass
class SimulationConfig:
    blur_sigma: float = 4.0
    iterations: int = 1_500_000
    start_x: float = 0.5
    start_y: float = 0.5
    initial_velocity: float = 1e-5


@dataclass
class SimulationProgress:
    current_iteration: int
    total_iterations: int
    progress_percent: float
    trajectory_points: int


def convert_slope_to_angle(slope: float) -> float:
    """Convert slope to angle in radians."""
    return np.arctan(slope)


def get_acceleration_components(theta: float) -> tuple[float, float, float]:
    """
    Get acceleration components for a ball on an inclined plane.
    Returns (horizontal_acc, vertical_acc, magnitude).
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    horizontal_acc = G * sin_theta * cos_theta
    vertical_acc = G * (sin_theta ** 2)
    magnitude = np.sqrt(horizontal_acc**2 + vertical_acc**2)

    return horizontal_acc, vertical_acc, magnitude


def get_acceleration_from_slope(slope: float) -> tuple[float, float, float]:
    """Get acceleration from slope value."""
    theta = convert_slope_to_angle(slope)
    return get_acceleration_components(theta)


def compute_gradients(surface: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute gradients of the surface.
    Returns (gradient_x, gradient_y) normalized to [0, 1] coordinate space.
    """
    h, w = surface.shape
    assert h == w, "Surface must be square"

    spacing = 1.0 / h
    gradient_y, gradient_x = np.gradient(surface, spacing)

    return gradient_x, gradient_y


def create_gradient_filter(size: int) -> np.ndarray:
    """
    Create a paraboloid gradient filter to prevent gradient dead zones.
    This ensures the ball always has somewhere to roll.
    """
    y = np.linspace(0, 1, size)
    x = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)

    # Paraboloid centered at (0.55, 0.5)
    a, b = 1.0, 0.5
    m, n = 0.55, 0.5

    x_shift = X - m
    y_shift = Y - n
    paraboloid = a * (x_shift ** 2) + b * (y_shift ** 2)

    # Normalize to [0, 1]
    normalized = paraboloid + 0.5
    normalized = normalized / (normalized.max() + 1e-8)

    return normalized


def preprocess_image(image: Image.Image, blur_sigma: float = 4.0) -> np.ndarray:
    """
    Preprocess image for simulation:
    1. Convert to grayscale
    2. Center crop to square
    3. Invert (dark becomes peaks)
    4. Apply Gaussian blur
    5. Apply gradient filter
    """
    # Convert to grayscale
    gray = image.convert('L')

    # Center crop to square
    w, h = gray.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    gray = gray.crop((left, top, left + size, top + size))

    # Convert to numpy and normalize to [0, 1]
    surface = np.array(gray, dtype=np.float32) / 255.0

    # Invert (dark areas become peaks)
    surface = 1.0 - surface

    # Scale down to prevent too steep slopes
    surface = surface / 400.0

    # Apply Gaussian blur
    blurred_img = Image.fromarray((surface * 255).astype(np.uint8))
    blurred_img = blurred_img.filter(ImageFilter.GaussianBlur(radius=blur_sigma))
    surface = np.array(blurred_img, dtype=np.float32) / 255.0

    # Apply gradient filter to prevent dead zones
    gradient_filter = create_gradient_filter(surface.shape[0])
    surface = surface * gradient_filter

    return surface


class PhysicsSimulator:
    """
    Simulates a ball rolling on a 3D surface derived from an image.
    """

    def __init__(self, surface: np.ndarray):
        self.surface = surface
        self.h, self.w = surface.shape
        assert self.h == self.w, "Surface must be square"

        # Precompute gradients
        self.gradient_x, self.gradient_y = compute_gradients(surface)

    def get_gradient_at(self, x: float, y: float) -> tuple[float, float]:
        """Get gradient at normalized coordinates (0-1)."""
        # Convert to pixel coordinates
        px = int(np.clip(x * self.w, 0, self.w - 1))
        py = int(np.clip(y * self.h, 0, self.h - 1))

        return self.gradient_x[py, px], self.gradient_y[py, px]

    def simulate(
        self,
        config: SimulationConfig,
        progress_interval: int = 10000
    ) -> Generator[SimulationProgress | np.ndarray, None, None]:
        """
        Run the physics simulation.

        Yields SimulationProgress objects during simulation,
        and the final trajectory as numpy array when complete.
        """
        # Initial position and velocity
        position = np.array([config.start_x, config.start_y], dtype=np.float64)
        velocity = np.array([1.0, 1.0], dtype=np.float64) * config.initial_velocity

        # Store trajectory
        trajectory = [position.copy()]

        for i in range(config.iterations):
            # Get gradients at current position
            x_slope, y_slope = self.get_gradient_at(position[0], position[1])

            # Compute acceleration components
            x_acc, _, _ = get_acceleration_from_slope(x_slope)
            y_acc, _, _ = get_acceleration_from_slope(y_slope)

            # Update velocity
            velocity[0] += x_acc
            velocity[1] += y_acc

            # Update position
            position += velocity

            # Bounce off boundaries
            for dim in (0, 1):
                if position[dim] >= 1.0:
                    position -= velocity
                    velocity[dim] *= -1
                elif position[dim] < 0.0:
                    position -= velocity
                    velocity[dim] *= -1

            # Clamp position to valid range
            position = np.clip(position, 0.0, 0.9999)

            trajectory.append(position.copy())

            # Yield progress at intervals
            if i > 0 and i % progress_interval == 0:
                yield SimulationProgress(
                    current_iteration=i,
                    total_iterations=config.iterations,
                    progress_percent=(i / config.iterations) * 100,
                    trajectory_points=len(trajectory)
                )

        # Yield final trajectory
        yield np.array(trajectory)


def run_simulation(
    image: Image.Image,
    config: SimulationConfig
) -> Generator[SimulationProgress | np.ndarray, None, None]:
    """
    High-level function to run simulation on an image.
    """
    # Preprocess the image
    surface = preprocess_image(image, config.blur_sigma)

    # Create simulator and run
    simulator = PhysicsSimulator(surface)

    yield from simulator.simulate(config)
