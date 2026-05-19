#!/usr/bin/python

from pathlib import Path

import numpy as np
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "orig"
OUTPUT_DIR = BASE_DIR / "out"
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def load_grayscale(path: Path) -> np.ndarray:
	"""Load image as grayscale float32 array."""
	img = Image.open(path).convert("L")
	return np.asarray(img, dtype=np.float32)


def normalize_to_u8(arr: np.ndarray) -> np.ndarray:
	"""Linearly normalize array to uint8 range [0, 255]."""
	min_v = float(arr.min())
	max_v = float(arr.max())
	if max_v <= min_v:
		return np.zeros(arr.shape, dtype=np.uint8)
	scaled = (arr - min_v) / (max_v - min_v)
	return np.clip(scaled * 255.0, 0, 255).astype(np.uint8)


def magnitude_to_u8(magnitude: np.ndarray) -> np.ndarray:
	"""Log-scale magnitude for visualization and convert to uint8."""
	return normalize_to_u8(np.log1p(magnitude))


def phase_to_u8(phase: np.ndarray) -> np.ndarray:
	"""Map phase from [-pi, pi] to [0, 255]."""
	scaled = (phase + np.pi) / (2.0 * np.pi)
	return np.clip(scaled * 255.0, 0, 255).astype(np.uint8)


def save_image(arr: np.ndarray, path: Path) -> None:
	Image.fromarray(arr).save(path)


def prepare_pair(img1: np.ndarray, img2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
	"""Crop both images to shared minimum shape so FFT operations are compatible."""
	h = min(img1.shape[0], img2.shape[0])
	w = min(img1.shape[1], img2.shape[1])
	return img1[:h, :w], img2[:h, :w]


def save_2x2_grid(top_left: np.ndarray, top_right: np.ndarray, bottom_left: np.ndarray, bottom_right: np.ndarray, path: Path) -> None:
	"""Save a 2x2 grid image: originals on top, swapped reconstructions on bottom."""
	h, w = top_left.shape
	pad = 10
	canvas_h = 2 * h + 3 * pad
	canvas_w = 2 * w + 3 * pad
	canvas = np.full((canvas_h, canvas_w), 255, dtype=np.uint8)

	canvas[pad:pad + h, pad:pad + w] = top_left
	canvas[pad:pad + h, 2 * pad + w:2 * pad + 2 * w] = top_right
	canvas[2 * pad + h:2 * pad + 2 * h, pad:pad + w] = bottom_left
	canvas[2 * pad + h:2 * pad + 2 * h, 2 * pad + w:2 * pad + 2 * w] = bottom_right

	Image.fromarray(canvas).save(path)


def display_results_windows(
	name1: str,
	name2: str,
	mag1_u8: np.ndarray,
	phase1_u8: np.ndarray,
	mag2_u8: np.ndarray,
	phase2_u8: np.ndarray,
	grid_path: Path,
) -> None:
	"""Display per-image 2x2 spectrum windows, then the final 2x2 swap grid."""

	def _normalize_1d(v: np.ndarray) -> np.ndarray:
		v = v.astype(np.float32)
		v_min = float(v.min())
		v_max = float(v.max())
		if v_max <= v_min:
			return np.zeros_like(v)
		return (v - v_min) / (v_max - v_min)

	def _show_spectrum_2x2(name: str, mag_u8: np.ndarray, phase_u8: np.ndarray) -> None:
		import matplotlib.pyplot as plt

		x_mag = _normalize_1d(mag_u8.mean(axis=0))
		y_mag = _normalize_1d(mag_u8.mean(axis=1))
		x_phase = _normalize_1d(phase_u8.mean(axis=0))
		y_phase = _normalize_1d(phase_u8.mean(axis=1))

		fig, axes = plt.subplots(2, 2, num=f"{name}: spectrum + projections")
		fig.patch.set_facecolor("black")
		for ax in axes.flat:
			ax.set_facecolor("#111111")
		axes[0, 0].imshow(mag_u8, cmap="gray")
		axes[0, 0].set_title("Magnitude")
		axes[0, 0].axis("off")

		axes[0, 1].imshow(phase_u8, cmap="gray")
		axes[0, 1].set_title("Phase")
		axes[0, 1].axis("off")

		axes[1, 0].plot(x_mag, label="Magnitude", color="cyan", linewidth=1)
		axes[1, 0].plot(x_phase, label="Phase", color="magenta", linewidth=1)
		axes[1, 0].set_title("X-axis projection")
		axes[1, 0].set_xlabel("x")
		axes[1, 0].set_ylabel("normalized")
		axes[1, 0].legend(loc="best", fontsize=8)

		axes[1, 1].plot(y_mag, label="Magnitude", color="cyan", linewidth=1)
		axes[1, 1].plot(y_phase, label="Phase", color="magenta", linewidth=1)
		axes[1, 1].set_title("Y-axis projection")
		axes[1, 1].set_xlabel("y")
		axes[1, 1].set_ylabel("normalized")
		axes[1, 1].legend(loc="best", fontsize=8)

		fig.tight_layout()

	grid_img = Image.open(grid_path)
	try:
		import matplotlib.pyplot as plt
		plt.style.use("dark_background")
		_show_spectrum_2x2(name1, mag1_u8, phase1_u8)
		_show_spectrum_2x2(name2, mag2_u8, phase2_u8)

		fig_grid = plt.figure("Phase Swap 2x2 Grid")
		fig_grid.patch.set_facecolor("black")
		plt.imshow(grid_img, cmap="gray")
		plt.axis("off")
		plt.tight_layout()
		plt.show()
	except Exception:
		# Fallback to system viewer if matplotlib is unavailable.
		pair1 = np.hstack((mag1_u8, phase1_u8))
		pair2 = np.hstack((mag2_u8, phase2_u8))
		Image.fromarray(pair1).show(title=f"{name1}: magnitude | phase")
		Image.fromarray(pair2).show(title=f"{name2}: magnitude | phase")
		grid_img.show(title="Phase Swap 2x2 Grid")


def main() -> None:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

	image_paths = sorted(
		p for p in INPUT_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
	)
	if len(image_paths) < 2:
		raise RuntimeError("Need at least two images in orig/ to perform phase swap.")

	path1, path2 = image_paths[0], image_paths[1]
	name1, name2 = path1.stem, path2.stem

	img1 = load_grayscale(path1)
	img2 = load_grayscale(path2)

	# Match requested preprocessing: flip Albert left-right before FFT.
	if path1.stem.lower() == "albert":
		img1 = np.fliplr(img1)
	if path2.stem.lower() == "albert":
		img2 = np.fliplr(img2)

	img1, img2 = prepare_pair(img1, img2)

	# Forward transforms.
	fft1 = np.fft.fft2(img1)
	fft2 = np.fft.fft2(img2)

	mag1, phase1 = np.abs(fft1), np.angle(fft1)
	mag2, phase2 = np.abs(fft2), np.angle(fft2)
	mag1_u8 = magnitude_to_u8(mag1)
	phase1_u8 = phase_to_u8(phase1)
	mag2_u8 = magnitude_to_u8(mag2)
	phase2_u8 = phase_to_u8(phase2)

	# Swap phases, keep original magnitudes.
	swapped1 = mag1 * np.exp(1j * phase2)
	swapped2 = mag2 * np.exp(1j * phase1)

	# Inverse transforms.
	recon1 = np.fft.ifft2(swapped1).real
	recon2 = np.fft.ifft2(swapped2).real

	# Save originals (cropped to common size).
	img1_u8 = normalize_to_u8(img1)
	img2_u8 = normalize_to_u8(img2)
	recon1_u8 = normalize_to_u8(recon1)
	recon2_u8 = normalize_to_u8(recon2)

	save_image(img1_u8, OUTPUT_DIR / f"{name1}_orig.png")
	save_image(img2_u8, OUTPUT_DIR / f"{name2}_orig.png")

	# Save swapped-phase reconstructions.
	save_image(recon1_u8, OUTPUT_DIR / f"{name1}_mag_{name2}_phase.png")
	save_image(recon2_u8, OUTPUT_DIR / f"{name2}_mag_{name1}_phase.png")
	save_image(mag1_u8, OUTPUT_DIR / f"{name1}_magnitude.png")
	save_image(phase1_u8, OUTPUT_DIR / f"{name1}_phase.png")
	save_image(mag2_u8, OUTPUT_DIR / f"{name2}_magnitude.png")
	save_image(phase2_u8, OUTPUT_DIR / f"{name2}_phase.png")

	grid_path = OUTPUT_DIR / "phase_swap_2x2_grid.png"
	save_2x2_grid(img1_u8, img2_u8, recon1_u8, recon2_u8, grid_path)

	print("Processed images:")
	print(f"  1) {path1}")
	print(f"  2) {path2}")
	print(f"Saved to {OUTPUT_DIR}:")
	print(f"  {name1}_orig.png")
	print(f"  {name2}_orig.png")
	print(f"  {name1}_magnitude.png")
	print(f"  {name1}_phase.png")
	print(f"  {name2}_magnitude.png")
	print(f"  {name2}_phase.png")
	print(f"  {name1}_mag_{name2}_phase.png")
	print(f"  {name2}_mag_{name1}_phase.png")
	print("  phase_swap_2x2_grid.png")

	display_results_windows(name1, name2, mag1_u8, phase1_u8, mag2_u8, phase2_u8, grid_path)


if __name__ == "__main__":
	main()
