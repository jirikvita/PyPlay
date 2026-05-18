import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
import importlib

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

try:
	go = importlib.import_module("plotly.graph_objects")
	make_subplots = importlib.import_module("plotly.subplots").make_subplots
	PLOTLY_AVAILABLE = True
except Exception:
	go = None
	make_subplots = None
	PLOTLY_AVAILABLE = False


def gauss_counts(x, amplitude, mean, sigma):
	"""Gaussian model for binned event counts."""
	return amplitude * np.exp(-0.5 * ((x - mean) / sigma) ** 2)


def run_toy(n_events, true_mean, true_sigma, n_bins=60, show_plot=True, save_outputs=True):
	"""Generate Gaussian toy data, fit it, and return fit results.

	When show_plot=False and save_outputs=False, this acts as a silent fit.
	"""
	rng = np.random.default_rng() #(12345)
	events = rng.normal(loc=true_mean, scale=true_sigma, size=n_events)

	# Build histogram around the generated Gaussian center/width
	x_min = true_mean - 4.0 * true_sigma
	x_max = true_mean + 4.0 * true_sigma
	counts, edges = np.histogram(events, bins=n_bins, range=(x_min, x_max))
	centers = 0.5 * (edges[:-1] + edges[1:])
	widths = np.diff(edges)
	mask_nonzero = counts > 0
	centers_nz = centers[mask_nonzero]
	counts_nz = counts[mask_nonzero]
	widths_nz = widths[mask_nonzero]

	if len(counts_nz) < 4:
		raise RuntimeError("Not enough nonzero bins for a stable fit. Increase n_events or reduce n_bins.")

	yerr = np.sqrt(counts_nz)
	p0 = [np.max(counts), np.mean(events), np.std(events)]

	popt, _ = curve_fit(
		gauss_counts,
		centers_nz,
		counts_nz,
		p0=p0,
		sigma=yerr,
		absolute_sigma=True,
		maxfev=10000,
	)
	amp_fit, mean_fit, sigma_fit = popt

	fit_counts = gauss_counts(centers_nz, amp_fit, mean_fit, sigma_fit)
	x_smooth = np.linspace(x_min, x_max, 800)
	fit_smooth = gauss_counts(x_smooth, amp_fit, mean_fit, sigma_fit)

	chi2 = np.sum(((counts_nz - fit_counts) / yerr) ** 2)
	ndf = len(counts_nz) - len(popt)
	chi2_ndf = chi2 / ndf

	residuals = counts_nz - fit_counts

	results = {
		"amplitude": float(amp_fit),
		"mean": float(mean_fit),
		"sigma": float(sigma_fit),
		"chi2": float(chi2),
		"ndf": int(ndf),
		"chi2_ndf": float(chi2_ndf),
	}

	if not show_plot and not save_outputs:
		return results

	fig, (ax_top, ax_bot) = plt.subplots(
		2,
		1,
		figsize=(8.5, 6.5),
		sharex=True,
		gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05},
	)

	ax_top.errorbar(
		centers_nz,
		counts_nz,
		yerr=yerr,
		xerr=0.5 * widths_nz,
		fmt="o",
		markersize=4,
		color="black",
		ecolor="black",
		elinewidth=1,
		capsize=2,
		label=f"Data (N={n_events})",
	)
	ax_top.plot(x_smooth, fit_smooth, color="crimson", lw=2, label="Gaussian fit")
	ax_top.set_ylabel("Counts / bin")
	ax_top.legend(loc="upper right")
	ax_top.grid(alpha=0.25)

	fit_text = (
		f"$\\mu = {mean_fit:.4f}$\n"
		f"$\\sigma = {sigma_fit:.4f}$\n"
		f"$\\chi^2/\\mathrm{{ndf}} = {chi2:.1f}/{ndf} = {chi2_ndf:.3f}$"
	)
	ax_top.text(
		0.03,
		0.97,
		fit_text,
		transform=ax_top.transAxes,
		va="top",
		ha="left",
		bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "gray"},
	)

	ax_bot.errorbar(
		centers_nz,
		residuals,
		yerr=yerr,
		xerr=0.5 * widths_nz,
		fmt="o",
		markersize=4,
		color="navy",
		ecolor="navy",
		elinewidth=1,
		capsize=2,
	)
	ax_bot.axhline(0.0, color="red", lw=1.5)
	ax_bot.set_xlabel("x")
	ax_bot.set_ylabel("Residuals")
	ax_bot.grid(alpha=0.25)

	if save_outputs:
		# Auto-save outputs: PNG, PDF, and HTML reports (static + plotly)
		out_dir = Path(__file__).resolve().parent / "outputs"
		out_dir.mkdir(parents=True, exist_ok=True)
		tag = datetime.now().strftime("%Y%m%d_%H%M%S")
		base_name = f"fitgaus_{tag}"
		png_path = out_dir / f"{base_name}.png"
		pdf_path = out_dir / f"{base_name}.pdf"
		html_path = out_dir / f"{base_name}.html"
		plotly_html_path = out_dir / f"{base_name}_plotly.html"

		fig.savefig(png_path, dpi=150, bbox_inches="tight")
		fig.savefig(pdf_path, bbox_inches="tight")

		html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Gaussian Toy Fit Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .meta {{ margin-bottom: 16px; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #bbb; }}
  </style>
</head>
<body>
  <h2>Gaussian Toy Fit Report</h2>
  <div class=\"meta\">
    <p><b>Generated events:</b> {n_events}</p>
    <p><b>Input mean:</b> {true_mean}</p>
    <p><b>Input sigma:</b> {true_sigma}</p>
    <p><b>Fitted mean:</b> {mean_fit:.6f}</p>
    <p><b>Fitted sigma:</b> {sigma_fit:.6f}</p>
    <p><b>Chi2/ndf:</b> {chi2:.3f}/{ndf} = {chi2_ndf:.6f}</p>
  </div>
  <img src=\"{png_path.name}\" alt=\"Gaussian fit plot\" />
</body>
</html>
"""
		html_path.write_text(html_content, encoding="utf-8")

		if PLOTLY_AVAILABLE:
			pfig = make_subplots(
				rows=2,
				cols=1,
				shared_xaxes=True,
				vertical_spacing=0.05,
				row_heights=[0.75, 0.25],
			)

			pfig.add_trace(
				go.Scatter(
					x=centers_nz,
					y=counts_nz,
					mode="markers",
					name=f"Data (N={n_events})",
					error_y=dict(type="data", array=yerr, visible=True),
					error_x=dict(type="data", array=0.5 * widths_nz, visible=True),
					marker=dict(color="black", size=6),
				),
				row=1,
				col=1,
			)
			pfig.add_trace(
				go.Scatter(
					x=x_smooth,
					y=fit_smooth,
					mode="lines",
					name="Gaussian fit",
					line=dict(color="crimson", width=2),
				),
				row=1,
				col=1,
			)

			pfig.add_trace(
				go.Scatter(
					x=centers_nz,
					y=residuals,
					mode="markers",
					name="Residuals",
					error_y=dict(type="data", array=yerr, visible=True),
					error_x=dict(type="data", array=0.5 * widths_nz, visible=True),
					marker=dict(color="navy", size=6),
					showlegend=False,
				),
				row=2,
				col=1,
			)
			pfig.add_hline(y=0.0, line=dict(color="red", width=1.5), row=2, col=1)

			pfig.update_layout(
				title=(
					"Gaussian Toy Fit"
					f"<br><sup>mu={mean_fit:.4f}, sigma={sigma_fit:.4f}, "
					f"chi2/ndf={chi2:.1f}/{ndf}={chi2_ndf:.3f}</sup>"
				),
				template="plotly_white",
				height=700,
			)
			pfig.update_yaxes(title_text="Counts / bin", row=1, col=1)
			pfig.update_yaxes(title_text="Residuals", row=2, col=1)
			pfig.update_xaxes(title_text="x", row=2, col=1)

			pfig.write_html(str(plotly_html_path), include_plotlyjs="cdn")
			print(f"Saved Plotly HTML: {plotly_html_path}")
		else:
			print("Plotly not available: skipped Plotly HTML export.")

		print(f"Saved PNG:  {png_path}")
		print(f"Saved PDF:  {pdf_path}")
		print(f"Saved HTML: {html_path}")

	if show_plot:
		plt.show()
	else:
		plt.close(fig)

	return results


def run_super_toy(n_toys, n_events, true_mean, true_sigma, n_bins=60):
	"""Run many toys and show 2x2 histograms of fit outputs."""
	def add_stats_box(ax, values):
		vals = np.asarray(values, dtype=float)
		stats_text = (
			f"N = {len(vals)}\n"
			f"mean = {np.mean(vals):.4g}\n"
			f"std = {np.std(vals, ddof=1):.4g}"
		)
		ax.text(
			0.97,
			0.97,
			stats_text,
			transform=ax.transAxes,
			ha="right",
			va="top",
			bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "gray"},
		)

	amplitudes = []
	means = []
	sigmas = []
	chi2_values = []

	n_failed = 0
	for _ in range(n_toys):
		try:
			res = run_toy(
				n_events=n_events,
				true_mean=true_mean,
				true_sigma=true_sigma,
				n_bins=n_bins,
				show_plot=False,
				save_outputs=False,
			)
			amplitudes.append(res["amplitude"])
			means.append(res["mean"])
			sigmas.append(res["sigma"])
			chi2_values.append(res["chi2"])
		except Exception:
			n_failed += 1

	if len(amplitudes) == 0:
		raise RuntimeError("All toys failed to fit.")

	fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.5))
	axes = axes.ravel()

	axes[0].hist(amplitudes, bins=30, color="steelblue", alpha=0.85, edgecolor="black")
	axes[0].set_title("Fitted amplitude")
	axes[0].set_xlabel("Amplitude")
	axes[0].set_ylabel("Entries")
	add_stats_box(axes[0], amplitudes)

	axes[1].hist(means, bins=30, color="seagreen", alpha=0.85, edgecolor="black")
	axes[1].set_title("Fitted mean")
	axes[1].set_xlabel("Mean")
	axes[1].set_ylabel("Entries")
	add_stats_box(axes[1], means)

	axes[2].hist(sigmas, bins=30, color="darkorange", alpha=0.85, edgecolor="black")
	axes[2].set_title("Fitted sigma")
	axes[2].set_xlabel("Sigma")
	axes[2].set_ylabel("Entries")
	add_stats_box(axes[2], sigmas)

	axes[3].hist(chi2_values, bins=30, color="indianred", alpha=0.85, edgecolor="black")
	axes[3].set_title("chi2")
	axes[3].set_xlabel("chi2")
	axes[3].set_ylabel("Entries")
	add_stats_box(axes[3], chi2_values)

	for ax in axes:
		ax.grid(alpha=0.25)

	fig.suptitle(
		f"SuperToy summary: requested={n_toys}, fitted={len(amplitudes)}, failed={n_failed}",
		fontsize=12,
	)
	fig.tight_layout(rect=[0, 0, 1, 0.96])

	# Auto-save SuperToy summary figure
	out_dir = Path(__file__).resolve().parent / "outputs"
	out_dir.mkdir(parents=True, exist_ok=True)
	tag = datetime.now().strftime("%Y%m%d_%H%M%S")
	base_name = f"supertoy_{tag}"
	png_path = out_dir / f"{base_name}.png"
	pdf_path = out_dir / f"{base_name}.pdf"
	fig.savefig(png_path, dpi=150, bbox_inches="tight")
	fig.savefig(pdf_path, bbox_inches="tight")
	print(f"Saved SuperToy PNG: {png_path}")
	print(f"Saved SuperToy PDF: {pdf_path}")

	plt.show()


def launch_gui():
	root = tk.Tk()
	root.title("Gaussian Toy Fit")
	root.resizable(False, False)

	pad = {"padx": 8, "pady": 6}

	tk_title = tk.Label(root, text="Gaussian Toy + Fit", font=("Helvetica", 13, "bold"))
	tk_title.grid(row=0, column=0, columnspan=2, **pad)

	tk_events = tk.Label(root, text="n_events:")
	tk_events.grid(row=1, column=0, sticky="e", **pad)
	entry_events = tk.Entry(root, width=16)
	entry_events.insert(0, "8000")
	entry_events.grid(row=1, column=1, sticky="w", **pad)

	tk_mean = tk.Label(root, text="gauss mean:")
	tk_mean.grid(row=2, column=0, sticky="e", **pad)
	entry_mean = tk.Entry(root, width=16)
	entry_mean.insert(0, "0.5")
	entry_mean.grid(row=2, column=1, sticky="w", **pad)

	tk_sigma = tk.Label(root, text="gauss sigma:")
	tk_sigma.grid(row=3, column=0, sticky="e", **pad)
	entry_sigma = tk.Entry(root, width=16)
	entry_sigma.insert(0, "1.2")
	entry_sigma.grid(row=3, column=1, sticky="w", **pad)

	tk_ntoys = tk.Label(root, text="NToys:")
	tk_ntoys.grid(row=4, column=0, sticky="e", **pad)
	entry_ntoys = tk.Entry(root, width=16)
	entry_ntoys.insert(0, "100")
	entry_ntoys.grid(row=4, column=1, sticky="w", **pad)

	silent_var = tk.BooleanVar(value=False)
	chk_silent = tk.Checkbutton(root, text="Silent fit (no plot/save)", variable=silent_var)
	chk_silent.grid(row=5, column=0, columnspan=2, sticky="w", **pad)

	def on_run():
		try:
			n_events = int(entry_events.get())
			true_mean = float(entry_mean.get())
			true_sigma = float(entry_sigma.get())
			if n_events <= 0:
				raise ValueError("n_events must be > 0")
			if true_sigma <= 0:
				raise ValueError("sigma must be > 0")
			if silent_var.get():
				res = run_toy(
					n_events=n_events,
					true_mean=true_mean,
					true_sigma=true_sigma,
					show_plot=False,
					save_outputs=False,
				)
				print(
					"Silent fit results: "
					f"mean={res['mean']:.6f}, sigma={res['sigma']:.6f}, "
					f"chi2/ndf={res['chi2_ndf']:.6f} ({res['chi2']:.3f}/{res['ndf']})"
				)
			else:
				run_toy(n_events=n_events, true_mean=true_mean, true_sigma=true_sigma)
		except Exception as exc:
			messagebox.showerror("Input/Run error", str(exc))

	def on_super_toy():
		try:
			n_toys = int(entry_ntoys.get())
			n_events = int(entry_events.get())
			true_mean = float(entry_mean.get())
			true_sigma = float(entry_sigma.get())
			if n_toys <= 0:
				raise ValueError("NToys must be > 0")
			if n_events <= 0:
				raise ValueError("n_events must be > 0")
			if true_sigma <= 0:
				raise ValueError("sigma must be > 0")
			run_super_toy(
				n_toys=n_toys,
				n_events=n_events,
				true_mean=true_mean,
				true_sigma=true_sigma,
			)
		except Exception as exc:
			messagebox.showerror("Input/Run error", str(exc))

	btn_run = tk.Button(
		root,
		text="Run",
		command=on_run,
		bg="#2e7d32",
		fg="white",
		activebackground="#1b5e20",
		activeforeground="white",
		width=12,
	)
	btn_run.grid(row=6, column=0, **pad)

	btn_super = tk.Button(
		root,
		text="SuperToy",
		command=on_super_toy,
		bg="#1976d2",
		fg="white",
		activebackground="#0d47a1",
		activeforeground="white",
		width=12,
	)
	btn_super.grid(row=6, column=1, **pad)

	btn_exit = tk.Button(
		root,
		text="Exit",
		command=root.destroy,
		bg="#f62828",
		fg="white",
		activebackground="#ff0000",
		activeforeground="white",
		width=12,
	)
	btn_exit.grid(row=7, column=0, columnspan=2, **pad)

	root.mainloop()


if __name__ == "__main__":
	launch_gui()
