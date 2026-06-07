#!/usr/bin/env python3

import argparse
import csv
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Read CSV in current directory and plot Beam Momentum Setting vs Run Number."
	)
	parser.add_argument(
		"--file",
		type=Path,
		default=None,
		help="Optional CSV file path (default: first *.csv in current working directory)",
	)
	parser.add_argument(
		"--out",
		type=Path,
		default=Path("beam_momentum_vs_run.png"),
		help="Output plot image path",
	)
	parser.add_argument(
		"--hist-out",
		type=Path,
		default=Path("beam_momentum_hist.png"),
		help="Output histogram image path",
	)
	parser.add_argument(
		"--hist-bins",
		type=int,
		default=30,
		help="Number of bins for beam momentum histogram",
	)
	parser.add_argument(
		"--spills-out",
		type=Path,
		default=Path("total_spills_vs_momentum.png"),
		help="Output bar plot image path for total spills vs momentum",
	)
	parser.add_argument(
		"--runs-spills-out",
		type=Path,
		default=Path("runs_vs_total_spills_2d.png"),
		help="Output 2D plot image path for total spills vs momentum with linear fit",
	)
	parser.add_argument(
		"--runs-count-spills-out",
		type=Path,
		default=Path("total_spills_vs_run_count_2d.png"),
		help="Output 2D plot image path for total spills vs number of runs at each momentum",
	)
	parser.add_argument(
		"--no-show",
		action="store_true",
		help="Do not show plots interactively",
	)
	parser.add_argument(
		"--gui",
		action="store_true",
		help="Launch GUI with plot buttons (default behavior)",
	)
	parser.add_argument(
		"--cli",
		action="store_true",
		help="Run in CLI batch mode instead of GUI",
	)
	return parser.parse_args()


def find_csv_in_cwd() -> Path:
	files = sorted(Path.cwd().glob("*.csv"))
	if not files:
		raise FileNotFoundError("No CSV file found in current working directory.")
	return files[0]


def find_header_row(rows: list[list[str]]) -> int:
	for i, row in enumerate(rows):
		normalized = [cell.strip() for cell in row]
		if "Run Number" in normalized and "Beam Momentum Setting (MeV/c)" in normalized:
			return i
	raise ValueError("Could not find CSV header row with required columns.")


def read_points(csv_path: Path) -> tuple[list[float], list[float], list[float]]:
	with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
		all_rows = list(csv.reader(f))

	header_idx = find_header_row(all_rows)
	header = [cell.strip() for cell in all_rows[header_idx]]
	run_col = header.index("Run Number")
	mom_col = header.index("Beam Momentum Setting (MeV/c)")
	spills_col = header.index("# Spills")

	runs: list[float] = []
	momenta: list[float] = []
	spills: list[float] = []

	for row in all_rows[header_idx + 1 :]:
		if not row:
			continue
		run_raw = row[run_col].strip() if run_col < len(row) else ""
		mom_raw = row[mom_col].strip() if mom_col < len(row) else ""
		spills_raw = row[spills_col].strip() if spills_col < len(row) else ""
		if not run_raw or not mom_raw or not spills_raw:
			continue
		try:
			run_val = float(run_raw)
			mom_val = float(mom_raw)
			spills_val = float(spills_raw)
		except ValueError:
			continue
		runs.append(run_val)
		momenta.append(mom_val)
		spills.append(spills_val)

	if not runs:
		raise ValueError("No valid numeric points found for Run Number vs Beam Momentum Setting.")

	return runs, momenta, spills


def make_plot(runs: list[float], momenta: list[float], out_path: Path) -> None:
	plt.figure(figsize=(5, 5), dpi=120)
	plt.plot(runs, momenta, "o-", ms=4, lw=1.2, color="#5c9ead")
	plt.xlabel("Run Number")
	plt.ylabel("Beam Momentum Setting (MeV/c)")
	plt.title("Beam Momentum Setting vs Run Number")
	plt.grid(alpha=0.3)
	plt.tight_layout()
	plt.savefig(out_path)
	print(f"Saved plot: {out_path}")


def make_histogram(momenta: list[float], out_path: Path, bins: int) -> None:
	plt.figure(figsize=(5, 5), dpi=120)
	plt.hist(momenta, bins=bins, color="#a8d5e2", edgecolor="#5c9ead", alpha=0.9)
	plt.xlabel("Beam Momentum Setting (MeV/c)")
	plt.ylabel("Count")
	plt.title("Histogram of Beam Momentum Settings")
	plt.grid(alpha=0.25)
	plt.tight_layout()
	plt.savefig(out_path)
	print(f"Saved histogram: {out_path}")


def aggregate_by_momentum(momenta: list[float], spills: list[float]) -> tuple[list[float], list[int], list[float]]:
	run_counts_by_momentum: dict[float, int] = defaultdict(int)
	totals_by_momentum: dict[float, float] = defaultdict(float)
	for momentum, spill_count in zip(momenta, spills):
		run_counts_by_momentum[momentum] += 1
		totals_by_momentum[momentum] += spill_count

	sorted_momenta = sorted(totals_by_momentum)
	run_counts = [run_counts_by_momentum[m] for m in sorted_momenta]
	total_spills = [totals_by_momentum[m] for m in sorted_momenta]
	return sorted_momenta, run_counts, total_spills


def make_spills_bar_plot(momenta: list[float], spills: list[float], out_path: Path) -> None:
	sorted_momenta, _, total_spills = aggregate_by_momentum(momenta, spills)

	plt.figure(figsize=(5, 5), dpi=120)
	plt.bar(sorted_momenta, total_spills, width=8.0, color="#b8c0a4", edgecolor="#7c8a68", alpha=0.9)
	plt.xlabel("Beam Momentum Setting (MeV/c)")
	plt.ylabel("Total # Spills")
	plt.title("Total Spills vs Beam Momentum Setting")
	plt.grid(axis="y", alpha=0.25)
	plt.tight_layout()
	plt.savefig(out_path)
	print(f"Saved spills bar plot: {out_path}")


def make_runs_vs_spills_2d_plot(momenta: list[float], spills: list[float], out_path: Path) -> None:
	sorted_momenta, _, total_spills = aggregate_by_momentum(momenta, spills)

	x = np.array(sorted_momenta, dtype=float)
	y = np.array(total_spills, dtype=float)
	m, b = np.polyfit(x, y, deg=1)
	rho = float(np.corrcoef(x, y)[0, 1])
	x_fit = np.linspace(float(np.min(x)), float(np.max(x)), 200)
	y_fit = m * x_fit + b

	plt.figure(figsize=(5, 5), dpi=120)
	plt.scatter(x, y, s=80, color="#9cc7d8", alpha=0.95, label="Momentum totals")
	plt.plot(x_fit, y_fit, color="#7fb3c8", lw=2.0, label="Linear fit")
	plt.xlabel("Beam Momentum Setting (MeV/c)")
	plt.ylabel("Total # Spills")
	plt.title("2D: Total Spills vs Momentum")
	plt.grid(alpha=0.25)
	plt.legend(loc="best")
	plt.text(
		0.04,
		0.96,
		f"y = {m:.2f}x + {b:.1f}\n$\\rho$ = {rho:.3f}",
		transform=plt.gca().transAxes,
		va="top",
		ha="left",
		bbox={"boxstyle": "round", "facecolor": "#fffaf0", "alpha": 0.9},
	)
	plt.tight_layout()
	plt.savefig(out_path)
	print(f"Saved 2D spills-vs-momentum plot with linear fit: {out_path}")


def make_spills_vs_run_count_2d_plot(momenta: list[float], spills: list[float], out_path: Path) -> None:
	sorted_momenta, run_counts, total_spills = aggregate_by_momentum(momenta, spills)
	x = np.array(run_counts, dtype=float)
	y = np.array(total_spills, dtype=float)
	m, b = np.polyfit(x, y, deg=1)
	rho = float(np.corrcoef(x, y)[0, 1])
	x_fit = np.linspace(float(np.min(x)), float(np.max(x)), 200)
	y_fit = m * x_fit + b

	plt.figure(figsize=(5, 5), dpi=120)
	plt.scatter(x, y, s=80, color="#a8d8b9", alpha=0.95, label="Momentum totals")
	plt.plot(x_fit, y_fit, color="#7fba96", lw=2.0, label="Linear fit")
	for x_point, y_point, mom in zip(x, y, sorted_momenta):
		plt.annotate(f"{mom:.0f}", (x_point, y_point), textcoords="offset points", xytext=(4, 4), fontsize=8)
	plt.xlabel("Number of Runs at Momentum")
	plt.ylabel("Total # Spills")
	plt.title("2D: Total Spills vs Number of Runs")
	plt.grid(alpha=0.25)
	plt.legend(loc="best")
	plt.text(
		0.04,
		0.96,
		f"y = {m:.2f}x + {b:.1f}\n$\\rho$ = {rho:.3f}",
		transform=plt.gca().transAxes,
		va="top",
		ha="left",
		bbox={"boxstyle": "round", "facecolor": "#fffaf0", "alpha": 0.9},
	)
	plt.tight_layout()
	plt.savefig(out_path)
	print(f"Saved 2D spills-vs-run-count plot with linear fit: {out_path}")


def launch_gui(
	runs: list[float],
	momenta: list[float],
	spills: list[float],
	out_path: Path,
	hist_out_path: Path,
	hist_bins: int,
	spills_out_path: Path,
	runs_spills_out_path: Path,
	runs_count_spills_out_path: Path,
) -> None:
	root = tk.Tk()
	root.title("CSV Plot Controls")
	root.resizable(False, False)

	frame = ttk.Frame(root, padding=12)
	frame.grid(row=0, column=0, sticky="nsew")

	status = tk.StringVar(value="Choose a plot button.")

	def show_nonblocking() -> None:
		plt.show(block=False)
		plt.pause(0.001)

	def plot_run_vs_momentum() -> None:
		make_plot(runs, momenta, out_path)
		show_nonblocking()
		status.set(f"Created {out_path.name}")

	def plot_histogram() -> None:
		make_histogram(momenta, hist_out_path, hist_bins)
		show_nonblocking()
		status.set(f"Created {hist_out_path.name}")

	def plot_spills_bar() -> None:
		make_spills_bar_plot(momenta, spills, spills_out_path)
		show_nonblocking()
		status.set(f"Created {spills_out_path.name}")

	def plot_runs_vs_spills_2d() -> None:
		make_runs_vs_spills_2d_plot(momenta, spills, runs_spills_out_path)
		show_nonblocking()
		status.set(f"Created {runs_spills_out_path.name}")

	def plot_spills_vs_run_count_2d() -> None:
		make_spills_vs_run_count_2d_plot(momenta, spills, runs_count_spills_out_path)
		show_nonblocking()
		status.set(f"Created {runs_count_spills_out_path.name}")

	def exit_all() -> None:
		plt.close("all")
		root.quit()
		root.destroy()

	root.protocol("WM_DELETE_WINDOW", exit_all)

	ttk.Label(frame, text="Plot Actions", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
	ttk.Button(frame, text="Run vs Momentum", command=plot_run_vs_momentum).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=3)
	ttk.Button(frame, text="Momentum Histogram", command=plot_histogram).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=3)
	ttk.Button(frame, text="Total Spills Bar", command=plot_spills_bar).grid(row=2, column=0, sticky="ew", padx=(0, 4), pady=3)
	ttk.Button(frame, text="2D Spills vs Momentum", command=plot_runs_vs_spills_2d).grid(row=2, column=1, sticky="ew", padx=(4, 0), pady=3)
	ttk.Button(frame, text="2D Spills vs Run Count", command=plot_spills_vs_run_count_2d).grid(row=3, column=0, columnspan=2, sticky="ew", pady=3)

	tk.Button(
		frame,
		text="Exit",
		command=exit_all,
		bg="#d98c8c",
		fg="white",
		activebackground="#c97f7f",
		activeforeground="white",
		relief="raised",
	).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 4))

	ttk.Label(frame, textvariable=status, wraplength=340, justify="left").grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, 0))

	root.mainloop()


def main() -> None:
	args = parse_args()
	csv_path = args.file if args.file is not None else find_csv_in_cwd()
	runs, momenta, spills = read_points(csv_path)
	if not args.cli:
		launch_gui(
			runs,
			momenta,
			spills,
			out_path=args.out,
			hist_out_path=args.hist_out,
			hist_bins=args.hist_bins,
			spills_out_path=args.spills_out,
			runs_spills_out_path=args.runs_spills_out,
			runs_count_spills_out_path=args.runs_count_spills_out,
		)
		return

	show = not args.no_show
	make_plot(runs, momenta, args.out)
	make_histogram(momenta, args.hist_out, args.hist_bins)
	make_spills_bar_plot(momenta, spills, args.spills_out)
	make_runs_vs_spills_2d_plot(momenta, spills, args.runs_spills_out)
	make_spills_vs_run_count_2d_plot(momenta, spills, args.runs_count_spills_out)
	if show:
		plt.show()
	plt.close("all")


if __name__ == "__main__":
	main()
