#!/usr/bin/env python3
import argparse
import importlib
import re
import string
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


# https://krestanem.cz/down/ekumenicky.pdf
# https://www.churchofjesuschrist.org/bc/content/shared/content/english/pdf/language-materials/83290_eng.pdf

LETTERS = string.ascii_lowercase
LETTER_TO_INDEX = {ch: idx for idx, ch in enumerate(LETTERS)}
BIGRAM_CHARS = string.ascii_lowercase + " "
BIGRAM_CHAR_TO_INDEX = {ch: idx for idx, ch in enumerate(BIGRAM_CHARS)}


def get_pdf_reader_class():
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = importlib.import_module(module_name)
            return module.PdfReader
        except ModuleNotFoundError:
            continue
    raise SystemExit(
        "Missing dependency: install pypdf or PyPDF2 (and matplotlib)."
    )


def render_progress(current: int, total: int, prefix: str, width: int = 30) -> None:
    if total <= 0:
        return
    ratio = current / total
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    percent = int(ratio * 100)
    print(f"\r{prefix} [{bar}] {current}/{total} ({percent}%)", end="", flush=True)
    if current == total:
        print()


def extract_text_from_pdf(pdf_path: Path, label: str) -> str:
    if not pdf_path.exists() or not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"Processing {label} document: {pdf_path}")
    pdf_reader_class = get_pdf_reader_class()
    reader = pdf_reader_class(str(pdf_path))
    parts = []
    total_pages = len(reader.pages)
    for idx, page in enumerate(reader.pages, start=1):
        parts.append(page.extract_text() or "")
        render_progress(idx, total_pages, prefix=f"Extracting {label}")
    print(f"Finished {label}: extracted text from {total_pages} pages")
    return "\n".join(parts)


def save_text_export(text: str, source_pdf: Path, output_dir: Path, label: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{source_pdf.stem}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"Saved {label} extracted text to: {out_path}")
    return out_path


def load_text_file(text_path: Path, label: str) -> str:
    if not text_path.exists() or not text_path.is_file():
        raise FileNotFoundError(f"Text file not found for {label}: {text_path}")
    print(f"Reading {label} analysis input from text file: {text_path}")
    return text_path.read_text(encoding="utf-8")


def strip_accents_to_ascii(text: str) -> str:
    # Normalize Czech diacritics so frequencies are measured over a..z only.
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_case_and_accents(text: str) -> str:
    # Case-insensitive processing for all PDF text before downstream counting.
    return strip_accents_to_ascii(text).casefold()


def letter_frequency_az(text: str) -> dict[str, float]:
    print("Normalizing text and computing letter frequencies...")
    text = normalize_case_and_accents(text)
    letters_only = [ch for ch in text if ch in LETTERS]
    counts = Counter(letters_only)
    total = sum(counts.values())

    if total == 0:
        return {ch: 0.0 for ch in LETTERS}

    return {ch: (counts.get(ch, 0) / total) * 100.0 for ch in LETTERS}


def normalize_for_bigrams(text: str) -> list[str]:
    """Normalize text for bigrams over a..z plus space."""
    normalized_text = normalize_case_and_accents(text)
    chars = []
    for ch in normalized_text:
        if ch in string.whitespace:
            chars.append(" ")
        elif ch in string.ascii_lowercase:
            chars.append(ch)
    return chars


def normalized_bigram_matrix_az(text: str) -> list[list[float]]:
    """Build a matrix M[x][y] = normalized frequency of bigram x->y over a..z + space."""
    letters_only = normalize_for_bigrams(text)

    matrix = [[0 for _ in BIGRAM_CHARS] for _ in BIGRAM_CHARS]
    if len(letters_only) < 2:
        return [[0.0 for _ in BIGRAM_CHARS] for _ in BIGRAM_CHARS]

    total_bigrams = 0
    for i in range(len(letters_only) - 1):
        x = letters_only[i]
        y = letters_only[i + 1]
        matrix[BIGRAM_CHAR_TO_INDEX[x]][BIGRAM_CHAR_TO_INDEX[y]] += 1
        total_bigrams += 1

    return [[cell / total_bigrams for cell in row] for row in matrix]


def word_length_distribution(text: str) -> dict[int, int]:
    normalized_text = normalize_case_and_accents(text)
    words = re.findall(r"[a-z]+", normalized_text)
    length_counts = Counter(len(word) for word in words)
    return dict(sorted(length_counts.items()))


def word_length_distribution_filtered(
    text: str,
    remove_common_english_articles: bool = False,
    drop_one_letter_words: bool = True,
) -> dict[int, int]:
    normalized_text = normalize_case_and_accents(text)
    words = re.findall(r"[a-z]+", normalized_text)

    filtered_words = []
    for word in words:
        if drop_one_letter_words and len(word) == 1:
            continue
        if remove_common_english_articles and word in {"the", "an"}:
            continue
        filtered_words.append(word)

    length_counts = Counter(len(word) for word in filtered_words)
    return dict(sorted(length_counts.items()))


def plot_bigram_square_matrix(
    cz_matrix: list[list[float]],
    en_matrix: list[list[float]],
    png_path: Path,
    pdf_path: Path,
) -> None:
    bigram_labels = ["-" if ch == " " else ch for ch in BIGRAM_CHARS]

    def _plot_one(ax, matrix: list[list[float]], title: str) -> None:
        xs = []
        ys = []
        sizes = []
        max_value = max(max(row) for row in matrix) if matrix else 0.0
        if max_value == 0.0:
            max_value = 1.0

        for x_idx in range(len(BIGRAM_CHARS)):
            for y_idx in range(len(BIGRAM_CHARS)):
                value = matrix[x_idx][y_idx]
                if value <= 0:
                    continue
                xs.append(x_idx)
                ys.append(y_idx)
                sizes.append((value / max_value) * 650.0)

        ax.scatter(xs, ys, s=sizes, marker="s", c="blue", alpha=0.7)
        ax.set_xlim(-0.5, len(BIGRAM_CHARS) - 0.5)
        ax.set_ylim(-0.5, len(BIGRAM_CHARS) - 0.5)
        ax.set_xticks(range(len(BIGRAM_CHARS)))
        ax.set_yticks(range(len(BIGRAM_CHARS)))
        ax.set_xticklabels(bigram_labels, fontsize=8)
        ax.set_yticklabels(bigram_labels, fontsize=8)
        ax.set_xlabel("Y (second letter)")
        ax.set_ylabel("X (first letter)")
        ax.set_title(title)
        ax.grid(True, linewidth=0.2, alpha=0.3)

    print("Rendering bigram XY square-matrix plot...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, sharey=True)
    _plot_one(axes[0], cz_matrix, "CZ Bigrams: X->Y")
    _plot_one(axes[1], en_matrix, "ENG Bigrams: X->Y")
    fig.tight_layout()
    fig.savefig(png_path)
    fig.savefig(pdf_path)
    print(f"Saved bigram plot PNG to: {png_path}")
    print(f"Saved bigram plot PDF to: {pdf_path}")


def plot_histograms(
    cz_freq: dict[str, float],
    en_freq: dict[str, float],
    title: str,
    png_path: Path,
    pdf_path: Path,
) -> None:
    x = list(range(len(LETTERS)))
    cz_values = [cz_freq[ch] for ch in LETTERS]
    en_values = [en_freq[ch] for ch in LETTERS]
    width = 0.42

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar([i - width / 2 for i in x], cz_values, width=width, color="green", label="CZ")
    ax.bar([i + width / 2 for i in x], en_values, width=width, color="blue", label="ENG")
    ax.set_xticks(x, list(LETTERS))
    ax.set_ylabel("Relative frequency (%)")
    ax.set_xlabel("Letter")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(png_path)
    fig.savefig(pdf_path)
    print(f"Saved histogram PNG to: {png_path}")
    print(f"Saved histogram PDF to: {pdf_path}")
    print("Prepared histogram plot.")


def plot_word_length_histogram_pair(
    cz_length_counts: dict[int, int],
    en_length_counts: dict[int, int],
    title: str,
    png_path: Path,
    pdf_path: Path,
    axis_lengths: list[int],
    y_max: int,
) -> None:
    lengths = axis_lengths
    cz_values = [cz_length_counts.get(length, 0) for length in lengths]
    en_values = [en_length_counts.get(length, 0) for length in lengths]
    width = 0.42

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([length - width / 2 for length in lengths], cz_values, width=width, color="green", label="CZ")
    ax.bar([length + width / 2 for length in lengths], en_values, width=width, color="blue", label="ENG")
    ax.set_xlabel("Word length")
    ax.set_ylabel("Word count")
    ax.set_title(title)
    ax.set_xticks(lengths)
    if lengths:
        ax.set_xlim(min(lengths) - 0.8, max(lengths) + 0.8)
    ax.set_ylim(0, max(1, int(y_max * 1.05)))
    ax.legend()
    fig.tight_layout()
    fig.savefig(png_path)
    fig.savefig(pdf_path)
    print(f"Saved word-length pair PNG to: {png_path}")
    print(f"Saved word-length pair PDF to: {pdf_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze a..z letter frequencies in Czech and English PDFs and plot them."
    )
    parser.add_argument(
        "--cz-pdf",
        type=Path,
        default=Path("/home/qitek/Documents/ekumenicky.pdf"),
        help="Path to Czech PDF",
    )
    parser.add_argument(
        "--en-pdf",
        type=Path,
        default=Path("/home/qitek/Documents/83290_eng.pdf"),
        help="Path to English PDF",
    )
    parser.add_argument(
        "--export-text",
        dest="export_text",
        action="store_true",
        help="Export each PDF extraction to a .txt file before analysis.",
    )
    parser.add_argument(
        "--no-export-text",
        dest="export_text",
        action="store_false",
        help="Use existing text files without exporting from PDFs (default).",
    )
    parser.add_argument(
        "--text-out-dir",
        type=Path,
        default=Path("extracted_text"),
        help="Directory for exported text files when --export-text is enabled.",
    )
    parser.set_defaults(export_text=False)
    args = parser.parse_args()

    cz_text_path = args.text_out_dir / f"{args.cz_pdf.stem}.txt"
    en_text_path = args.text_out_dir / f"{args.en_pdf.stem}.txt"

    try:
        if args.export_text:
            print("Exporting extracted PDF text to files...")
            cz_pdf_text = extract_text_from_pdf(args.cz_pdf, label="CZ")
            en_pdf_text = extract_text_from_pdf(args.en_pdf, label="ENG")
            cz_text_path = save_text_export(cz_pdf_text, args.cz_pdf, args.text_out_dir, "CZ")
            en_text_path = save_text_export(en_pdf_text, args.en_pdf, args.text_out_dir, "ENG")

        cz_text = load_text_file(cz_text_path, label="CZ")
        en_text = load_text_file(en_text_path, label="ENG")
    except Exception as exc:
        print(f"Error preparing text inputs: {exc}", file=sys.stderr)
        return 1

    print("Computing frequency distributions...")
    cz_freq = letter_frequency_az(cz_text)
    en_freq = letter_frequency_az(en_text)
    print("Computing normalized bigram matrices (27x27, includes space)...")
    cz_bigram_matrix = normalized_bigram_matrix_az(cz_text)
    en_bigram_matrix = normalized_bigram_matrix_az(en_text)
    print("Computing word-length distributions...")
    cz_word_lengths = word_length_distribution(cz_text)
    en_word_lengths = word_length_distribution(en_text)
    print("Computing filtered word-length distributions (drop 1-letter words; ENG also drop 'the' and 'an')...")
    cz_word_lengths_filtered = word_length_distribution_filtered(
        cz_text,
        remove_common_english_articles=False,
        drop_one_letter_words=True,
    )
    en_word_lengths_filtered = word_length_distribution_filtered(
        en_text,
        remove_common_english_articles=True,
        drop_one_letter_words=True,
    )

    print("Letter frequencies (%):")
    print("letter\tCZ\tENG")
    for ch in LETTERS:
        print(f"{ch}\t{cz_freq[ch]:.4f}\t{en_freq[ch]:.4f}")

    histogram_png = Path("letter_frequency_histogram.png").resolve()
    histogram_pdf = Path("letter_frequency_histogram.pdf").resolve()
    bigram_png = Path("bigram_xy_square_matrix.png").resolve()
    bigram_pdf = Path("bigram_xy_square_matrix.pdf").resolve()
    wordlen_pair_png = Path("word_length_histogram_pair.png").resolve()
    wordlen_pair_pdf = Path("word_length_histogram_pair.pdf").resolve()
    wordlen_filtered_pair_png = Path("word_length_histogram_pair_filtered.png").resolve()
    wordlen_filtered_pair_pdf = Path("word_length_histogram_pair_filtered.pdf").resolve()

    shared_word_lengths = sorted(
        set(cz_word_lengths.keys())
        | set(en_word_lengths.keys())
        | set(cz_word_lengths_filtered.keys())
        | set(en_word_lengths_filtered.keys())
    )
    shared_y_max = max(
        list(cz_word_lengths.values())
        + list(en_word_lengths.values())
        + list(cz_word_lengths_filtered.values())
        + list(en_word_lengths_filtered.values())
        + [0]
    )

    plot_histograms(
        cz_freq,
        en_freq,
        "a..z Letter Frequency: Czech vs English",
        histogram_png,
        histogram_pdf,
    )
    plot_bigram_square_matrix(
        cz_bigram_matrix,
        en_bigram_matrix,
        bigram_png,
        bigram_pdf,
    )
    plot_word_length_histogram_pair(
        cz_word_lengths,
        en_word_lengths,
        "Word Length Distribution (CZ vs ENG)",
        wordlen_pair_png,
        wordlen_pair_pdf,
        shared_word_lengths,
        shared_y_max,
    )
    plot_word_length_histogram_pair(
        cz_word_lengths_filtered,
        en_word_lengths_filtered,
        "Word Length Distribution Filtered (drop 1-letter; ENG drop 'the' and 'an')",
        wordlen_filtered_pair_png,
        wordlen_filtered_pair_pdf,
        shared_word_lengths,
        shared_y_max,
    )
    print("Showing all plots...")
    plt.show()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
