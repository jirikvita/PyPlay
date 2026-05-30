#!/usr/bin/env python3

import argparse
import json
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import onnx
import onnxruntime as ort
from onnx.reference import ReferenceEvaluator

from readTools import ReadData


DEFAULT_RESULTS_DIR = Path(
    "results_n1_80_n2_80_i1_0_i2_4000_train_31_32_33_nImgs_4000_rate_0.005"
)


def parse_setup_tag_for_range(setup_tag):
    i1 = None
    i2 = None
    nimgs = None

    m_i = re.search(r"_i1_(\d+)_i2_(\d+)_", setup_tag)
    if m_i:
        i1 = int(m_i.group(1))
        i2 = int(m_i.group(2))

    m_n = re.search(r"_nImgs_(\d+)_", setup_tag)
    if m_n:
        nimgs = int(m_n.group(1))

    return i1, i2, nimgs


def resolve_artifacts(results_dir):
    meta_files = sorted(results_dir.glob("model_meta*.json"))
    onnx_files = sorted(results_dir.glob("model*.onnx"))

    if not meta_files:
        raise FileNotFoundError(f"No model_meta*.json found in {results_dir}")
    if not onnx_files:
        raise FileNotFoundError(f"No model*.onnx found in {results_dir}")

    # In this project each results folder should contain a single model pair.
    return meta_files[0], onnx_files[0]


def resolve_artifacts_from_inputs(results_dir, meta_file=None, onnx_file=None):
    if meta_file is not None and onnx_file is not None:
        meta_path = Path(meta_file)
        onnx_path = Path(onnx_file)
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file does not exist: {meta_path}")
        if not onnx_path.exists():
            raise FileNotFoundError(f"ONNX file does not exist: {onnx_path}")
        return meta_path, onnx_path
    return resolve_artifacts(results_dir)


def class_value_map(hexcodes):
    nnoutmax = 1.0
    nnoutmin = 0.0
    delta = 0.1
    nhex = len(hexcodes)
    sep = (nnoutmax - nnoutmin) / nhex

    value_to_hex = {}
    for ihex, hexcode in enumerate(hexcodes):
        class_value = nnoutmin + ihex * sep + delta
        value_to_hex[class_value] = hexcode
    return value_to_hex


def class_value_map_with_params(hexcodes, nnoutmin, nnoutmax, delta):
    nhex = len(hexcodes)
    sep = (nnoutmax - nnoutmin) / nhex
    value_to_hex = {}
    for ihex, hexcode in enumerate(hexcodes):
        class_value = nnoutmin + ihex * sep + delta
        value_to_hex[class_value] = hexcode
    return value_to_hex


def _onnx_props_dict(model):
    props = {}
    for p in model.metadata_props:
        props[p.key] = p.value
    return props


def _meta_float(props, fallback_meta, key, default):
    if key in props:
        try:
            return float(props[key])
        except ValueError:
            pass
    try:
        return float(fallback_meta.get(key, default))
    except Exception:
        return float(default)


def _meta_int(props, fallback_meta, key, default):
    if key in props:
        try:
            return int(props[key])
        except ValueError:
            pass
    try:
        return int(fallback_meta.get(key, default))
    except Exception:
        return int(default)


def nearest_hex(value_to_hex, value):
    return min(value_to_hex.items(), key=lambda kv: abs(kv[0] - value))[1]


def run_inference_in_batches(run_batch_fn, x, batch_size):
    preds = []
    n = len(x)
    for ibeg in range(0, n, batch_size):
        iend = min(ibeg + batch_size, n)
        batch = x[ibeg:iend]
        y = run_batch_fn(batch)
        preds.append(np.asarray(y).reshape(-1))
    return np.concatenate(preds, axis=0)


def plot_outputs_split_by_class(results_dir, setup_tag, hexcodes, pred_by_class):
    plt.figure()
    bins = np.linspace(0.0, 1.0, 101)

    for hexcode in hexcodes:
        vals = np.asarray(pred_by_class.get(hexcode, []), dtype=np.float32)
        if vals.size == 0:
            continue
        plt.hist(
            vals,
            bins=bins,
            alpha=0.35,
            edgecolor="black",
            linewidth=0.5,
            label=f"class {hexcode} (n={vals.size})",
        )

    plt.title("onnx_test_results_split")
    plt.xlabel("NN output")
    plt.ylabel("Count")
    plt.xlim(0.0, 1.0)
    plt.legend()

    base = f"onnx_test_results_split_{setup_tag.strip('_')}" if setup_tag else "onnx_test_results_split"
    png_path = results_dir / f"{base}.png"
    pdf_path = results_dir / f"{base}.pdf"
    plt.tight_layout()
    plt.savefig(png_path)
    plt.savefig(pdf_path)
    plt.close()
    return png_path, pdf_path


def run_onnx_on_same_dataset(
    results_dir,
    data_path=None,
    i1=None,
    i2=None,
    batch_size=512,
    correct_cut=0.10,
    meta_file=None,
    onnx_file=None,
    n_details=100,
    make_plots=True,
):
    results_dir = Path(results_dir)
    if not results_dir.exists():
        raise FileNotFoundError(f"Results directory does not exist: {results_dir}")

    meta_file, onnx_file = resolve_artifacts_from_inputs(results_dir, meta_file, onnx_file)
    with meta_file.open("r") as f:
        meta = json.load(f)

    onnx_model = onnx.load(str(onnx_file))
    onnx_props = _onnx_props_dict(onnx_model)

    hexcodes = list(meta["hexcodes"])
    cutoffx = _meta_int(onnx_props, meta, "cutoffx", 16)
    cutoffy = _meta_int(onnx_props, meta, "cutoffy", 20)
    rebinx = _meta_int(onnx_props, meta, "rebinx", 2)
    rebiny = _meta_int(onnx_props, meta, "rebiny", 2)
    base_dimx = _meta_int(onnx_props, meta, "baseDimx", 32)
    preprocess_thr = _meta_float(onnx_props, meta, "preprocessThr", 0.5)
    label_nnoutmin = _meta_float(onnx_props, meta, "labelNnoutmin", 0.0)
    label_nnoutmax = _meta_float(onnx_props, meta, "labelNnoutmax", 1.0)
    label_delta = _meta_float(onnx_props, meta, "labelDelta", 0.1)
    n0 = int(meta["n0"])
    data_path = data_path if data_path else str(meta.get("dataPath", "data/by_class"))
    setup_tag = str(meta.get("setupTag", ""))

    parsed_i1, parsed_i2, parsed_nimgs = parse_setup_tag_for_range(setup_tag)
    i1 = i1 if i1 is not None else parsed_i1
    i2 = i2 if i2 is not None else parsed_i2
    if i1 is None:
        i1 = 0
    if i2 is None:
        i2 = i1 + (parsed_nimgs if parsed_nimgs is not None else 4000)

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")
    if i2 <= i1:
        raise ValueError(f"Expected i2 > i1, got i1={i1}, i2={i2}")

    print(f"Using results dir: {results_dir}")
    print(f"Using ONNX model: {onnx_file}")
    print(f"Using metadata: {meta_file}")
    print(f"Dataset path: {data_path}")
    print(f"Reading classes: {hexcodes}")
    print(f"Image range: [{i1}, {i2})")
    print(f"Preprocess: cutoff=({cutoffx},{cutoffy}) rebin=({rebinx},{rebiny}) thr={preprocess_thr}")

    inputs, outputs = ReadData(
        hexcodes,
        i1,
        i2,
        cutoffx,
        cutoffy,
        rebinx,
        rebiny,
        base_dimx,
        toTrain=False,
        nExampleCharsToPrint=0,
        dataPath=data_path,
        thr=preprocess_thr,
    )

    x = np.asarray(inputs, dtype=np.float32)
    y_true = np.asarray(outputs, dtype=np.float32).reshape(-1)

    if x.size == 0:
        raise RuntimeError("No input images were loaded. Check data_path and index range.")
    if x.shape[1] != n0:
        raise RuntimeError(
            f"Input feature dimension mismatch: got {x.shape[1]}, expected {n0}"
        )

    providers = ["CPUExecutionProvider"]
    run_batch = None
    input_name = None
    output_name = None
    engine = None
    try:
        session = ort.InferenceSession(str(onnx_file), providers=providers)
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name

        print(
            f"ONNXRuntime input: {input_name}, shape={session.get_inputs()[0].shape}"
        )
        print(
            f"ONNXRuntime output: {output_name}, shape={session.get_outputs()[0].shape}"
        )

        def run_batch(batch):
            return session.run([output_name], {input_name: batch})[0]

        engine = "onnxruntime"

    except Exception as ex:
        print(f"WARNING: ONNXRuntime failed, falling back to ReferenceEvaluator: {ex}")
        model = onnx_model
        ref = ReferenceEvaluator(model)
        input_name = model.graph.input[0].name
        output_name = model.graph.output[0].name
        print(f"ReferenceEvaluator input: {input_name}")
        print(f"ReferenceEvaluator output: {output_name}")

        def run_batch(batch):
            return ref.run([output_name], {input_name: batch})[0]

        engine = "onnx-reference"

    print(f"Running inference on {len(x)} samples...")
    y_pred = run_inference_in_batches(run_batch, x, batch_size=batch_size)

    if y_pred.shape[0] != y_true.shape[0]:
        raise RuntimeError(
            f"Prediction count mismatch: got {y_pred.shape[0]}, expected {y_true.shape[0]}"
        )

    value_to_hex = class_value_map_with_params(
        hexcodes,
        nnoutmin=label_nnoutmin,
        nnoutmax=label_nnoutmax,
        delta=label_delta,
    )
    all_count = {}
    correct_count = {}
    pred_by_class = {}
    n_all = 0
    n_correct = 0

    for y_t, y_p in zip(y_true, y_pred):
        key = nearest_hex(value_to_hex, float(y_t))
        all_count[key] = all_count.get(key, 0) + 1
        if key not in pred_by_class:
            pred_by_class[key] = []
        pred_by_class[key].append(float(y_p))
        n_all += 1
        if abs(float(y_t) - float(y_p)) < correct_cut:
            correct_count[key] = correct_count.get(key, 0) + 1
            n_correct += 1

    print("Per-class accuracy:")
    per_class_accuracy = {}
    for hexcode in hexcodes:
        n_cls = all_count.get(hexcode, 0)
        n_ok = correct_count.get(hexcode, 0)
        acc = (float(n_ok) / n_cls) if n_cls else 0.0
        per_class_accuracy[hexcode] = acc
        print(f"  class {hexcode}: {n_ok}/{n_cls} = {acc:.4f}")

    total_acc = (float(n_correct) / n_all) if n_all else 0.0
    mse = float(np.mean((y_pred - y_true) ** 2))
    print(f"Total accuracy: {n_correct}/{n_all} = {total_acc:.4f}")
    print(f"MSE(y_pred, y_true): {mse:.6f}")

    # Save per-event ONNX predictions for the first n_details events in each class.
    details_rows = []
    details_count = {hexcode: 0 for hexcode in hexcodes}
    for i, (y_t, y_p) in enumerate(zip(y_true, y_pred)):
        key = nearest_hex(value_to_hex, float(y_t))
        if details_count[key] >= n_details:
            continue
        details_rows.append([
            i1 + i,
            key,
            float(y_t),
            float(y_p),
            float(y_t - y_p),
        ])
        details_count[key] = details_count[key] + 1

    details_csv = results_dir / f"onnx_event_details_N{n_details}{setup_tag}.csv"
    with details_csv.open("w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow([
            "event_abs_i",
            "true_hex_class",
            "target_value",
            "onnx_output",
            "diff_target_minus_output",
        ])
        writer.writerows(details_rows)
    print(f"Saved ONNX event details: {details_csv}")

    png_path = None
    pdf_path = None
    if make_plots:
        png_path, pdf_path = plot_outputs_split_by_class(
            results_dir, setup_tag, hexcodes, pred_by_class
        )
        print(f"Saved split-by-class output histogram: {png_path}")
        print(f"Saved split-by-class output histogram: {pdf_path}")
    else:
        print("Plotting disabled: skipping ONNX histogram outputs.")

    return {
        "engine": engine,
        "n_all": n_all,
        "n_correct": n_correct,
        "total_accuracy": total_acc,
        "mse": mse,
        "per_class_accuracy": per_class_accuracy,
        "details_csv": str(details_csv),
        "plot_png": str(png_path),
        "plot_pdf": str(pdf_path),
        "setup_tag": setup_tag,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run an exported ONNX model on the same dataset used in training."
    )
    parser.add_argument(
        "--results-dir",
        default=str(DEFAULT_RESULTS_DIR),
        help="Directory that contains model_meta*.json and model*.onnx",
    )
    parser.add_argument("--data-path", default=None, help="Override dataset path")
    parser.add_argument("--i1", type=int, default=None, help="Start image index (inclusive)")
    parser.add_argument("--i2", type=int, default=None, help="End image index (exclusive)")
    parser.add_argument(
        "--batch-size", type=int, default=512, help="ONNX inference batch size"
    )
    parser.add_argument(
        "--correct-cut",
        type=float,
        default=0.10,
        help="Absolute error threshold for a correct class decision",
    )
    parser.add_argument(
        "--n-details",
        type=int,
        default=100,
        help="How many events per class to save into ONNX details CSV",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable creation of ONNX histogram plots",
    )
    args = parser.parse_args()

    run_onnx_on_same_dataset(
        results_dir=args.results_dir,
        data_path=args.data_path,
        i1=args.i1,
        i2=args.i2,
        batch_size=args.batch_size,
        correct_cut=args.correct_cut,
        n_details=args.n_details,
        make_plots=(not args.no_plots),
    )


if __name__ == "__main__":
    main()
