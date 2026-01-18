"""
Drawing utilities for rendering trajectory as images.
"""

import numpy as np
from PIL import Image, ImageDraw
from io import BytesIO
import base64


def render_trajectory_to_image(
    trajectory: np.ndarray,
    size: int = 800,
    line_width: float = 0.5,
    line_color: tuple[int, int, int] = (0, 0, 0),
    background_color: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """
    Render trajectory points to a PIL Image.

    Args:
        trajectory: Nx2 array of (x, y) coordinates in [0, 1] range
        size: Output image size (square)
        line_width: Width of the drawn line
        line_color: RGB tuple for line color
        background_color: RGB tuple for background color

    Returns:
        PIL Image with the rendered trajectory
    """
    # Create white background
    img = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(img)

    # Scale trajectory to pixel coordinates
    points = trajectory * size

    # Draw line segments
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        # Skip very long segments (likely boundary bounces)
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if distance > size * 0.1:  # Skip if jump is > 10% of image size
            continue

        draw.line(
            [(x1, y1), (x2, y2)],
            fill=line_color,
            width=max(1, int(line_width))
        )

    return img


def render_trajectory_with_velocity(
    trajectory: np.ndarray,
    size: int = 800,
    min_width: float = 0.5,
    max_width: float = 3.0,
    line_color: tuple[int, int, int] = (0, 0, 0),
    background_color: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """
    Render trajectory with line width based on velocity.
    Faster movement = thicker lines.
    """
    img = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(img)

    # Scale trajectory to pixel coordinates
    points = trajectory * size

    # Calculate velocities
    velocities = np.zeros(len(points))
    for i in range(1, len(points)):
        dx = points[i, 0] - points[i-1, 0]
        dy = points[i, 1] - points[i-1, 1]
        velocities[i] = np.sqrt(dx**2 + dy**2)

    # Normalize velocities for width mapping
    if velocities.max() > 0:
        vel_normalized = velocities / velocities.max()
    else:
        vel_normalized = velocities

    # Draw line segments with varying width
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        # Skip very long segments
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if distance > size * 0.1:
            continue

        # Calculate width based on velocity
        width = min_width + vel_normalized[i+1] * (max_width - min_width)

        draw.line(
            [(x1, y1), (x2, y2)],
            fill=line_color,
            width=max(1, int(width))
        )

    return img


def image_to_base64(img: Image.Image, format: str = 'PNG') -> str:
    """Convert PIL Image to base64 string."""
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def image_to_bytes(img: Image.Image, format: str = 'PNG') -> bytes:
    """Convert PIL Image to bytes."""
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.read()


def save_trajectory_image(
    trajectory: np.ndarray,
    output_path: str,
    size: int = 800
) -> None:
    """Save trajectory to an image file."""
    img = render_trajectory_to_image(trajectory, size)
    img.save(output_path)
