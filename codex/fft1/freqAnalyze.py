import argparse
from pathlib import Path
import wave

import matplotlib.pyplot as plt
import numpy as np


SOURCE_PROFILES = {
	"fis": {
		"filenames": ("fis.waw", "fis.wav"),
		"ref_freq": 440.0 * pow(2.0, 9.0 / 12.0),
		"formula": "440 * 2^(9/12)",
	},
	"razy": {
		"filenames": ("razy.waw", "razy.wav"),
		"ref_freq": 440.0 * pow(2.0, 10.0 / 12.0),
		"formula": "440 * 2^(10/12)",
	},
}


def update_progress(step: int, total: int, label: str) -> None:
	"""Render a one-line progress bar in the terminal."""
	bar_width = 36
	filled = int(bar_width * step / total)
	bar = "#" * filled + "-" * (bar_width - filled)
	percent = (100.0 * step) / total
	print(f"\rFFT1 progress [{bar}] {percent:6.2f}% | {label}", end="", flush=True)
	if step >= total:
		print()


def load_wav_mono(path: Path) -> tuple[np.ndarray, int]:
	"""Load a WAV file and return normalized mono signal and sample rate."""
	print(f"Reading audio file into memory: {path}")
	with wave.open(str(path), "rb") as wav:
		sample_rate = wav.getframerate()
		channels = wav.getnchannels()
		sample_width = wav.getsampwidth()
		n_frames = wav.getnframes()
		raw = wav.readframes(n_frames)
		print(
			"WAV metadata: "
			f"sample_rate={sample_rate} Hz, channels={channels}, "
			f"sample_width={sample_width} bytes, frames={n_frames}"
		)

	print(f"Raw bytes read: {len(raw)}")

	if sample_width == 1:
		# 8-bit PCM is unsigned.
		data = np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
		data = (data - 128.0) / 128.0
	elif sample_width == 2:
		data = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
		data = data / np.iinfo(np.int16).max
	elif sample_width == 3:
		# 24-bit PCM packed in 3 bytes. Expand to int32 then normalize.
		bytes_ = np.frombuffer(raw, dtype=np.uint8)
		triplets = bytes_.reshape(-1, 3)
		vals = (
			triplets[:, 0].astype(np.int32)
			| (triplets[:, 1].astype(np.int32) << 8)
			| (triplets[:, 2].astype(np.int32) << 16)
		)
		sign_mask = 1 << 23
		vals = (vals ^ sign_mask) - sign_mask
		data = vals.astype(np.float64) / float(1 << 23)
	elif sample_width == 4:
		data = np.frombuffer(raw, dtype=np.int32).astype(np.float64)
		data = data / np.iinfo(np.int32).max
	else:
		raise ValueError(f"Unsupported sample width: {sample_width} bytes")

	if channels > 1:
		print("Converting multi-channel audio to mono by channel averaging")
		data = data.reshape(-1, channels).mean(axis=1)

	print(f"Loaded samples to memory: {data.size} float64 values")

	return data, sample_rate


def resolve_input_file(script_dir: Path, source_name: str) -> Path:
	"""Resolve the source audio file, allowing spelled variants from the request."""
	filenames = SOURCE_PROFILES[source_name]["filenames"]
	for filename in filenames:
		candidate = script_dir / filename
		if candidate.exists():
			return candidate
	raise FileNotFoundError(
		f"Could not find any of {filenames} in {script_dir} for source '{source_name}'"
	)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="FFT1 analysis for fis/razy audio files")
	parser.add_argument(
		"--source",
		choices=("razy", "fis"),
		default="razy",
		help="Choose audio source profile (default: razy)",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	source_name = args.source
	profile = SOURCE_PROFILES[source_name]
	ref_freq = profile["ref_freq"]
	formula = profile["formula"]
	print(f"Selected source profile: {source_name}")
	print(f"Reference frequency ({formula}): {ref_freq:.6f} Hz")

	script_dir = Path(__file__).resolve().parent
	print(f"Resolving input file from directory: {script_dir}")
	wav_path = resolve_input_file(script_dir, source_name)
	print(f"Resolved input audio file: {wav_path.name}")
	signal, sample_rate = load_wav_mono(wav_path)

	n = signal.size
	if n == 0:
		raise ValueError(f"The WAV file has no audio samples: {wav_path.name}")
	print(f"Samples ready for FFT: {n}, sample_rate={sample_rate} Hz")

	total_fft_steps = 6
	update_progress(0, total_fft_steps, "starting")

	# Use a Hann window to reduce spectral leakage.
	print("Computing Hann window")
	window = np.hanning(n)
	update_progress(1, total_fft_steps, "window")

	print("Computing rFFT")
	spectrum = np.fft.rfft(signal * window)
	update_progress(2, total_fft_steps, "fft")

	print("Computing spectrum magnitude")
	magnitudes = np.abs(spectrum)
	update_progress(3, total_fft_steps, "magnitude")

	print("Applying log(1 + magnitude)")
	log_magnitudes = np.log1p(magnitudes)
	update_progress(4, total_fft_steps, "log(1+magnitude)")

	print("Computing frequency bins for rFFT")
	freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
	update_progress(5, total_fft_steps, "frequency bins")

	# Build 1 Hz histogram of FFT magnitude.
	print("Building 1 Hz histogram of transformed magnitude")
	max_hz = int(np.ceil(freqs.max()))
	bin_edges = np.arange(0, max_hz + 2, 1, dtype=np.float64)
	hist_magnitude, _ = np.histogram(freqs, bins=bin_edges, weights=log_magnitudes)
	hz_centers = bin_edges[:-1]
	update_progress(6, total_fft_steps, "done")
	print(f"Histogram ready: {hist_magnitude.size} bins, max frequency {max_hz} Hz")

	plt.figure(figsize=(12, 5))
	plt.bar(hz_centers, hist_magnitude, width=1.0, align="edge", color="#3b82f6")
	plt.axvline(
		ref_freq,
		color="red",
		linestyle="--",
		linewidth=2,
		label=f"Reference: {ref_freq:.2f} Hz",
	)
	plt.title(
		f"1 Hz Frequency Histogram (log(1 + FFT Magnitude))\\n"
		f"{wav_path.name} | source={source_name} | {formula}"
	)
	plt.xlabel("Frequency (Hz)")
	plt.ylabel("Summed log(1 + FFT Magnitude)")
	plt.xlim(0, 5000)
	plt.legend()
	plt.tight_layout()
	print("Plotting is going on...")
	plt.show()


if __name__ == "__main__":
	main()
