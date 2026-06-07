#!/usr/bin/env python3

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def gaussian(x: np.ndarray, amplitude: float, mean: float, sigma: float, offset: float) -> np.ndarray:
	"""Gaussian model with constant offset."""
	return amplitude * np.exp(-0.5 * ((x - mean) / sigma) ** 2) + offset


def generate_data(
	n_points: int,
	x_min: float,
	x_max: float,
	true_params: tuple[float, float, float, float],
	y_err: float,
	seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
	"""Generate synthetic Gaussian data with homoscedastic Gaussian noise."""
	rng = np.random.default_rng(seed)
	x = np.linspace(x_min, x_max, n_points)
	y_true = gaussian(x, *true_params)
	y = y_true + rng.normal(0.0, y_err, size=n_points)
	dy = np.full_like(y, y_err, dtype=float)
	return x, y, dy


def initial_guess(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
	"""Estimate reasonable initial parameters from data."""
	offset0 = float(np.percentile(y, 10))
	amplitude0 = float(np.max(y) - offset0)
	mean0 = float(x[np.argmax(y)])

	# Weighted width estimate around baseline-subtracted signal.
	weights = np.clip(y - offset0, 1e-12, None)
	variance0 = np.average((x - mean0) ** 2, weights=weights)
	sigma0 = float(np.sqrt(max(variance0, 1e-6)))
	return amplitude0, mean0, sigma0, offset0


def fit_data(x: np.ndarray, y: np.ndarray, dy: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, int]:
	"""Fit Gaussian model and compute chi2 and ndf."""
	p0 = initial_guess(x, y)
	popt, pcov = curve_fit(
		gaussian,
		x,
		y,
		p0=p0,
		sigma=dy,
		absolute_sigma=True,
		maxfev=10000,
	)

	residuals = (y - gaussian(x, *popt)) / dy
	chi2 = float(np.sum(residuals**2))
	ndf = int(len(x) - len(popt))
	return popt, pcov, chi2, ndf


def format_fit_text(popt: np.ndarray, perr: np.ndarray, chi2: float, ndf: int) -> str:
	"""Create annotation string for fitted parameters and chi2/ndf."""
	return "\n".join(
		[
			rf"$A = {popt[0]:.4g} \pm {perr[0]:.2g}$",
			rf"$\mu = {popt[1]:.4g} \pm {perr[1]:.2g}$",
			rf"$\sigma = {popt[2]:.4g} \pm {perr[2]:.2g}$",
			rf"$C = {popt[3]:.4g} \pm {perr[3]:.2g}$",
			rf"$\chi^2/\mathrm{{ndf}} = {chi2:.2f}/{ndf} = {chi2 / ndf:.3f}$",
		]
	)


def make_plot(
	x: np.ndarray,
	y: np.ndarray,
	dy: np.ndarray,
	popt: np.ndarray,
	perr: np.ndarray,
	chi2: float,
	ndf: int,
	out_base: Path,
	show: bool,
) -> None:
	"""Plot data and fit, save to PNG/PDF, and optionally show interactively."""
	fig, ax = plt.subplots(figsize=(8, 5), dpi=120)

	ax.errorbar(x, y, yerr=dy, fmt="o", ms=4, capsize=2, label="Data", alpha=0.9)

	x_fit = np.linspace(x.min(), x.max(), 500)
	y_fit = gaussian(x_fit, *popt)
	ax.plot(x_fit, y_fit, "r-", lw=2, label="Gaussian fit")

	ax.set_xlabel("x")
	ax.set_ylabel("y")
	ax.set_title("Gaussian Fit to Synthetic Data")
	ax.grid(alpha=0.25)
	ax.legend(loc="upper right")

	ax.text(
		0.03,
		0.97,
		format_fit_text(popt, perr, chi2, ndf),
		transform=ax.transAxes,
		va="top",
		ha="left",
		bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
	)

	fig.tight_layout()
	png_path = out_base.with_suffix(".png")
	pdf_path = out_base.with_suffix(".pdf")
	fig.savefig(png_path)
	fig.savefig(pdf_path)
	if show:
		plt.show()
	plt.close(fig)

	print(f"Saved plot: {png_path}")
	print(f"Saved plot: {pdf_path}")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Generate random Gaussian data, fit it, and plot results.")
	parser.add_argument("--n-points", type=int, default=1200, help="Number of generated data points")
	parser.add_argument("--x-min", type=float, default=-5.0, help="Minimum x")
	parser.add_argument("--x-max", type=float, default=5.0, help="Maximum x")
	parser.add_argument("--amplitude", type=float, default=10.0, help="True amplitude")
	parser.add_argument("--mean", type=float, default=0.0, help="True mean")
	parser.add_argument("--sigma", type=float, default=1., help="True sigma")
	parser.add_argument("--offset", type=float, default=0.0, help="True constant offset")
	parser.add_argument("--y-err", type=float, default=1.0, help="Gaussian noise sigma on y")
	parser.add_argument("--seed", type=int, default=42, help="Random seed")
	parser.add_argument("--out", type=Path, default=Path("gfit"), help="Output basename (without extension)")
	parser.add_argument("--no-show", action="store_true", help="Do not open interactive plot window")
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	true_params = (args.amplitude, args.mean, args.sigma, args.offset)
	x, y, dy = generate_data(
		n_points=args.n_points,
		x_min=args.x_min,
		x_max=args.x_max,
		true_params=true_params,
		y_err=args.y_err,
		seed=args.seed,
	)

	popt, pcov, chi2, ndf = fit_data(x, y, dy)
	perr = np.sqrt(np.diag(pcov))

	print("True parameters:")
	print(f"  A={true_params[0]:.6g}, mu={true_params[1]:.6g}, sigma={true_params[2]:.6g}, C={true_params[3]:.6g}")
	print("Fitted parameters:")
	print(f"  A={popt[0]:.6g} ± {perr[0]:.3g}")
	print(f"  mu={popt[1]:.6g} ± {perr[1]:.3g}")
	print(f"  sigma={popt[2]:.6g} ± {perr[2]:.3g}")
	print(f"  C={popt[3]:.6g} ± {perr[3]:.3g}")
	print(f"chi2/ndf = {chi2:.3f}/{ndf} = {chi2 / ndf:.4f}")

	make_plot(x, y, dy, popt, perr, chi2, ndf, args.out, show=not args.no_show)


if __name__ == "__main__":
	main()
