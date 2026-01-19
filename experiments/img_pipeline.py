import numpy as np
from scipy.ndimage import gaussian_filter # type: ignore
from PIL import Image


def convert_to_greyscale(img: Image.Image) -> Image.Image:
    return img.convert('L')

def convert_to_numpy(img: Image.Image) -> np.ndarray:
    return np.array(img, dtype=np.float64) / 255.0 # normalize between 0 and 1

def center_crop_square(img: np.ndarray) -> np.ndarray:
    h, w = img.shape
    size = min(h, w)  # target square size
    top = (h - size) // 2
    left = (w - size) // 2
    return img[top:top+size, left:left+size]

def invert_and_flatten_suface(img: np.ndarray) -> np.ndarray:
    img = 1 - img
    img = img / 400.0 # we flatten the height map
    return img

def blur_the_image(img: np.ndarray) -> np.ndarray:
    SIGMA = 1.8
    return gaussian_filter(img, sigma=SIGMA) # type: ignore

def _get_parabaloid_mask(H: int, W: int) -> np.ndarray:
    y = np.linspace(0, 1, H)
    x = np.linspace(0, 1, W)
    Y, X = np.meshgrid(y, x, indexing="ij")

    a = 1
    b = 0.5
    m = 0.55
    n = 0.5
    h = 0.5
    x_shift = X - m
    y_shift = Y - n
    return a * (x_shift ** 2) + b * (y_shift ** 2) + h

def normalize_array(arr: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    max_val = arr.max()
    return arr / (max_val + eps)

def apply_deadzone_mask(img: np.ndarray) -> np.ndarray:
    para_mask = _get_parabaloid_mask(*img.shape)
    para_mask = normalize_array(para_mask)
    return img * para_mask

def get_grads_np(img: np.ndarray):
    """
    return the gradient assuming z: f(x, y) -> img where x, y in [0, 1]
    """
    H, W = img.shape
    assert H == W
    spacing = 1 / H
    gradient_y, gradient_x = np.gradient(img, spacing)
    return gradient_x, gradient_y

def convert_slope_to_angle(slope: np.ndarray) -> np.ndarray:
    _theta = np.atan(slope)
    return _theta

G = -1 * 0.000001
def get_acceleration_right_triangle(theta: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    width_dir_acc = G * np.sin(theta) * np.cos(theta)
    height_dir_acc = G * (np.sin(theta) ** 2)
    magnitude = np.sqrt(width_dir_acc**2 + height_dir_acc**2)
    return width_dir_acc, height_dir_acc, magnitude

def get_acceleration_right_triangle_slope(slope: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    _theta = convert_slope_to_angle(slope)
    return get_acceleration_right_triangle(_theta)


def run_simulation(gradient_x: np.ndarray, gradient_y: np.ndarray, start_coords: np.ndarray, Z: np.ndarray, NUM_ITER: int = 1_500_000):
    initial_velocity = np.array([1.0, 1.0]) * 0.00002 # small ↘ intial velocity
    position_over_iterations_raw = [start_coords.copy()]
    velocity_mag_over_time_raw = [np.linalg.norm(initial_velocity)]

    H, W = Z.shape
    def get_grad_at_xy(x: float, y: float) -> tuple[float, float]: # 2d yx array
        # TODO: can make this with numpy fully
        coords = int(y * W), int(x * H)
        return gradient_x[*coords], gradient_y[*coords]

    position_of_ball = start_coords
    velocity = initial_velocity
    for i in range(NUM_ITER):
        # try:
        x_slope, y_slope = get_grad_at_xy(position_of_ball[0], position_of_ball[1])
        x_acc_comp, _, _ = get_acceleration_right_triangle_slope(x_slope)
        y_acc_comp, _, _, = get_acceleration_right_triangle_slope(y_slope)
        acceleration = np.stack((x_acc_comp, y_acc_comp))
        velocity += acceleration
        position_of_ball += velocity
        for i in (0, 1):
            if position_of_ball[i] >= 1:
                position_of_ball -= velocity
                velocity[i] *= -1
        assert np.all((position_of_ball >= 0) & (position_of_ball < 1)), "Tensor elements are not all between 0 and 1"
        position_over_iterations_raw.append(position_of_ball.copy())
        velocity_mag_over_time_raw.append(np.linalg.norm(velocity))
        # except Exception as e:
        #     print("Broke at: ", i)
        #     raise e from e
        #     break

    position_over_iterations = np.stack(position_over_iterations_raw)
    velocity_mag_over_time = np.stack(velocity_mag_over_time_raw) * 90 * 10 * 8 # * 200 * 100
    return position_over_iterations, velocity_mag_over_time ** 1.5




def process_image(img: Image.Image) -> np.ndarray:
    # Pre-processing
    img = convert_to_greyscale(img)
    img_surface = convert_to_numpy(img)
    img_surface = center_crop_square(img_surface)
    img_surface = invert_and_flatten_suface(img_surface)
    img_surface = blur_the_image(img_surface)
    img_surface = apply_deadzone_mask(img_surface)




    return img_surface

