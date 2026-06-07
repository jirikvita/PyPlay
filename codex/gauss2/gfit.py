#!/usr/bin/env python3

import argparse
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


@dataclass
class FitResult:
	"""Container for fit outputs."""
	popt: np.ndarray
	perr: np.ndarray
	chi2: float
	ndf: int
	chi2_per_ndf: float
	output_png: Path
	output_pdf: Path


def gaussian_counts(x: np.ndarray, amplitude: float, mean: float, sigma: float) -> np.ndarray:
	"""Gaussian model for histogram counts."""
	return amplitude * np.exp(-0.5 * ((x - mean) / sigma) ** 2)


def generate_samples(n_samples: int, mean: float, sigma: float, seed: int | None) -> np.ndarray:
	"""Generate x samples directly from a Gaussian distribution."""
	rng = np.random.default_rng(seed)
	return rng.normal(loc=mean, scale=sigma, size=n_samples)


def make_histogram(samples: np.ndarray, bins: int, x_min: float | None, x_max: float | None) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
	"""Build histogram and Poisson uncertainties."""
	if x_min is None:
		x_min = float(np.min(samples))
	if x_max is None:
		x_max = float(np.max(samples))

	counts, edges = np.histogram(samples, bins=bins, range=(x_min, x_max))
	centers = 0.5 * (edges[:-1] + edges[1:])
	err = np.sqrt(np.maximum(counts, 1.0))
	bin_width = float(edges[1] - edges[0])
	return centers, counts.astype(float), err.astype(float), bin_width


def initial_guess(centers: np.ndarray, counts: np.ndarray) -> tuple[float, float, float]:
	"""Estimate fit start values from histogram."""
	amplitude0 = float(np.max(counts))
	mean0 = float(centers[np.argmax(counts)])
	weights = np.clip(counts, 1e-12, None)
	var0 = np.average((centers - mean0) ** 2, weights=weights)
	sigma0 = float(np.sqrt(max(var0, 1e-6)))
	return amplitude0, mean0, sigma0


def fit_histogram(centers: np.ndarray, counts: np.ndarray, err: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, int]:
	"""Fit histogram counts with a Gaussian model and compute chi2/ndf."""
	mask = counts > 0.0
	x_fit = centers[mask]
	y_fit = counts[mask]
	dy_fit = err[mask]

	p0 = initial_guess(x_fit, y_fit)
	popt, pcov = curve_fit(
		gaussian_counts,
		x_fit,
		y_fit,
		p0=p0,
		sigma=dy_fit,
		absolute_sigma=True,
		maxfev=10000,
	)

	residuals = (y_fit - gaussian_counts(x_fit, *popt)) / dy_fit
	chi2 = float(np.sum(residuals**2))
	ndf = int(len(x_fit) - len(popt))
	return popt, pcov, chi2, ndf


def format_fit_text(popt: np.ndarray, perr: np.ndarray, chi2: float, ndf: int) -> str:
	"""Create annotation string for fitted parameters and chi2/ndf."""
	chi2_per_ndf = chi2 / ndf if ndf > 0 else float("nan")
	return "\n".join(
		[
			rf"$A = {popt[0]:.4g} \pm {perr[0]:.2g}$",
			rf"$\mu = {popt[1]:.4g} \pm {perr[1]:.2g}$",
			rf"$\sigma = {popt[2]:.4g} \pm {perr[2]:.2g}$",
			rf"$\chi^2/\mathrm{{ndf}} = {chi2:.2f}/{ndf} = {chi2_per_ndf:.3f}$",
		]
	)


def make_plot(
	samples: np.ndarray,
	centers: np.ndarray,
	counts: np.ndarray,
	err: np.ndarray,
	popt: np.ndarray,
	perr: np.ndarray,
	chi2: float,
	ndf: int,
	true_mean: float,
	true_sigma: float,
	bin_width: float,
	out_base: Path,
	show: bool,
	block_show: bool,
) -> None:
	"""Plot histogram and fit, save to PNG/PDF, and optionally show interactively."""
	fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
	hist_color = "#a8d5e2"
	point_color = "#5c9ead"
	fit_color = "#efb8bb"
	true_color = "#b8c0a4"

	ax.hist(samples, bins=len(counts), range=(centers[0] - 0.5 * bin_width, centers[-1] + 0.5 * bin_width), alpha=0.55, color=hist_color, label="Samples")
	ax.errorbar(centers, counts, yerr=err, fmt="o", ms=4, capsize=2, color=point_color, label="Bin counts")

	x_fit = np.linspace(centers.min(), centers.max(), 500)
	y_fit = gaussian_counts(x_fit, *popt)
	ax.plot(x_fit, y_fit, color=fit_color, lw=2.2, label="Gaussian fit")

	# Expected shape from generation parameters, scaled to histogram counts.
	true_amp = len(samples) * bin_width / (true_sigma * np.sqrt(2.0 * np.pi))
	y_true = gaussian_counts(x_fit, true_amp, true_mean, true_sigma)
	ax.plot(x_fit, y_true, "--", color=true_color, lw=1.8, label="True model")

	ax.set_xlabel("x")
	ax.set_ylabel("Counts per bin")
	ax.set_title("Gaussian Samples: Histogram Fit")
	ax.set_xlim(-3.0 * true_sigma, 3.0 * true_sigma)
	ax.grid(alpha=0.35, color="#d8dee9")
	ax.legend(loc="upper right")

	ax.text(
		0.03,
		0.97,
		format_fit_text(popt, perr, chi2, ndf),
		transform=ax.transAxes,
		va="top",
		ha="left",
		bbox={"boxstyle": "round", "facecolor": "#fffaf0", "alpha": 0.92},
	)

	fig.tight_layout()
	png_path = out_base.with_suffix(".png")
	pdf_path = out_base.with_suffix(".pdf")
	fig.savefig(png_path)
	fig.savefig(pdf_path)
	if show:
		plt.show(block=block_show)
		if not block_show:
			plt.pause(0.001)
	else:
		plt.close(fig)

	print(f"Saved plot: {png_path}")
	print(f"Saved plot: {pdf_path}")


def gfit(
	n_samples: int = 5000,
	bins: int = 60,
	x_min: float | None = None,
	x_max: float | None = None,
	mean: float = 0.0,
	sigma: float = 1.0,
	seed: int | None = None,
	out_base: Path = Path("gfit"),
	show: bool = True,
	block_show: bool = True,
	print_summary: bool = True,
) -> FitResult:
	"""Generate Gaussian samples, histogram them, fit the histogram, and plot."""
	if sigma <= 0:
		raise ValueError("sigma must be > 0")
	if bins < 3:
		raise ValueError("bins must be >= 3")
	if n_samples < 10:
		raise ValueError("n_samples must be >= 10")

	samples = generate_samples(
		n_samples=n_samples,
		mean=mean,
		sigma=sigma,
		seed=seed,
	)
	centers, counts, err, bin_width = make_histogram(samples, bins, x_min, x_max)
	popt, pcov, chi2, ndf = fit_histogram(centers, counts, err)
	perr = np.sqrt(np.diag(pcov))
	chi2_per_ndf = chi2 / ndf if ndf > 0 else float("nan")

	true_amplitude = len(samples) * bin_width / (sigma * np.sqrt(2.0 * np.pi))
	if print_summary:
		print("Generation parameters:")
		seed_text = "None (random)" if seed is None else str(seed)
		print(f"  N={n_samples}, mu={mean:.6g}, sigma={sigma:.6g}, seed={seed_text}")
		print(f"  Expected histogram amplitude ~ {true_amplitude:.6g}")
		print("Fitted parameters:")
		print(f"  A={popt[0]:.6g} ± {perr[0]:.3g}")
		print(f"  mu={popt[1]:.6g} ± {perr[1]:.3g}")
		print(f"  sigma={popt[2]:.6g} ± {perr[2]:.3g}")
		print(f"chi2/ndf = {chi2:.3f}/{ndf} = {chi2_per_ndf:.4f}")

	make_plot(
		samples,
		centers,
		counts,
		err,
		popt,
		perr,
		chi2,
		ndf,
		true_mean=mean,
		true_sigma=sigma,
		bin_width=bin_width,
		out_base=out_base,
		show=show,
		block_show=block_show,
	)

	return FitResult(
		popt=popt,
		perr=perr,
		chi2=chi2,
		ndf=ndf,
		chi2_per_ndf=chi2_per_ndf,
		output_png=out_base.with_suffix(".png"),
		output_pdf=out_base.with_suffix(".pdf"),
	)


def launch_gui() -> None:
	"""Start a simple GUI to tune parameters and run gfit."""
	root = tk.Tk()
	root.title("Gaussian Histogram Fit")
	root.resizable(False, False)

	frame = ttk.Frame(root, padding=12)
	frame.grid(row=0, column=0, sticky="nsew")

	params = {
		"n_samples": tk.StringVar(value="5000"),
		"bins": tk.StringVar(value="60"),
		"x_min": tk.StringVar(value=""),
		"x_max": tk.StringVar(value=""),
		"mean": tk.StringVar(value="0.0"),
		"sigma": tk.StringVar(value="1.0"),
		"seed": tk.StringVar(value=""),
		"out": tk.StringVar(value="gfit"),
	}
	show_plot = tk.BooleanVar(value=True)
	status = tk.StringVar(value="Set parameters and click Run.")

	def exit_all() -> None:
		plt.close("all")
		root.quit()
		root.destroy()

	root.protocol("WM_DELETE_WINDOW", exit_all)

	labels = [
		("Samples", "n_samples"),
		("Bins", "bins"),
		("X min (optional)", "x_min"),
		("X max (optional)", "x_max"),
		("Mean", "mean"),
		("Sigma", "sigma"),
		("Seed (optional)", "seed"),
		("Output basename", "out"),
	]

	for i, (label, key) in enumerate(labels):
		ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", padx=(0, 10), pady=3)
		ttk.Entry(frame, textvariable=params[key], width=24).grid(row=i, column=1, sticky="ew", pady=3)

	ttk.Checkbutton(frame, text="Show plot window", variable=show_plot).grid(row=len(labels), column=0, columnspan=2, sticky="w", pady=(6, 4))

	def run_fit() -> None:
		try:
			x_min_value = params["x_min"].get().strip()
			x_max_value = params["x_max"].get().strip()
			seed_value = params["seed"].get().strip()
			x_min = float(x_min_value) if x_min_value else None
			x_max = float(x_max_value) if x_max_value else None
			seed = int(seed_value) if seed_value else None

			result = gfit(
				n_samples=int(params["n_samples"].get()),
				bins=int(params["bins"].get()),
				x_min=x_min,
				x_max=x_max,
				mean=float(params["mean"].get()),
				sigma=float(params["sigma"].get()),
				seed=seed,
				out_base=Path(params["out"].get()),
				show=bool(show_plot.get()),
				block_show=False,
				print_summary=False,
			)
			status.set(
				"Done: "
				f"mu={result.popt[1]:.4f}, sigma={result.popt[2]:.4f}, "
				f"chi2/ndf={result.chi2_per_ndf:.3f}"
			)
		except Exception as exc:
			status.set(f"Error: {exc}")

	button_row = ttk.Frame(frame)
	button_row.grid(row=len(labels) + 1, column=0, columnspan=2, sticky="ew", pady=(6, 4))
	button_row.columnconfigure(0, weight=1)
	button_row.columnconfigure(1, weight=1)

	tk.Button(
		button_row,
		text="Run",
		command=run_fit,
		bg="#4caf50",
		fg="white",
		activebackground="#3f9143",
		activeforeground="white",
		relief="raised",
	).grid(row=0, column=0, sticky="ew", padx=(0, 4))
	tk.Button(
		button_row,
		text="Exit",
		command=exit_all,
		bg="#d98c8c",
		fg="white",
		activebackground="#c97f7f",
		activeforeground="white",
		relief="raised",
	).grid(row=0, column=1, sticky="ew", padx=(4, 0))

	ttk.Label(frame, textvariable=status, foreground="#333333", wraplength=340, justify="left").grid(row=len(labels) + 2, column=0, columnspan=2, sticky="w")

	root.mainloop()


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Generate Gaussian-distributed x samples, histogram them, and fit the histogram.")
	parser.add_argument("--n-samples", type=int, default=5000, help="Number of generated x samples")
	parser.add_argument("--bins", type=int, default=60, help="Histogram bin count")
	parser.add_argument("--x-min", type=float, default=None, help="Histogram minimum x (default: sample min)")
	parser.add_argument("--x-max", type=float, default=None, help="Histogram maximum x (default: sample max)")
	parser.add_argument("--mean", type=float, default=0.0, help="True mean")
	parser.add_argument("--sigma", type=float, default=1.0, help="True sigma")
	parser.add_argument("--seed", type=int, default=None, help="Optional random seed (default: random)")
	parser.add_argument("--out", type=Path, default=Path("gfit"), help="Output basename (without extension)")
	parser.add_argument("--no-show", action="store_true", help="Do not open interactive plot window")
	parser.add_argument("--gui", action="store_true", help="Launch GUI with tunable parameters (default behavior)")
	parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of GUI")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	if not args.cli:
		launch_gui()
		return

	gfit(
		n_samples=args.n_samples,
		bins=args.bins,
		x_min=args.x_min,
		x_max=args.x_max,
		mean=args.mean,
		sigma=args.sigma,
		seed=args.seed,
		out_base=args.out,
		show=not args.no_show,
		block_show=True,
		print_summary=True,
	)


if __name__ == "__main__":
	main()
