#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_RESULTS_DIR = Path(
    "results_n1_80_n2_80_i1_0_i2_3000_train_31_32_33_nImgs_3000_iters_45_bs_32_rate_0.005"
)


def _find_single_csv(results_dir, pattern):
    files = sorted(results_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in {results_dir}")
    if len(files) > 1:
        raise RuntimeError(
            f"Expected one file matching '{pattern}', found {len(files)}: {files}"
        )
    return files[0]


def _read_csv_rows(path):
    with path.open("r", newline="") as handle:
        return list(csv.DictReader(handle))


def _key_from_row(row):
    return (int(row["event_abs_i"]), row["true_hex_class"])


def build_xy(train_csv, onnx_csv):
    train_rows = _read_csv_rows(train_csv)
    onnx_rows = _read_csv_rows(onnx_csv)

    onnx_map = {}
    for row in onnx_rows:
        onnx_map[_key_from_row(row)] = float(row["onnx_output"])

    x_vals = []
    y_vals = []
    missing = 0
    for row in train_rows:
        key = _key_from_row(row)
        if key not in onnx_map:
            missing += 1
            continue
        x_vals.append(float(row["classifier_output"]))
        y_vals.append(onnx_map[key])

    if not x_vals:
        raise RuntimeError("No matched events found between train and ONNX CSV files")

    return np.asarray(x_vals, dtype=np.float64), np.asarray(y_vals, dtype=np.float64), missing


def make_plot(x_vals, y_vals, out_png, out_pdf, title):
    plt.figure(figsize=(7, 7))
    plt.scatter(x_vals, y_vals, s=20, alpha=0.7, edgecolors="none")

    axis_min = float(min(np.min(x_vals), np.min(y_vals)))
    axis_max = float(max(np.max(x_vals), np.max(y_vals)))
    plt.plot([axis_min, axis_max], [axis_min, axis_max], "k--", linewidth=1.0, label="y = x")

    plt.xlabel("Asimov/train classifier_output")
    plt.ylabel("ONNX output")
    plt.title(title)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.savefig(out_pdf)


def plot_train_vs_onnx_scatter(
    results_dir,
    train_csv=None,
    onnx_csv=None,
    out_prefix="train_vs_onnx_scatter",
    show=False,
):
    results_dir = Path(results_dir)
    if not results_dir.exists():
        raise FileNotFoundError(f"Results directory does not exist: {results_dir}")

    train_csv = Path(train_csv) if train_csv else _find_single_csv(results_dir, "train_event_details_N*.csv")
    onnx_csv = Path(onnx_csv) if onnx_csv else _find_single_csv(results_dir, "onnx_event_details_N*.csv")

    x_vals, y_vals, missing = build_xy(train_csv, onnx_csv)

    out_png = results_dir / f"{out_prefix}.png"
    out_pdf = results_dir / f"{out_prefix}.pdf"
    title = f"ONNX vs Asimov(train) outputs (matched events: {len(x_vals)})"
    make_plot(x_vals, y_vals, out_png, out_pdf, title)

    print(f"Train CSV: {train_csv}")
    print(f"ONNX CSV: {onnx_csv}")
    print(f"Matched events: {len(x_vals)}")
    print(f"Missing train events in ONNX CSV: {missing}")
    print(f"Saved scatter plot: {out_png}")
    print(f"Saved scatter plot: {out_pdf}")

    if show:
        plt.show()
    else:
        plt.close()

    return {
        "train_csv": str(train_csv),
        "onnx_csv": str(onnx_csv),
        "matched": int(len(x_vals)),
        "missing": int(missing),
        "out_png": str(out_png),
        "out_pdf": str(out_pdf),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Plot ONNX output (y) vs train/Asimov classifier_output (x) from detail CSV files."
    )
    parser.add_argument(
        "--results-dir",
        default=str(DEFAULT_RESULTS_DIR),
        help="Directory containing train_event_details*.csv and onnx_event_details*.csv",
    )
    parser.add_argument("--train-csv", default=None, help="Optional explicit train details CSV")
    parser.add_argument("--onnx-csv", default=None, help="Optional explicit ONNX details CSV")
    parser.add_argument(
        "--out-prefix",
        default="train_vs_onnx_scatter",
        help="Output file prefix (without extension)",
    )
    parser.set_defaults(show=False)
    parser.add_argument(
        "--show",
        dest="show",
        action="store_true",
        help="Show plot interactively (default: save only)",
    )
    parser.add_argument(
        "--no-show",
        dest="show",
        action="store_false",
        help="Do not show plot interactively",
    )
    args = parser.parse_args()

    plot_train_vs_onnx_scatter(
        results_dir=args.results_dir,
        train_csv=args.train_csv,
        onnx_csv=args.onnx_csv,
        out_prefix=args.out_prefix,
        show=args.show,
    )


if __name__ == "__main__":
    main()
