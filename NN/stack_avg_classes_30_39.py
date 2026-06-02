#!/usr/bin/python3

import argparse
from itertools import islice
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from readTools import Rebin2DRGBArray

# jk: https://petercbsmith.github.io/color-tutorial.html

def parse_args():
    parser = argparse.ArgumentParser(
        description="Stack images in classes 30..39 and save average PNG per class."
    )
    parser.add_argument(
        "--datapath",
        default="data/by_class",
        help="Path to by_class dataset root (default: data/by_class)",
    )
    parser.add_argument(
        "--outdir",
        default="stacked_avg_30_39",
        help="Output directory for averaged PNGs",
    )
    parser.add_argument(
        "--rebinx",
        type=int,
        default=-1,
        help="Rebin factor in x (<=0 disables rebin)",
    )
    parser.add_argument(
        "--rebiny",
        type=int,
        default=-1,
        help="Rebin factor in y (<=0 disables rebin)",
    )
    parser.add_argument(
        "--cutoffx",
        type=int,
        default=16,
        help="Crop cutoff in x on each side (default: 16)",
    )
    parser.add_argument(
        "--cutoffy",
        type=int,
        default=20,
        help="Crop cutoff in y on each side (default: 20)",
    )
    parser.add_argument(
        "--nimgs",
        type=int,
        default=500,
        help="Number of images to stack per class (default: 500, <=0 means all)",
    )
    parser.add_argument(
        "--plotlog",
        dest="plotlog",
        action="store_true",
        default=True,
        help="Plot and save log-transformed stacked data (default: enabled)",
    )
    parser.add_argument(
        "--no-plotlog",
        dest="plotlog",
        action="store_false",
        help="Disable plotting/saving log-transformed stacked data",
    )
    return parser.parse_args()


def class_codes_30_39():
    return [f"{v:02x}" for v in range(0x30, 0x3A)]


def class_codes_A_Z():
    return [f"{v:02x}" for v in range(0x41, 0x5B)]


def load_and_optionally_rebin_and_crop(png_path, rebinx, rebiny, cutoffx, cutoffy):
    arr = np.asarray(Image.open(png_path), dtype=np.float32)
    if rebinx > 0 and rebiny > 0:
        arr = Rebin2DRGBArray(arr, rebinx=rebinx, rebiny=rebiny, doAver=True)

    n_lines = arr.shape[0]
    n_cols = arr.shape[1]
    arr = arr[cutoffy:n_lines-cutoffy, cutoffx:n_cols-cutoffx]

    return arr


def save_average_png(avg_arr, out_path):
    avg_arr = np.clip(avg_arr, 0.0, 255.0).astype(np.uint8)
    Image.fromarray(avg_arr).save(out_path)


def save_log_plot(avg_arr, out_path_base, class_code):
    arr = np.asarray(avg_arr, dtype=np.float64)
    if arr.ndim == 3:
        # Collapse RGB to a single intensity map for stable log plotting.
        arr = arr.mean(axis=2)

    log_arr = np.log1p(np.clip(arr, 0.0, None))
    fig = plt.figure(facecolor="black")
    ax = fig.add_subplot(111)
    ax.set_facecolor("black")
    # Use inverted blackbody-like palette.
    ax.imshow(log_arr, cmap="afmhot_r")
    ax.set_title(f"Log stacked average class {class_code}", color="white")
    ax.set_xlabel("x", color="white")
    ax.set_ylabel("y", color="white")
    ax.tick_params(colors="white")
    plt.savefig(f"{out_path_base}.png")
    plt.savefig(f"{out_path_base}.pdf")
    plt.close()


def compute_class_average(code, data_root, args):
    class_dir = data_root / code / f"train_{code}"
    if not class_dir.exists():
        print(f"WARNING: class dir missing, skipping: {class_dir}")
        return None, 0

    png_iter = class_dir.glob("*.png")
    if args.nimgs > 0:
        png_iter = islice(png_iter, args.nimgs)

    sum_img = None
    n_imgs = 0
    for png_path in png_iter:
        arr = load_and_optionally_rebin_and_crop(
            png_path,
            args.rebinx,
            args.rebiny,
            args.cutoffx,
            args.cutoffy,
        )
        if arr.size == 0:
            print(f"WARNING: skipping fully cropped image {png_path.name}")
            continue
        if sum_img is None:
            sum_img = np.zeros_like(arr, dtype=np.float64)
        if arr.shape != sum_img.shape:
            print(
                f"WARNING: skipping shape-mismatched image {png_path.name} "
                f"with shape {arr.shape}, expected {sum_img.shape}"
            )
            continue
        sum_img += arr
        n_imgs += 1

    if n_imgs == 0:
        return None, 0
    return (sum_img / float(n_imgs)), n_imgs


def save_alnum_grid(averages_by_code, out_path_base):
    codes = class_codes_30_39() + class_codes_A_Z()
    ncols = 8
    nrows = 5
    fig, axes = plt.subplots(nrows, ncols, figsize=(2.5 * ncols, 2.5 * nrows), facecolor="black")
    axes = axes.flatten()

    last_im = None
    for i, code in enumerate(codes):
        ax = axes[i]
        ax.set_facecolor("black")
        arr = averages_by_code.get(code)
        label = chr(int(code, 16))
        if arr is None:
            ax.set_axis_off()
            ax.set_title(f"{label} ({code})\nmissing", fontsize=9, color="white")
            continue

        if arr.ndim == 3:
            arr = arr.mean(axis=2)
        log_arr = np.log1p(np.clip(arr, 0.0, None))
        last_im = ax.imshow(log_arr, cmap="afmhot_r")
        ax.set_title(f"{label} ({code})", fontsize=9, color="white")
        ax.set_xticks([])
        ax.set_yticks([])

    for j in range(len(codes), len(axes)):
        axes[j].set_axis_off()

    fig.suptitle("0-9 and A-Z stacked averages (log scale)", color="white")
    fig.tight_layout()
    fig.savefig(f"{out_path_base}.png")
    fig.savefig(f"{out_path_base}.pdf")
    plt.close(fig)


def main():
    args = parse_args()

    data_root = Path(args.datapath)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data_root.exists():
        print(f"ERROR: dataset root does not exist: {data_root}")
        return 1

    codes = class_codes_30_39()
    az_codes = class_codes_A_Z()
    print(f"Will process classes: {codes}")
    print(f"Will also process A-Z classes: {az_codes}")
    print(f"Rebin settings: rebinx={args.rebinx}, rebiny={args.rebiny}")
    print(f"Crop settings: cutoffx={args.cutoffx}, cutoffy={args.cutoffy}")
    print(f"Max images per class: {args.nimgs if args.nimgs > 0 else 'all'}")
    print(f"Log plotting enabled: {args.plotlog}")

    n_done = 0
    digit_averages = {}
    for code in codes:
        avg_img, n_imgs = compute_class_average(code, data_root, args)
        if avg_img is None:
            print(f"WARNING: no images found/compatible for class {code}, skipping")
            digit_averages[code] = None
            continue

        digit_averages[code] = avg_img

        rebin_tag = f"_rbx{args.rebinx}_rby{args.rebiny}" if args.rebinx > 0 and args.rebiny > 0 else ""
        crop_tag = f"_cx{args.cutoffx}_cy{args.cutoffy}"
        out_png = out_dir / f"stacked_avg_class_{code}{rebin_tag}{crop_tag}.png"
        save_average_png(avg_img, out_png)

        if args.plotlog:
            log_base = out_dir / f"stacked_avg_class_{code}{rebin_tag}{crop_tag}_log"
            save_log_plot(avg_img, log_base, code)

        print(f"Saved {out_png} from {n_imgs} images")
        n_done += 1

    az_averages = {}
    az_done = 0
    for code in az_codes:
        avg_img, n_imgs = compute_class_average(code, data_root, args)
        if avg_img is None:
            print(f"WARNING: no images found/compatible for A-Z class {code}, skipping")
            az_averages[code] = None
            continue
        az_averages[code] = avg_img
        az_done += 1

    rebin_tag = f"_rbx{args.rebinx}_rby{args.rebiny}" if args.rebinx > 0 and args.rebiny > 0 else ""
    crop_tag = f"_cx{args.cutoffx}_cy{args.cutoffy}"
    alnum_averages = {}
    alnum_averages.update(digit_averages)
    alnum_averages.update(az_averages)
    alnum_grid_base = out_dir / f"stacked_avg_0_9_A_Z_grid{rebin_tag}{crop_tag}"
    save_alnum_grid(alnum_averages, alnum_grid_base)
    print(f"Saved 0-9 + A-Z grid plot to {alnum_grid_base}.png/.pdf")

    print(f"Done. Produced {n_done} averaged digit class images and {az_done} A-Z averages in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
