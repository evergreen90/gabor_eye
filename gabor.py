import io
import math
import numpy as np
from PIL import Image


def generate_gabor(
    size: int = 128,
    cycles: float = 6.0,  # cycles per image (width)
    theta_deg: float = 0.0,  # orientation in deg
    phase_deg: float = 0.0,  # phase in deg
    sigma_ratio: float = 0.22,  # relative to image diagonal
    gamma: float = 1.0,  # aspect ratio
    contrast: float = 0.9,  # 0..1
    bg_level: int = 127,  # 0..255
    use_sine: bool = False,
    normalize: bool = True,
):
    H = W = int(size)
    y, x = np.mgrid[0:H, 0:W].astype(np.float64)
    x -= (W - 1) / 2.0
    y -= (H - 1) / 2.0

    th = math.radians(theta_deg)
    x_p = x * math.cos(th) + y * math.sin(th)
    y_p = -x * math.sin(th) + y * math.cos(th)

    f_cpp = cycles / W  # cycles per pixel (along x')
    phase = math.radians(phase_deg)
    diag = math.sqrt(W * W + H * H)
    sigma = max(1.0, sigma_ratio * diag)

    gauss = np.exp(-(x_p**2 + (gamma**2) * (y_p**2)) / (2.0 * sigma**2))
    arg = 2.0 * math.pi * f_cpp * x_p + phase
    carrier = np.sin(arg) if use_sine else np.cos(arg)

    g = carrier * gauss
    if normalize:
        peak = np.max(np.abs(g))
        if peak > 1e-8:
            g = g / peak
    g = contrast * g

    img = bg_level + (127.0 * g)
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img


def generate_gabor_png(
    size: int,
    cycles: float,
    theta_deg: float,
    phase_deg: float,
    sigma_ratio: float,
    gamma: float,
    contrast: float,
    bg_level: int,
    use_sine: bool,
    normalize: bool,
) -> bytes:
    arr = generate_gabor(
        size=size,
        cycles=cycles,
        theta_deg=theta_deg,
        phase_deg=phase_deg,
        sigma_ratio=sigma_ratio,
        gamma=gamma,
        contrast=contrast,
        bg_level=bg_level,
        use_sine=use_sine,
        normalize=normalize,
    )
    im = Image.fromarray(arr, mode="L")
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()
