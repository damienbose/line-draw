from PIL import Image
import matplotlib.pyplot as plt
import torch

def print_tensor(tensor: torch.Tensor, scatter_points: torch.Tensor | None = None, ball_sizes: torch.Tensor | None = None): # [(x,y)]*time
    plt.imshow(
        tensor.numpy(),
        cmap='hot',
        interpolation='nearest',
        extent=[0, 1, 1, 0]  # force axes to go from 0 to 1
    )
    plt.colorbar()
    if scatter_points is not None:
        xs = scatter_points[:, 0].numpy()
        ys = scatter_points[:, 1].numpy()
        s = 2 if ball_sizes is None else ball_sizes.numpy()
        plt.scatter(xs, ys, c='blue', marker='o', s=s, edgecolors='none')
    plt.show()


def print_list_numbers(numbers: list[float]) -> None:
    # Plot as a line graph
    plt.plot(numbers, marker='o')  # marker='o' shows dots on each point
    plt.title("Line Graph of Floats")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)

    # Show the plot
    plt.show()

def mark_point_on_tensor(tensor: torch.Tensor, ball_position: tuple[float, float], slice_size=0.05) -> torch.Tensor:
    tensor = tensor.clone()
    height, width = ball_position
    assert 0 <= height <= 1
    assert 0 <= width <= 1
    assert 0 <= slice_size <= 1, "slice size is a percentage"
    pixel_height_max, pixel_width_max = tensor.shape
    pixel_height = int(height * pixel_height_max)
    pixel_width = int(width * pixel_width_max)
    slice_size_pixels = int(pixel_width * slice_size)
    ball_position_pixel = (pixel_height, pixel_width)
    row_slice = slice(max(0, ball_position_pixel[0] - slice_size_pixels), min(pixel_height, ball_position_pixel[0] + slice_size_pixels + 1))
    column_slice = slice(max(0, ball_position_pixel[1] - slice_size_pixels), min(pixel_width, ball_position_pixel[1] + slice_size_pixels + 1))
    tensor[row_slice, column_slice] = 0
    return tensor

def get_acceleration_right_triangle_slope(slope: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    _theta = convert_slope_to_angle(slope)
    return get_acceleration_right_triangle(_theta)


def convert_slope_to_angle(slope: torch.Tensor) -> torch.Tensor:
    _theta = torch.atan(slope)
    return _theta

G = -1 * 0.000001
def get_acceleration_right_triangle(theta: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    width_dir_acc = G * torch.sin(theta) * torch.cos(theta)
    height_dir_acc = G * (torch.sin(theta) ** 2)
    magnitude = torch.sqrt(width_dir_acc**2 + height_dir_acc**2)
    return width_dir_acc, height_dir_acc, magnitude

def get_grads(z, H, W):
    """
    return the gradient assuming z: f(x, y) -> z where x, y in [0, 1]
    """
    assert H == W
    spacing = 1 / H # multiplies all point with spacing, (so, [500, 500]) becomes (1, 1)
    gradient_y, gradient_x = torch.gradient(z, spacing=spacing)
    return gradient_x, gradient_y # note: image have coordinate (0, 0) on top left

# for SIMPLe
a = 1
b = 0.5
m = 0.55
n = 0.5
def f_paraboloid(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """
    f: (x, y) -> z (broadcasted)
    """
    x_shift = x - m
    y_shift = y - n
    return a * (x_shift ** 2) + b * (y_shift ** 2)

def f_grad(x: torch.Tensor, y: torch. Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """
    grad_f (x,y) -> (d_x(f), d_y(f)) (broadcasted)
    """
    x_shift = x - m
    y_shift = y - n
    x_grad = 2 * a * x_shift
    y_grad = 2 * b * y_shift
    return x_grad, y_grad

import torch

def normalize_tensor(tensor: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """
    Normalize a tensor to the range [0, 1]. assuming it's in the right range

    Args:
        tensor (torch.Tensor): Input tensor to normalize.
        eps (float): Small constant to avoid division by zero.

    Returns:
        torch.Tensor: Normalized tensor with values in [0, 1].
    """
    max_val = tensor.max()
    return tensor / (max_val + eps)
