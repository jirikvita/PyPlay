use cairo::{Context, PdfSurface};
use image::ImageReader;
use plotters::coord::Shift;
use plotters::prelude::*;
use plotters_cairo::CairoBackend;
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use tract_onnx::prelude::{tvec, Framework, InferenceModelExt, Tensor};

const DEFAULT_MODEL_PATH: &str = "/home/qitek/work/github/PyPlay/NN/results_n1_90_n2_90_i1_0_i2_4000_train_31_32_33_nImgs_4000_iters_100_bs_64_rate_0.005/model_n1_90_n2_90_i1_0_i2_4000_train_31_32_33_nImgs_4000_iters_100_bs_64_rate_0.005.onnx";
const DEFAULT_DATA_PATH: &str = "../../data/by_class";

#[derive(Debug, Clone)]
enum InputNormalization {
    None,
    Scalar {
        subtract: f32,
        divide: f32,
    },
    PerElement {
        subtract: Vec<f32>,
        divide: Vec<f32>,
    },
}

#[derive(Debug, Clone)]
struct ModelPreprocess {
    cutoffx: Option<usize>,
    cutoffy: Option<usize>,
    rebinx: Option<usize>,
    rebiny: Option<usize>,
    preprocess_thr: Option<f32>,
    input_normalization: InputNormalization,
}

impl Default for ModelPreprocess {
    fn default() -> Self {
        Self {
            cutoffx: None,
            cutoffy: None,
            rebinx: None,
            rebiny: None,
            preprocess_thr: None,
            input_normalization: InputNormalization::None,
        }
    }
}

#[derive(Debug)]
struct Config {
    model_path: PathBuf,
    data_path: PathBuf,
    hexcodes: Vec<String>,
    start_index: usize,
    count: usize,
    cutoffx: usize,
    cutoffy: usize,
    rebinx: usize,
    rebiny: usize,
    threshold: f32,
    correct_cut: f32,
    input_normalization: InputNormalization,
}

#[derive(Debug)]
struct ClassResult {
    hex: String,
    correct: usize,
    total: usize,
}

fn default_config() -> Config {
    Config {
        model_path: PathBuf::from(DEFAULT_MODEL_PATH),
        data_path: PathBuf::from(DEFAULT_DATA_PATH),
        hexcodes: vec!["31".to_string(), "32".to_string(), "33".to_string()],
        // nnRun_Chars.py tests on the next ntested chunk (default ntested=4000)
        start_index: 0,
        count: 4000,
        cutoffx: 16,
        cutoffy: 20,
        rebinx: 2,
        rebiny: 2,
        threshold: 0.5,
        correct_cut: 0.2,
        input_normalization: InputNormalization::None,
    }
}

fn parse_args() -> Result<Config, String> {
    let mut cfg = default_config();
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;

    while i < args.len() {
        match args[i].as_str() {
            "--help" | "-h" => {
                print_help();
                std::process::exit(0);
            }
            "--model" => {
                i += 1;
                cfg.model_path = PathBuf::from(args.get(i).ok_or("Missing value for --model")?);
            }
            "--data" => {
                i += 1;
                cfg.data_path = PathBuf::from(args.get(i).ok_or("Missing value for --data")?);
            }
            "--classes" => {
                i += 1;
                let val = args.get(i).ok_or("Missing value for --classes")?;
                cfg.hexcodes = val
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .filter(|s| !s.is_empty())
                    .collect();
                if cfg.hexcodes.is_empty() {
                    return Err("--classes produced an empty class list".to_string());
                }
            }
            "--start" => {
                i += 1;
                cfg.start_index = args
                    .get(i)
                    .ok_or("Missing value for --start")?
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid --start: {e}"))?;
            }
            "--count" => {
                i += 1;
                cfg.count = args
                    .get(i)
                    .ok_or("Missing value for --count")?
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid --count: {e}"))?;
            }
            "--cutoffx" => {
                i += 1;
                cfg.cutoffx = args
                    .get(i)
                    .ok_or("Missing value for --cutoffx")?
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid --cutoffx: {e}"))?;
            }
            "--cutoffy" => {
                i += 1;
                cfg.cutoffy = args
                    .get(i)
                    .ok_or("Missing value for --cutoffy")?
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid --cutoffy: {e}"))?;
            }
            "--rebinx" => {
                i += 1;
                cfg.rebinx = args
                    .get(i)
                    .ok_or("Missing value for --rebinx")?
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid --rebinx: {e}"))?;
            }
            "--rebiny" => {
                i += 1;
                cfg.rebiny = args
                    .get(i)
                    .ok_or("Missing value for --rebiny")?
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid --rebiny: {e}"))?;
            }
            other => return Err(format!("Unknown argument: {other}")),
        }
        i += 1;
    }

    Ok(cfg)
}

fn print_help() {
    println!("Run NN ONNX classifier on data/by_class images");
    println!("Usage: cargo run -- [options]");
    println!("  --model   <path>   ONNX model path");
    println!("  --data    <path>   Dataset root, default ../../data/by_class");
    println!("  --classes <csv>    Comma-separated hex classes, default 31,32,33");
    println!("  --start   <n>      First image index per class, default 0");
    println!("  --count   <n>      Number of images per class, default 4000");
    println!("  --cutoffx <n>      X crop cutoff after rebin, default 16");
    println!("  --cutoffy <n>      Y crop cutoff after rebin, default 20");
    println!("  --rebinx  <n>      Rebin factor in X, default 2");
    println!("  --rebiny  <n>      Rebin factor in Y, default 2");
}

fn resolve_data_path(data_path: &Path) -> PathBuf {
    if data_path.exists() {
        return data_path.to_path_buf();
    }
    // Allow passing ../../data while still matching python's default data/by_class layout.
    let by_class = data_path.join("by_class");
    if by_class.exists() {
        return by_class;
    }
    data_path.to_path_buf()
}

fn parse_json_f32_list(v: &serde_json::Value) -> Option<Vec<f32>> {
    let arr = v.as_array()?;
    let mut out = Vec::with_capacity(arr.len());
    for x in arr {
        out.push(x.as_f64()? as f32);
    }
    Some(out)
}

fn get_f32_from_json(v: &serde_json::Value, keys: &[&str]) -> Option<f32> {
    for k in keys {
        if let Some(val) = v.get(*k) {
            if let Some(n) = val.as_f64() {
                return Some(n as f32);
            }
        }
    }
    None
}

fn get_usize_from_json(v: &serde_json::Value, keys: &[&str]) -> Option<usize> {
    for k in keys {
        if let Some(val) = v.get(*k) {
            if let Some(n) = val.as_u64() {
                return Some(n as usize);
            }
        }
    }
    None
}

fn resolve_model_path(model_path: &Path) -> Result<PathBuf, String> {
    if model_path.is_file() {
        return Ok(model_path.to_path_buf());
    }
    if model_path.is_dir() {
        let mut onnx_files = Vec::new();
        for entry in fs::read_dir(model_path)
            .map_err(|e| format!("read_dir {} failed: {e}", model_path.display()))?
        {
            let entry = entry.map_err(|e| format!("read_dir entry failed: {e}"))?;
            let p = entry.path();
            if p.extension().and_then(|s| s.to_str()) == Some("onnx") {
                onnx_files.push(p);
            }
        }
        onnx_files.sort();
        if let Some(p) = onnx_files
            .iter()
            .find(|p| p.file_name().and_then(|s| s.to_str()).unwrap_or("").starts_with("model_"))
            .cloned()
            .or_else(|| onnx_files.first().cloned())
        {
            return Ok(p);
        }
        return Err(format!("No .onnx model found in directory {}", model_path.display()));
    }
    Err(format!("Model path not found: {}", model_path.display()))
}

fn load_model_preprocess(model_path: &Path) -> Result<ModelPreprocess, String> {
    let parent = match model_path.parent() {
        Some(p) => p,
        None => return Ok(ModelPreprocess::default()),
    };

    let mut meta_candidates = Vec::new();
    let stem = model_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("");
    let setup_tag = stem.strip_prefix("model").unwrap_or("");
    if !setup_tag.is_empty() {
        meta_candidates.push(parent.join(format!("model_meta{setup_tag}.json")));
    }
    meta_candidates.push(parent.join("model_meta.json"));

    let meta_path = if let Some(p) = meta_candidates.iter().find(|p| p.exists()) {
        p.clone()
    } else {
        let mut found = None;
        for entry in fs::read_dir(parent)
            .map_err(|e| format!("read_dir {} failed: {e}", parent.display()))?
        {
            let entry = entry.map_err(|e| format!("read_dir entry failed: {e}"))?;
            let p = entry.path();
            let name = p.file_name().and_then(|s| s.to_str()).unwrap_or("");
            if name.starts_with("model_meta") && name.ends_with(".json") {
                found = Some(p);
                break;
            }
        }
        if let Some(p) = found {
            p
        } else {
            return Ok(ModelPreprocess::default());
        }
    };

    let txt = fs::read_to_string(&meta_path)
        .map_err(|e| format!("Read model meta {} failed: {e}", meta_path.display()))?;
    let v: serde_json::Value = serde_json::from_str(&txt)
        .map_err(|e| format!("Parse model meta {} failed: {e}", meta_path.display()))?;

    let cutoffx = get_usize_from_json(&v, &["cutoffx"]);
    let cutoffy = get_usize_from_json(&v, &["cutoffy"]);
    let rebinx = get_usize_from_json(&v, &["rebinx"]);
    let rebiny = get_usize_from_json(&v, &["rebiny"]);
    let preprocess_thr = get_f32_from_json(&v, &["preprocessThr", "threshold", "thr"]);

    let scalar_mean = get_f32_from_json(&v, &["inputMean", "normalizeMean", "mean", "input_bias"]);
    let scalar_std = get_f32_from_json(&v, &["inputStd", "normalizeStd", "std", "input_scale"])
        .filter(|s| s.abs() > f32::EPSILON);

    let mut normalization = InputNormalization::None;
    if let (Some(m), Some(s)) = (scalar_mean, scalar_std) {
        normalization = InputNormalization::Scalar {
            subtract: m,
            divide: s,
        };
    } else {
        let mean_vec = v
            .get("inputMeanVec")
            .and_then(parse_json_f32_list)
            .or_else(|| v.get("normalizeMeanVec").and_then(parse_json_f32_list));
        let std_vec = v
            .get("inputStdVec")
            .and_then(parse_json_f32_list)
            .or_else(|| v.get("normalizeStdVec").and_then(parse_json_f32_list));
        if let (Some(mv), Some(sv)) = (mean_vec, std_vec) {
            if mv.len() == sv.len() && sv.iter().all(|x| x.abs() > f32::EPSILON) {
                normalization = InputNormalization::PerElement {
                    subtract: mv,
                    divide: sv,
                };
            }
        }
    }

    Ok(ModelPreprocess {
        cutoffx,
        cutoffy,
        rebinx,
        rebiny,
        preprocess_thr,
        input_normalization: normalization,
    })
}

fn apply_input_normalization(input: &mut [f32], normalization: &InputNormalization) -> Result<(), String> {
    match normalization {
        InputNormalization::None => Ok(()),
        InputNormalization::Scalar { subtract, divide } => {
            if divide.abs() <= f32::EPSILON {
                return Err("Invalid scalar normalization: divide is zero".to_string());
            }
            for x in input {
                *x = (*x - *subtract) / *divide;
            }
            Ok(())
        }
        InputNormalization::PerElement { subtract, divide } => {
            if input.len() != subtract.len() || input.len() != divide.len() {
                return Err(format!(
                    "Per-element normalization length mismatch: input={}, mean={}, std={}",
                    input.len(),
                    subtract.len(),
                    divide.len()
                ));
            }
            for i in 0..input.len() {
                if divide[i].abs() <= f32::EPSILON {
                    return Err(format!("Invalid per-element normalization: std at index {} is zero", i));
                }
                input[i] = (input[i] - subtract[i]) / divide[i];
            }
            Ok(())
        }
    }
}

fn make_img_id(i: usize) -> String {
    // Match existing dataset naming convention: train_<hex>_00000.png
    format!("{i:05}")
}

fn read_png_as_input(
    data_path: &Path,
    hexcode: &str,
    img_idx: usize,
    cutoffx: usize,
    cutoffy: usize,
    rebinx: usize,
    rebiny: usize,
    thr: f32,
) -> Result<Vec<f32>, String> {
    let imgid = make_img_id(img_idx);
    let file = data_path
        .join(hexcode)
        .join(format!("train_{hexcode}"))
        .join(format!("train_{hexcode}_{imgid}.png"));

    let img = ImageReader::open(&file)
        .map_err(|e| format!("open {}: {e}", file.display()))?
        .decode()
        .map_err(|e| format!("decode {}: {e}", file.display()))?
        .to_rgb8();

    let width = img.width() as usize;
    let height = img.height() as usize;
    let out_h = height / rebinx;
    let out_w = width / rebiny;
    if out_h == 0 || out_w == 0 {
        return Ok(Vec::new());
    }

    let mut rebinned = vec![0f32; out_h * out_w * 3];
    for oy in 0..out_h {
        for ox in 0..out_w {
            let mut sum_r = 0f32;
            let mut sum_g = 0f32;
            let mut sum_b = 0f32;
            for ky in 0..rebinx {
                for kx in 0..rebiny {
                    let py = oy * rebinx + ky;
                    let px = ox * rebiny + kx;
                    let p = img.get_pixel(px as u32, py as u32);
                    sum_r += p[0] as f32;
                    sum_g += p[1] as f32;
                    sum_b += p[2] as f32;
                }
            }
            let norm = (rebinx * rebiny) as f32;
            let base = (oy * out_w + ox) * 3;
            rebinned[base] = sum_r / norm;
            rebinned[base + 1] = sum_g / norm;
            rebinned[base + 2] = sum_b / norm;
        }
    }

    if out_h <= cutoffy * 2 || out_w <= cutoffx * 2 {
        return Err(format!(
            "crop became empty for {} (rebinned dims {}x{}, cutoffs {}x{})",
            file.display(),
            out_w,
            out_h,
            cutoffx,
            cutoffy
        ));
    }

    let mut flat = Vec::with_capacity((out_h - 2 * cutoffy) * (out_w - 2 * cutoffx));
    for y in cutoffy..(out_h - cutoffy) {
        for x in cutoffx..(out_w - cutoffx) {
            let base = (y * out_w + x) * 3;
            let is_dark = rebinned[base] <= thr && rebinned[base + 1] <= thr && rebinned[base + 2] <= thr;
            flat.push(if is_dark { 1.0 } else { 0.0 });
        }
    }

    Ok(flat)
}

fn class_target_map(hexcodes: &[String]) -> BTreeMap<String, f32> {
    let nhex = hexcodes.len() as f32;
    let sep = 1.0 / nhex;
    let delta = 0.1f32;
    let mut map = BTreeMap::new();
    for (i, hex) in hexcodes.iter().enumerate() {
        map.insert(hex.clone(), i as f32 * sep + delta);
    }
    map
}

fn nearest_class_index(pred: f32, targets: &[f32]) -> usize {
    let mut best_i = 0usize;
    let mut best_d = f32::INFINITY;
    for (i, t) in targets.iter().enumerate() {
        let d = (pred - *t).abs();
        if d < best_d {
            best_d = d;
            best_i = i;
        }
    }
    best_i
}

fn draw_accuracy_chart<DB: DrawingBackend>(
    root: DrawingArea<DB, Shift>,
    class_results: &[ClassResult],
    total_acc: f32,
    correct_cut: f32,
) -> Result<(), String>
where
    DB::ErrorType: std::fmt::Debug,
{
    root.fill(&WHITE)
        .map_err(|e| format!("draw background failed: {e:?}"))?;

    let labels: Vec<String> = class_results
        .iter()
        .map(|c| c.hex.clone())
        .chain(std::iter::once("TOTAL".to_string()))
        .collect();
    let mut values: Vec<f32> = class_results
        .iter()
        .map(|c| {
            if c.total > 0 {
                c.correct as f32 / c.total as f32
            } else {
                0.0
            }
        })
        .collect();
    values.push(total_acc);

    let n = values.len() as i32;
    let labels_for_axis = labels.clone();
    let mut chart = ChartBuilder::on(&root)
        .caption(
            format!("Accuracies (correct_cut = {:.2})", correct_cut),
            ("sans-serif", 28),
        )
        .margin(20)
        .x_label_area_size(60)
        .y_label_area_size(55)
        .build_cartesian_2d(0..n, 0f32..1f32)
        .map_err(|e| format!("build accuracy chart failed: {e:?}"))?;

    chart
        .configure_mesh()
        .y_desc("accuracy")
        .x_desc("class")
        .x_labels(labels.len())
        .x_label_formatter(&move |x| {
            labels_for_axis
                .get(*x as usize)
                .cloned()
                .unwrap_or_else(|| "".to_string())
        })
        .draw()
        .map_err(|e| format!("draw accuracy mesh failed: {e:?}"))?;

    chart
        .draw_series(values.iter().enumerate().map(|(i, acc)| {
            Rectangle::new(
                [(i as i32, 0.0f32), (i as i32 + 1, *acc)],
                BLUE.mix(0.65).filled(),
            )
        }))
        .map_err(|e| format!("draw accuracy bars failed: {e:?}"))?
        .label(format!("accuracy (correct_cut = {:.2})", correct_cut))
        .legend(|(x, y)| Rectangle::new([(x, y - 5), (x + 15, y + 5)], BLUE.mix(0.65).filled()));

    chart
        .configure_series_labels()
        .background_style(WHITE.mix(0.85))
        .border_style(BLACK)
        .draw()
        .map_err(|e| format!("draw accuracy legend failed: {e:?}"))?;

    root.present()
        .map_err(|e| format!("present accuracy chart failed: {e:?}"))?;
    Ok(())
}

fn draw_confusion_chart<DB: DrawingBackend>(
    root: DrawingArea<DB, Shift>,
    hexcodes: &[String],
    confusion: &[Vec<usize>],
    correct_cut: f32,
) -> Result<(), String>
where
    DB::ErrorType: std::fmt::Debug,
{
    root.fill(&WHITE)
        .map_err(|e| format!("draw background failed: {e:?}"))?;

    let n = hexcodes.len() as i32;
    let x_labels = hexcodes.to_vec();
    let y_labels = hexcodes.to_vec();

    let mut chart = ChartBuilder::on(&root)
        .caption(
            format!("Confusion Matrix (correct_cut = {:.2})", correct_cut),
            ("sans-serif", 28),
        )
        .margin(20)
        .x_label_area_size(70)
        .y_label_area_size(70)
        .build_cartesian_2d(0f32..n as f32, 0f32..n as f32)
        .map_err(|e| format!("build confusion chart failed: {e:?}"))?;

    chart
        .configure_mesh()
        .x_desc("predicted")
        .y_desc("actual")
        .x_labels(hexcodes.len())
        .y_labels(hexcodes.len())
        .x_label_formatter(&move |x| {
            let idx = (*x).floor() as usize;
            x_labels
                .get(idx)
                .cloned()
                .unwrap_or_else(|| "".to_string())
        })
        .y_label_formatter(&move |y| {
            let idx = (*y).floor() as usize;
            y_labels
                .get(idx)
                .cloned()
                .unwrap_or_else(|| "".to_string())
        })
        .draw()
        .map_err(|e| format!("draw confusion mesh failed: {e:?}"))?;

    let mut normalized = vec![vec![0.0f32; hexcodes.len()]; hexcodes.len()];
    for (actual_idx, row) in confusion.iter().enumerate() {
        let row_sum: usize = row.iter().sum();
        if row_sum > 0 {
            for (pred_idx, count) in row.iter().enumerate() {
                normalized[actual_idx][pred_idx] = *count as f32 / row_sum as f32 * 100.0;
            }
        }
    }

    for (actual_idx, row) in normalized.iter().enumerate() {
        for (pred_idx, pct) in row.iter().enumerate() {
            let intensity = (*pct as f64 / 100.0).clamp(0.0, 1.0);
            let shade = (255.0 * (1.0 - intensity)) as u8;
            let color = RGBColor(shade, shade, 255);
            chart
                .draw_series(std::iter::once(Rectangle::new(
                    [
                        (pred_idx as f32, actual_idx as f32),
                        (pred_idx as f32 + 1.0, actual_idx as f32 + 1.0),
                    ],
                    color.filled(),
                )))
                .map_err(|e| format!("draw confusion cell failed: {e:?}"))?;

            let text_color = if *pct > 55.0 { &WHITE } else { &BLACK };
            chart
                .draw_series(std::iter::once(Text::new(
                    format!("{pct:.1}%"),
                    (pred_idx as f32 + 0.5, actual_idx as f32 + 0.5),
                    ("sans-serif", 18).into_font().color(text_color),
                )))
                .map_err(|e| format!("draw confusion text failed: {e:?}"))?;
        }
    }

    chart
        .draw_series(std::iter::once(PathElement::new(
            vec![(0.0, 0.0), (0.0, 0.0)],
            BLUE.mix(0.65),
        )))
        .map_err(|e| format!("draw confusion legend anchor failed: {e:?}"))?
        .label(format!("correct_cut = {:.2}", correct_cut))
        .legend(|(x, y)| Rectangle::new([(x, y - 5), (x + 15, y + 5)], BLUE.mix(0.65).filled()));

    chart
        .configure_series_labels()
        .background_style(WHITE.mix(0.85))
        .border_style(BLACK)
        .draw()
        .map_err(|e| format!("draw confusion legend failed: {e:?}"))?;

    root.present()
        .map_err(|e| format!("present confusion chart failed: {e:?}"))?;
    Ok(())
}

fn draw_output_histogram_chart<DB: DrawingBackend>(
    root: DrawingArea<DB, Shift>,
    hexcodes: &[String],
    outputs_by_class: &[Vec<f32>],
    correct_cut: f32,
) -> Result<(), String>
where
    DB::ErrorType: std::fmt::Debug,
{
    root.fill(&WHITE)
        .map_err(|e| format!("draw background failed: {e:?}"))?;

    let all_values: Vec<f32> = outputs_by_class
        .iter()
        .flat_map(|v| v.iter().copied())
        .collect();
    if all_values.is_empty() {
        return Ok(());
    }

    let mut x_min = all_values
        .iter()
        .copied()
        .fold(f32::INFINITY, f32::min);
    let mut x_max = all_values
        .iter()
        .copied()
        .fold(f32::NEG_INFINITY, f32::max);
    if (x_max - x_min).abs() < f32::EPSILON {
        x_min -= 0.5;
        x_max += 0.5;
    }

    let bins = 80usize;
    let bin_w = (x_max - x_min) / bins as f32;
    let mut histograms = vec![vec![0usize; bins]; outputs_by_class.len()];
    for (class_idx, values) in outputs_by_class.iter().enumerate() {
        for v in values {
            let mut b = ((v - x_min) / bin_w).floor() as isize;
            if b < 0 {
                b = 0;
            }
            if b as usize >= bins {
                b = bins as isize - 1;
            }
            histograms[class_idx][b as usize] += 1;
        }
    }

    let mut y_max = 0.0f32;
    for (class_idx, hist) in histograms.iter().enumerate() {
        let denom = outputs_by_class[class_idx].len().max(1) as f32;
        for c in hist {
            y_max = y_max.max(*c as f32 / denom);
        }
    }
    if y_max <= 0.0 {
        y_max = 1.0;
    }

    let mut chart = ChartBuilder::on(&root)
        .caption(
            format!(
                "Model Output Histograms by Class (correct_cut = {:.2})",
                correct_cut
            ),
            ("sans-serif", 28),
        )
        .margin(20)
        .x_label_area_size(60)
        .y_label_area_size(70)
        .build_cartesian_2d(x_min..x_max, 0f32..(y_max * 1.15))
        .map_err(|e| format!("build histogram chart failed: {e:?}"))?;

    chart
        .configure_mesh()
        .x_desc("model output")
        .y_desc("fraction per bin")
        .draw()
        .map_err(|e| format!("draw histogram mesh failed: {e:?}"))?;

    let palette = [RED, BLUE, GREEN, MAGENTA, CYAN, BLACK, RGBColor(255, 140, 0)];
    for (class_idx, hist) in histograms.iter().enumerate() {
        let color = palette[class_idx % palette.len()];
        let alpha = 0.35;
        let denom = outputs_by_class[class_idx].len().max(1) as f32;
        chart
            .draw_series((0..bins).map(|b| {
                let x0 = x_min + b as f32 * bin_w;
                let x1 = x0 + bin_w;
                let h = hist[b] as f32 / denom;
                Rectangle::new([(x0, 0.0), (x1, h)], color.mix(alpha).filled())
            }))
            .map_err(|e| format!("draw histogram series failed: {e:?}"))?
            .label(format!("class {}", hexcodes[class_idx]))
            .legend(move |(x, y)| {
                Rectangle::new([(x, y - 5), (x + 15, y + 5)], color.mix(alpha).filled())
            });
    }

    chart
        .draw_series(std::iter::once(PathElement::new(
            vec![(x_min, 0.0), (x_min, 0.0)],
            BLACK,
        )))
        .map_err(|e| format!("draw histogram legend anchor failed: {e:?}"))?
        .label(format!("correct_cut = {:.2}", correct_cut))
        .legend(|(x, y)| Rectangle::new([(x, y - 5), (x + 15, y + 5)], BLACK.mix(0.7).filled()));

    chart
        .configure_series_labels()
        .background_style(WHITE.mix(0.85))
        .border_style(BLACK)
        .draw()
        .map_err(|e| format!("draw histogram legend failed: {e:?}"))?;

    root.present()
        .map_err(|e| format!("present histogram chart failed: {e:?}"))?;
    Ok(())
}

fn save_plots(
    cfg: &Config,
    class_results: &[ClassResult],
    total_acc: f32,
    confusion: &[Vec<usize>],
    outputs_by_class: &[Vec<f32>],
) -> Result<(), String> {
    let acc_png = PathBuf::from("accuracy_plot.png");
    let acc_pdf = PathBuf::from("accuracy_plot.pdf");
    let cm_png = PathBuf::from("confusion_matrix.png");
    let cm_pdf = PathBuf::from("confusion_matrix.pdf");
    let hist_png = PathBuf::from("output_histograms.png");
    let hist_pdf = PathBuf::from("output_histograms.pdf");

    let acc_png_root = BitMapBackend::new(&acc_png, (1200, 800)).into_drawing_area();
    draw_accuracy_chart(acc_png_root, class_results, total_acc, cfg.correct_cut)?;

    let acc_pdf_surface = PdfSurface::new(1200.0, 800.0, &acc_pdf)
        .map_err(|e| format!("create accuracy PDF surface failed: {e}"))?;
    let acc_pdf_ctx =
        Context::new(&acc_pdf_surface).map_err(|e| format!("create accuracy PDF context failed: {e}"))?;
    let acc_pdf_root = CairoBackend::new(&acc_pdf_ctx, (1200, 800))
        .map_err(|e| format!("create accuracy PDF backend failed: {e:?}"))?
        .into_drawing_area();
    draw_accuracy_chart(acc_pdf_root, class_results, total_acc, cfg.correct_cut)?;
    acc_pdf_surface.flush();
    acc_pdf_surface.finish();

    let cm_png_root = BitMapBackend::new(&cm_png, (1200, 900)).into_drawing_area();
    draw_confusion_chart(cm_png_root, &cfg.hexcodes, confusion, cfg.correct_cut)?;

    let cm_pdf_surface = PdfSurface::new(1200.0, 900.0, &cm_pdf)
        .map_err(|e| format!("create confusion PDF surface failed: {e}"))?;
    let cm_pdf_ctx =
        Context::new(&cm_pdf_surface).map_err(|e| format!("create confusion PDF context failed: {e}"))?;
    let cm_pdf_root = CairoBackend::new(&cm_pdf_ctx, (1200, 900))
        .map_err(|e| format!("create confusion PDF backend failed: {e:?}"))?
        .into_drawing_area();
    draw_confusion_chart(cm_pdf_root, &cfg.hexcodes, confusion, cfg.correct_cut)?;
    cm_pdf_surface.flush();
    cm_pdf_surface.finish();

    let hist_png_root = BitMapBackend::new(&hist_png, (1200, 800)).into_drawing_area();
    draw_output_histogram_chart(
        hist_png_root,
        &cfg.hexcodes,
        outputs_by_class,
        cfg.correct_cut,
    )?;

    let hist_pdf_surface = PdfSurface::new(1200.0, 800.0, &hist_pdf)
        .map_err(|e| format!("create histogram PDF surface failed: {e}"))?;
    let hist_pdf_ctx =
        Context::new(&hist_pdf_surface).map_err(|e| format!("create histogram PDF context failed: {e}"))?;
    let hist_pdf_root = CairoBackend::new(&hist_pdf_ctx, (1200, 800))
        .map_err(|e| format!("create histogram PDF backend failed: {e:?}"))?
        .into_drawing_area();
    draw_output_histogram_chart(
        hist_pdf_root,
        &cfg.hexcodes,
        outputs_by_class,
        cfg.correct_cut,
    )?;
    hist_pdf_surface.flush();
    hist_pdf_surface.finish();

    println!("Saved accuracy plot: {}", acc_png.display());
    println!("Saved accuracy plot: {}", acc_pdf.display());
    println!("Saved confusion matrix: {}", cm_png.display());
    println!("Saved confusion matrix: {}", cm_pdf.display());
    println!("Saved output histograms: {}", hist_png.display());
    println!("Saved output histograms: {}", hist_pdf.display());

    Ok(())
}

fn run() -> Result<(), String> {
    let mut cfg = parse_args()?;
    cfg.model_path = resolve_model_path(&cfg.model_path)?;
    cfg.data_path = resolve_data_path(&cfg.data_path);

    let model_preprocess = load_model_preprocess(&cfg.model_path)?;
    if let Some(v) = model_preprocess.cutoffx {
        cfg.cutoffx = v;
    }
    if let Some(v) = model_preprocess.cutoffy {
        cfg.cutoffy = v;
    }
    if let Some(v) = model_preprocess.rebinx {
        cfg.rebinx = v;
    }
    if let Some(v) = model_preprocess.rebiny {
        cfg.rebiny = v;
    }
    if let Some(v) = model_preprocess.preprocess_thr {
        cfg.threshold = v;
    }
    cfg.input_normalization = model_preprocess.input_normalization;

    if !cfg.model_path.exists() {
        return Err(format!(
            "Model file not found: {}",
            cfg.model_path.display()
        ));
    }
    if !cfg.data_path.exists() {
        return Err(format!(
            "Data path not found: {}\nHint: mount the external drive or pass --data <path-to-by_class>",
            cfg.data_path.display()
        ));
    }

    println!("Model: {}", cfg.model_path.display());
    println!("Data path: {}", cfg.data_path.display());
    println!("Classes: {}", cfg.hexcodes.join(","));
    println!("Range: [{}..{})", cfg.start_index, cfg.start_index + cfg.count);
    println!("Threshold: {:.4}", cfg.threshold);
    println!("Correct cut: {:.4}", cfg.correct_cut);
    match &cfg.input_normalization {
        InputNormalization::None => println!("Input normalization: none"),
        InputNormalization::Scalar { subtract, divide } => {
            println!(
                "Input normalization: scalar (x - {:.6}) / {:.6}",
                subtract, divide
            )
        }
        InputNormalization::PerElement { subtract, .. } => {
            println!("Input normalization: per-element, length {}", subtract.len())
        }
    }

    let targets = class_target_map(&cfg.hexcodes);
    let model = tract_onnx::onnx()
        .model_for_path(&cfg.model_path)
        .map_err(|e| format!("Load ONNX model failed: {e}"))?
        .into_optimized()
        .map_err(|e| format!("Optimize ONNX model failed: {e}"))?
        .into_runnable()
        .map_err(|e| format!("Prepare ONNX model runtime failed: {e}"))?;

    let mut total_all = 0usize;
    let mut total_ok = 0usize;
    let mut class_results = Vec::with_capacity(cfg.hexcodes.len());
    let mut confusion = vec![vec![0usize; cfg.hexcodes.len()]; cfg.hexcodes.len()];
    let mut outputs_by_class = vec![Vec::<f32>::new(); cfg.hexcodes.len()];

    let target_values: Vec<f32> = cfg
        .hexcodes
        .iter()
        .map(|hex| {
            targets
                .get(hex)
                .copied()
                .ok_or_else(|| format!("No target mapping for class {hex}"))
        })
        .collect::<Result<Vec<_>, _>>()?;

    for (actual_idx, hex) in cfg.hexcodes.iter().enumerate() {
        let class_dir = cfg.data_path.join(hex);
        if !class_dir.exists() {
            return Err(format!(
                "Missing class directory: {}",
                class_dir.display()
            ));
        }

        let target = *targets
            .get(hex)
            .ok_or_else(|| format!("No target mapping for class {hex}"))?;
        let mut class_all = 0usize;
        let mut class_ok = 0usize;

        for idx in cfg.start_index..(cfg.start_index + cfg.count) {
            let input = match read_png_as_input(
                &cfg.data_path,
                hex,
                idx,
                cfg.cutoffx,
                cfg.cutoffy,
                cfg.rebinx,
                cfg.rebiny,
                cfg.threshold,
            ) {
                Ok(v) if !v.is_empty() => v,
                Ok(_) => continue,
                Err(_) => continue,
            };

            let mut input = input;
            apply_input_normalization(&mut input, &cfg.input_normalization)
                .map_err(|e| format!("Normalization failed for class {hex}, idx {idx}: {e}"))?;

            let input_tensor = Tensor::from_shape(&[1usize, input.len()], &input)
                .map_err(|e| format!("Create input tensor failed for class {hex}, idx {idx}: {e}"))?;

            let result = model
                .run(tvec!(input_tensor.into()))
                .map_err(|e| format!("Inference failed for class {hex}, idx {idx}: {e}"))?;
            let output = result[0]
                .to_array_view::<f32>()
                .map_err(|e| format!("Read output tensor failed for class {hex}, idx {idx}: {e}"))?;

            let pred = output.iter().next().copied().ok_or_else(|| {
                format!("Empty output tensor for class {hex}, idx {idx}")
            })?;
            outputs_by_class[actual_idx].push(pred);

            let pred_idx = nearest_class_index(pred, &target_values);
            confusion[actual_idx][pred_idx] += 1;

            let diff = (target - pred).abs();
            class_all += 1;
            total_all += 1;
            if diff < cfg.correct_cut {
                class_ok += 1;
                total_ok += 1;
            }
        }

        let acc = if class_all > 0 {
            class_ok as f32 / class_all as f32
        } else {
            0.0
        };
        println!(
            "Class {} -> target {:.4}, accuracy {}/{} = {:.4}",
            hex, target, class_ok, class_all, acc
        );

        class_results.push(ClassResult {
            hex: hex.clone(),
            correct: class_ok,
            total: class_all,
        });
    }

    let total_acc = if total_all > 0 {
        total_ok as f32 / total_all as f32
    } else {
        0.0
    };
    println!(
        "Total accuracy: {}/{} = {:.4}",
        total_ok, total_all, total_acc
    );

    if total_all == 0 {
        println!(
            "No samples were processed. Check mounted data path and image index range."
        );
    } else {
        save_plots(
            &cfg,
            &class_results,
            total_acc,
            &confusion,
            &outputs_by_class,
        )?;
    }

    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
