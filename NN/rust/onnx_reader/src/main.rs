use image::ImageReader;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use tract_onnx::prelude::{tvec, Framework, InferenceModelExt, Tensor};

const DEFAULT_MODEL_PATH: &str = "/home/qitek/work/github/PyPlay/NN/results_n1_80_n2_80_i1_0_i2_4000_train_31_32_33_nImgs_4000_rate_0.005/model_n1_80_n2_80_i1_0_i2_4000_train_31_32_33_nImgs_4000_rate_0.005.onnx";
const DEFAULT_DATA_PATH: &str = "../../data/by_class";

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
}

fn default_config() -> Config {
    Config {
        model_path: PathBuf::from(DEFAULT_MODEL_PATH),
        data_path: PathBuf::from(DEFAULT_DATA_PATH),
        hexcodes: vec!["31".to_string(), "32".to_string(), "33".to_string()],
        // nnRun_Chars.py tests on the next ntested chunk (default ntested=4000)
        start_index: 4000,
        count: 4000,
        cutoffx: 16,
        cutoffy: 20,
        rebinx: 2,
        rebiny: 2,
        threshold: 0.5,
        correct_cut: 0.10,
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
    println!("  --start   <n>      First image index per class, default 4000");
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

fn run() -> Result<(), String> {
    let mut cfg = parse_args()?;
    cfg.data_path = resolve_data_path(&cfg.data_path);

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

    for hex in &cfg.hexcodes {
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
    }

    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
