#!/usr/bin/python3
# jiri kvita
# Keras/TensorFlow rewrite of nnRun_Chars.py

import os
import sys
import gc
import subprocess
from pathlib import Path
import shutil
import json
import csv

import numpy as np
import matplotlib.pyplot as plt

from argvTools import parse_argv
from readTools import ReadData
from printAndPlotTools import PrintUnique, PlotCost, PlotDataAsHisto, PlotIndivDataAsHisto


def save_keras_model(model, setup_tag, model_meta):
	model_file = Path(f"model{setup_tag}.keras")
	model.save(model_file)

	meta_file = Path(f"model_meta{setup_tag}.json")
	with meta_file.open("w") as out:
		json.dump(model_meta, out, indent=2, sort_keys=True)

	print(f"Saved Keras model to {model_file}")
	print(f"Saved model metadata to {meta_file}")
	return model_file, meta_file


def save_keras_onnx_model(model, setup_tag, input_dim, opset=11):
	try:
		import tensorflow as tf
		import tf2onnx
	except Exception as ex:
		print(f"WARNING: ONNX export skipped (missing TensorFlow/tf2onnx): {ex}")
		print("Hint: pip install tf2onnx")
		return None

	onnx_file = Path(f"model{setup_tag}.onnx")
	input_signature = [tf.TensorSpec([None, input_dim], tf.float32, name="input")]
	try:
		tf2onnx.convert.from_keras(
			model,
			input_signature=input_signature,
			opset=opset,
			output_path=str(onnx_file),
		)
		print(f"Saved ONNX model to {onnx_file}")
		return onnx_file
	except Exception as ex:
		print(f"WARNING: ONNX export failed: {ex}")
		return None


def build_model(input_dim, n1, n2, learning_rate, use_relu=True):
	# Delayed import so the script can still print a clear message if TF is missing.
	import tensorflow as tf

	activation = "relu" if use_relu else "sigmoid"
	model = tf.keras.Sequential(
		[
			tf.keras.layers.Input(shape=(input_dim,)),
			tf.keras.layers.Dense(n1, activation=activation, name="dense_1"),
			tf.keras.layers.Dense(n2, activation=activation, name="dense_2"),
			tf.keras.layers.Dense(1, activation="sigmoid", name="dense_out"),
		]
	)
	model.compile(
		optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
		# The legacy script used a chi2-like objective; MSE is the closest standard Keras loss.
		loss="mse",
	)
	return model


def plot_dense_weights(model, setup_tag, suffix="post"):
	dense_layers = [layer for layer in model.layers if hasattr(layer, "get_weights")]
	for ilayer, layer in enumerate(dense_layers):
		w_and_b = layer.get_weights()
		if not w_and_b:
			continue
		w = w_and_b[0]
		fig = plt.figure(figsize=(0.5 + 0.1 * w.shape[1], 0.5 + 0.02 * w.shape[0]))
		ax = fig.add_subplot(111)
		ax.set_title(f"weights_{layer.name}")
		plt.imshow(w.T)
		ax.set_aspect("auto")
		plt.colorbar(orientation="vertical")
		plt.savefig(f"ws_tf_{ilayer}_{suffix}{setup_tag}.png")
		plt.savefig(f"ws_tf_{ilayer}_{suffix}{setup_tag}.pdf")
		plt.close(fig)


def evaluate_subset(subset_name, subset_inputs, subset_outputs, subset_pred, hexcodes, value_to_hex, correct_cut):
	subset_results = []
	subset_results_dict = {}
	n_all = 0
	n_correct = 0
	n_all_dict = {}
	n_correct_dict = {}

	for i in range(len(subset_inputs)):
		diff = subset_outputs[i] - subset_pred[i]
		n_all += 1
		key = min(value_to_hex.items(), key=lambda kv: abs(kv[0] - subset_outputs[i]))[1]
		if key not in n_all_dict:
			n_all_dict[key] = 1
			n_correct_dict[key] = 0
		else:
			n_all_dict[key] += 1

		if key not in subset_results_dict:
			subset_results_dict[key] = []

		if abs(diff) < correct_cut:
			n_correct_dict[key] += 1
			n_correct += 1

		subset_results_dict[key].append(subset_pred[i])
		subset_results.append(subset_pred[i])

	frac_dict = {}
	frac = []
	for hexcode in hexcodes:
		nall = n_all_dict.get(hexcode, 0)
		ncorrect = n_correct_dict.get(hexcode, 0)
		frac_dict[hexcode] = (1.0 * ncorrect / nall) if nall else 0.0
		frac.append(frac_dict[hexcode])
		print("Fraction of correct {} classification for class {} is {}".format(subset_name, hexcode, frac_dict[hexcode]))

	total_frac = (n_correct / float(n_all)) if n_all else 0.0
	print("{} total correct fraction: {}/{} = {}".format(subset_name, n_correct, n_all, total_frac))

	return {
		"results": subset_results,
		"resultsDict": subset_results_dict,
		"fracDict": frac_dict,
		"frac": frac,
		"nAll": n_all,
		"nCorrect": n_correct,
		"total_frac": total_frac,
	}


def plot_confusion_matrix_half_sep(true_outputs, pred_outputs, hexcodes, class_values, subset_name, setup_tag):
	"""Plot confusion matrix using half-distance boundaries between expected class outputs."""
	true_arr = np.asarray(true_outputs, dtype=float).reshape(-1)
	pred_arr = np.asarray(pred_outputs, dtype=float).reshape(-1)
	if len(true_arr) == 0 or len(pred_arr) == 0:
		print(f"WARNING: empty arrays for confusion matrix on {subset_name}, skipping plot.")
		return

	n = min(len(true_arr), len(pred_arr))
	true_arr = true_arr[:n]
	pred_arr = pred_arr[:n]

	boundaries = [0.5 * (class_values[i] + class_values[i + 1]) for i in range(len(class_values) - 1)]
	true_idx = np.digitize(true_arr, boundaries)
	pred_idx = np.digitize(pred_arr, boundaries)

	ncls = len(hexcodes)
	cm = np.zeros((ncls, ncls), dtype=int)
	for it, ip in zip(true_idx, pred_idx):
		cm[int(it), int(ip)] += 1

	plt.figure(figsize=(8, 7))
	cm_plot = np.log1p(cm.astype(float))
	plt.imshow(cm_plot, interpolation="nearest", cmap="hot_r")
	plt.title(f"confusion_matrix_{subset_name}")
	cbar = plt.colorbar()
	cbar.set_label("log(1+N)")
	ticks = np.arange(ncls)
	plt.xticks(ticks, hexcodes, rotation=45)
	plt.yticks(ticks, hexcodes)
	plt.gca().invert_yaxis()
	plt.xlabel("Predicted class")
	plt.ylabel("True class")
	plt.tight_layout()
	plt.savefig(f"confusion_matrix_{subset_name.lower()}{setup_tag}.png")
	plt.savefig(f"confusion_matrix_{subset_name.lower()}{setup_tag}.pdf")
	plt.close()


def build_results_pdf_report(results_dir):
	report_script = Path(__file__).with_name("build_pdf_report_from_results.py")
	if not report_script.exists():
		print(f"WARNING: report builder script not found: {report_script}")
		return

	cmd = [sys.executable, str(report_script), str(results_dir)]
	print("Running report builder: {}".format(" ".join(cmd)))
	proc = subprocess.run(cmd)
	if proc.returncode != 0:
		print("WARNING: report builder failed for {}".format(results_dir))
	else:
		print("Report PDF generated in {}".format(results_dir))


def maybe_restart_with_cpu_fallback(exc):
	msg = str(exc)
	low = msg.lower()
	gpu_init_error = (
		"cuda" in low
		or "cudnn" in low
		or "cublas" in low
		or "failed call to cuinit" in low
		or "could not create cudnn handle" in low
	)
	if not gpu_init_error:
		return False

	if os.environ.get("NN_TF_CPU_FALLBACK_USED") == "1":
		return False

	print("Detected TensorFlow CUDA initialization failure.")
	print("Re-launching this run in CPU-only mode (CUDA_VISIBLE_DEVICES=-1).")
	env = dict(os.environ)
	env["CUDA_VISIBLE_DEVICES"] = "-1"
	env["NN_TF_CPU_FALLBACK_USED"] = "1"
	os.execve(sys.executable, [sys.executable] + sys.argv, env)
	return True


def main(argv):
	default_settings = {
		"ntested": 15000,
		"nIters": 100,
		"inputn1": 250,
		"inputn2": 200,
		"batch_size": 32,
		"gBatch": True,
		"runOnnxTrainEval": True,
		"useFullTrainSet": True,
		"gTag": "",
		"dataPath": os.environ.get("NN_DATA_PATH", "data/by_class"),
	}

	settings = parse_argv(argv, default_settings)
	ntested = settings["ntested"]
	nIters = settings["nIters"]
	inputn1 = settings["inputn1"]
	inputn2 = settings["inputn2"]
	batch_size = settings["batch_size"]
	gBatch = settings["gBatch"]
	runOnnxTrainEval = settings["runOnnxTrainEval"]
	useFullTrainSet = settings["useFullTrainSet"]
	gTag = settings["gTag"]
	dataPath = settings["dataPath"]

	i1 = 0
	i2 = i1 + ntested

	learning_rate = 0.005

	print("*** Settings:")
	print("tag={:}, batch={:}".format(gTag, gBatch))
	hostname = os.environ.get("HOSTNAME", "")
	do_plots = True
	no_plot_show = gBatch or (hostname == "zubr")
	if gBatch:
		print("Batch mode enabled: plots will be saved, interactive display disabled.")
	elif hostname == "zubr":
		print("Running on zubr: interactive plot display disabled (saving files only).")

	print(f"nIters: {nIters}")
	print(f"ntested: {ntested}")
	print(f"inputn1: {inputn1}")
	print(f"inputn2: {inputn2}")
	print(f"batch_size: {batch_size}")
	print(f"runOnnxTrainEval: {runOnnxTrainEval}")
	print(f"useFullTrainSet: {useFullTrainSet}")
	print(f"dataPath: {dataPath}")

	hexcodes = [
        "30", # 1 
		"31", # 1 
		"32", # 2
		"33", # 3
		"34", # 4
		"35", # 5
        '36', # 6
        '37', # 7
        '38', # 8
        '39', # 9
                #'5a', # z
	]
	print("Will train on characters with hex codes: {}".format(hexcodes))

	cutoffx, cutoffy = 16, 20
	rebinx = 2
	rebiny = 2
	base_dim_x = int(128 / rebinx) - 2 * cutoffx
	base_dim_y = int(128 / rebiny) - 2 * cutoffy
	dim = base_dim_x * base_dim_y
	print("*** Got image dimension base {}x{} = {}".format(base_dim_x, base_dim_y, dim))

	preprocess_thr = 0.5
	use_relu = True

	n0 = dim
	n1 = inputn1
	n2 = inputn2
	n3 = 1
	print(f"*** Will train on NN with {n0} input, {n1} in 1st hidden, {n2} in 2nd hidden, {n3} output neurons.")

	train_chars = "train_" + "_".join(hexcodes)
	user_tag = f"_tag_{gTag}" if gTag else ""
	setup_tag = (
		f"{user_tag}_kerasTF_n1_{n1}_n2_{n2}_i1_{i1}_i2_{i2}_{train_chars}"
		f"_nImgs_{ntested}_iters_{nIters}_bs_{batch_size}_rate_{learning_rate:1.3f}"
	)
	print(f"Train tag: {setup_tag}")

	if not Path(dataPath).exists():
		print("ERROR: dataset path does not exist: {}".format(dataPath))
		print("Hint: set --datapath=/path/to/by_class or export NN_DATA_PATH=/path/to/by_class")
		return

	missing_classes = [hexcode for hexcode in hexcodes if not Path(dataPath, hexcode).exists()]
	if missing_classes:
		print("ERROR: dataset path is missing class directories: {}".format(missing_classes))
		return

	print("+++ reading training images +++")
	inputs, outputs = ReadData(
		hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, base_dim_x, dataPath=dataPath, thr=preprocess_thr
	)
	inputs = np.asarray(inputs, dtype=np.float32)
	outputs = np.asarray(outputs, dtype=np.float32)
	print("*** Train outputs:")
	PrintUnique(outputs)

	n_loaded = len(inputs)
	if n_loaded == 0:
		print("ERROR: no training data loaded, stopping.")
		return

	if useFullTrainSet:
		train_inputs = inputs
		train_outputs = outputs
		val_inputs = np.asarray([], dtype=np.float32)
		val_outputs = np.asarray([], dtype=np.float32)
		train_abs_ids = np.arange(i1, i1 + n_loaded)
		print("Using full training set: {}/{} train, {}/{} validation".format(len(train_inputs), n_loaded, 0, n_loaded))
	else:
		n_val = int(round(0.2 * n_loaded)) if n_loaded > 1 else 0
		n_val = max(1, min(n_val, n_loaded - 1)) if n_loaded > 1 else 0
		split_perm = np.random.permutation(n_loaded)
		val_idx = split_perm[:n_val]
		train_idx = split_perm[n_val:]
		train_inputs = inputs[train_idx]
		train_outputs = outputs[train_idx]
		val_inputs = inputs[val_idx]
		val_outputs = outputs[val_idx]
		train_abs_ids = i1 + train_idx
		print("Training/Validation split: {}/{} train, {}/{} validation".format(len(train_inputs), n_loaded, len(val_inputs), n_loaded))

	if len(train_inputs) == 0:
		print("ERROR: no training samples available, stopping.")
		return

	if batch_size <= 0:
		print("ERROR: batch_size must be > 0, stopping.")
		return
	batch_size = min(batch_size, len(train_inputs))

	try:
		import tensorflow as tf
		model = build_model(dim, n1, n2, learning_rate, use_relu=use_relu)
	except Exception as ex:
		if maybe_restart_with_cpu_fallback(ex):
			return
		print(f"ERROR: failed to construct TensorFlow model: {ex}")
		print("Hints:")
		print("- Force CPU: CUDA_VISIBLE_DEVICES=-1 python3 kerasTFnnRun_chars.py ...")
		print("- Your GT 730 (compute capability 3.5) is too old for modern TF GPU builds.")
		print("- Or install a CUDA/driver/TensorFlow combo that is mutually compatible.")
		return

	if do_plots:
		plot_dense_weights(model, setup_tag, suffix="pre")

	epoch_print_every = 10

	class EpochEveryN(tf.keras.callbacks.Callback):
		def __init__(self, every):
			super().__init__()
			self.every = max(1, int(every))

		def on_epoch_end(self, epoch, logs=None):
			logs = logs or {}
			epoch_num = epoch + 1
			total_epochs = int(self.params.get("epochs", epoch_num))
			if epoch_num == 1 or epoch_num % self.every == 0 or epoch_num == total_epochs:
				loss = logs.get("loss", float("nan"))
				val_loss = logs.get("val_loss", None)
				if val_loss is None:
					print(f"Epoch {epoch_num}/{total_epochs} - loss: {loss:.6f}")
				else:
					print(f"Epoch {epoch_num}/{total_epochs} - loss: {loss:.6f} - val_loss: {val_loss:.6f}")

	print("+++ training Keras model +++")
	fit_kwargs = {
		"x": train_inputs,
		"y": train_outputs,
		"epochs": nIters,
		"batch_size": batch_size,
		"verbose": 0,
		"shuffle": True,
		"callbacks": [EpochEveryN(epoch_print_every)],
	}
	if len(val_inputs):
		fit_kwargs["validation_data"] = (val_inputs, val_outputs)

	history = model.fit(**fit_kwargs)
	loss_hist = history.history.get("loss", [])

	correct_cut = 0.10
	nhex = len(hexcodes)
	nnoutmax = 1.0
	nnoutmin = 0.0
	delta = 0.1
	sep = (nnoutmax - nnoutmin) / nhex
	value_to_hex = {}
	class_values = []
	for ihex, hexcode in enumerate(hexcodes):
		class_value = nnoutmin + ihex * sep + delta
		class_values.append(class_value)
		value_to_hex[class_value] = hexcode

	print("+++ evaluating TRAIN subset +++")
	train_pred = model.predict(train_inputs, batch_size=batch_size, verbose=0).reshape(-1)
	train_metrics = evaluate_subset("TRAIN", train_inputs, train_outputs, train_pred, hexcodes, value_to_hex, correct_cut)

	n_details = 100
	train_detail_rows = []
	train_detail_count = {hexcode: 0 for hexcode in hexcodes}
	for i in range(len(train_inputs)):
		key = min(value_to_hex.items(), key=lambda kv: abs(kv[0] - train_outputs[i]))[1]
		if train_detail_count[key] >= n_details:
			continue
		train_detail_rows.append(
			[
				int(train_abs_ids[i]),
				key,
				float(train_outputs[i]),
				float(train_pred[i]),
				float(train_outputs[i] - train_pred[i]),
			]
		)
		train_detail_count[key] += 1

	train_details_csv = Path(f"train_event_details_N{n_details}{setup_tag}.csv")
	with train_details_csv.open("w", newline="") as out:
		writer = csv.writer(out)
		writer.writerow(["event_abs_i", "true_hex_class", "target_value", "classifier_output", "diff_target_minus_output"])
		writer.writerows(train_detail_rows)
	print(f"Saved training event details to {train_details_csv}")

	val_metrics = {
		"results": [],
		"resultsDict": {},
		"fracDict": {hexcode: 0.0 for hexcode in hexcodes},
		"frac": [0.0 for _ in hexcodes],
		"nAll": 0,
		"nCorrect": 0,
		"total_frac": 0.0,
	}

	if len(val_inputs):
		print("+++ evaluating VALIDATION subset +++")
		val_pred = model.predict(val_inputs, batch_size=batch_size, verbose=0).reshape(-1)
		val_metrics = evaluate_subset("VALIDATION", val_inputs, val_outputs, val_pred, hexcodes, value_to_hex, correct_cut)

	if do_plots:
		if len(loss_hist):
			PlotCost(loss_hist, setup_tag, "Cost Evolution", "red", "dotted")
		PlotDataAsHisto(train_metrics["results"], "Asimov_results", setup_tag)
		PlotIndivDataAsHisto(train_metrics["resultsDict"], "Asimov_results", setup_tag)
		PlotCost(train_metrics["frac"], setup_tag, "train_accuracies", "blue", "solid", "Char ID", "Accuracy", 0.0, 1.1)
		plot_confusion_matrix_half_sep(train_outputs, train_pred, hexcodes, class_values, "train", setup_tag)
		if len(val_inputs):
			PlotDataAsHisto(val_metrics["results"], "validation_results", setup_tag)
			PlotIndivDataAsHisto(val_metrics["resultsDict"], "validation_results", setup_tag)
			PlotCost(val_metrics["frac"], setup_tag, "validation_accuracies", "green", "solid", "Char ID", "Accuracy", 0.0, 1.1)

	if do_plots:
		plot_dense_weights(model, setup_tag, suffix="post")

	model_meta = {
		"framework": "tensorflow-keras",
		"setupTag": setup_tag,
		"n0": n0,
		"n1": n1,
		"n2": n2,
		"n3": n3,
		"learning_rate": learning_rate,
		"useReLu": use_relu,
		"useFullTrainSet": useFullTrainSet,
		"hexcodes": hexcodes,
		"cutoffx": cutoffx,
		"cutoffy": cutoffy,
		"rebinx": rebinx,
		"rebiny": rebiny,
		"baseDimx": base_dim_x,
		"baseDimy": base_dim_y,
		"preprocessThr": preprocess_thr,
		"labelNnoutmin": nnoutmin,
		"labelNnoutmax": nnoutmax,
		"labelDelta": delta,
		"dataPath": dataPath,
	}
	save_keras_model(model, setup_tag, model_meta)
	if runOnnxTrainEval:
		save_keras_onnx_model(model, setup_tag, dim)
	else:
		print("ONNX export disabled by runOnnxTrainEval setting")

	del inputs, outputs, train_inputs, train_outputs, train_pred
	gc.collect()

	print("+++ reading test images +++")
	i1 = 1 * i2
	i2 = i1 + ntested
	test_inputs, test_outputs = ReadData(
		hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, base_dim_x, False, -1, dataPath, thr=preprocess_thr
	)
	test_inputs = np.asarray(test_inputs, dtype=np.float32)
	test_outputs = np.asarray(test_outputs, dtype=np.float32)
	print("*** Test outputs:")
	PrintUnique(test_outputs)

	if len(test_inputs) == 0:
		print("ERROR: no test data loaded, stopping.")
		return

	test_pred = model.predict(test_inputs, batch_size=batch_size, verbose=0).reshape(-1)
	test_metrics = evaluate_subset("TEST", test_inputs, test_outputs, test_pred, hexcodes, value_to_hex, correct_cut)

	if do_plots:
		PlotDataAsHisto(test_metrics["results"], "test_results", setup_tag)
		PlotIndivDataAsHisto(test_metrics["resultsDict"], "test_results", setup_tag)
		plot_confusion_matrix_half_sep(test_outputs, test_pred, hexcodes, class_values, "test", setup_tag)
		PlotCost(test_metrics["frac"], setup_tag, "test_accuracies", "black", "solid", "Char ID", "Accuracy", 0.0, 1.1)

		plt.figure()
		xvals = range(1, len(hexcodes) + 1)
		plt.plot(xvals, train_metrics["frac"], "o", color="blue", linewidth=1, markersize=4, linestyle="solid", label="train")
		if len(val_inputs):
			plt.plot(xvals, val_metrics["frac"], "o", color="green", linewidth=1, markersize=4, linestyle="solid", label="validation")
		plt.plot(xvals, test_metrics["frac"], "o", color="black", linewidth=1, markersize=4, linestyle="solid", label="test")
		plt.xticks(list(xvals), hexcodes)
		plt.xlabel("Char ID")
		plt.ylabel("Accuracy")
		plt.title("train_vs_validation_vs_test_accuracies")
		plt.ylim(0.0, 1.1)
		plt.legend()
		plt.savefig(f"train_vs_validation_vs_test_accuracies{setup_tag}.png")
		plt.savefig(f"train_vs_validation_vs_test_accuracies{setup_tag}.pdf")

	sumfrac = sum(test_metrics["frac"])
	with open(f"accuracies{setup_tag}_sum_{sumfrac:1.3f}.txt", "w") as outfile:
		outfile.write("CharHexID : accuracy\n")
		for key, frac in test_metrics["fracDict"].items():
			outfile.write(f"{key} : {frac:1.3f}\n")
		outfile.write(f"Sum : {sumfrac:1.3f}\n")
		outfile.write(
			"Total correct fraction: {}/{} = {:1.3f}".format(
				test_metrics["nCorrect"], test_metrics["nAll"], test_metrics["total_frac"]
			) + "\n"
		)
		if len(val_inputs):
			outfile.write(
				"Validation total correct fraction: {}/{} = {:1.3f}".format(
					val_metrics["nCorrect"], val_metrics["nAll"], val_metrics["total_frac"]
				) + "\n"
			)

	if do_plots and not no_plot_show:
		plt.show()

	results_dir = Path("results") / f"results{setup_tag}"
	results_dir.mkdir(parents=True, exist_ok=True)
	for artifact in Path(".").glob(f"*{setup_tag}*.*"):
		if artifact.is_file():
			shutil.move(str(artifact), str(results_dir / artifact.name))

	print(f"All artifacts moved to {results_dir}")
	build_results_pdf_report(results_dir)


if __name__ == "__main__":
	main(sys.argv)
