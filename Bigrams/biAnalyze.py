#!/usr/bin/env python3
import argparse
import importlib
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


def strip_accents_to_ascii(text: str) -> str:
    # Normalize Czech diacritics so frequencies are measured over a..z only.
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def letter_frequency_az(text: str) -> dict[str, float]:
    print("Normalizing text and computing letter frequencies...")
    text = strip_accents_to_ascii(text).lower()
    letters_only = [ch for ch in text if ch in LETTERS]
    counts = Counter(letters_only)
    total = sum(counts.values())

    if total == 0:
        return {ch: 0.0 for ch in LETTERS}

    return {ch: (counts.get(ch, 0) / total) * 100.0 for ch in LETTERS}


def normalized_bigram_matrix_az(text: str) -> list[list[float]]:
    """Build a 26x26 matrix M[x][y] = normalized frequency of bigram x->y."""
    normalized_text = strip_accents_to_ascii(text).lower()
    letters_only = [ch for ch in normalized_text if ch in LETTERS]

    matrix = [[0 for _ in LETTERS] for _ in LETTERS]
    if len(letters_only) < 2:
        return [[0.0 for _ in LETTERS] for _ in LETTERS]

    total_bigrams = 0
    for i in range(len(letters_only) - 1):
        x = letters_only[i]
        y = letters_only[i + 1]
        matrix[LETTER_TO_INDEX[x]][LETTER_TO_INDEX[y]] += 1
        total_bigrams += 1

    return [[cell / total_bigrams for cell in row] for row in matrix]


def plot_bigram_square_matrix(
    cz_matrix: list[list[float]], en_matrix: list[list[float]]
) -> None:
    def _plot_one(ax, matrix: list[list[float]], title: str) -> None:
        xs = []
        ys = []
        sizes = []
        max_value = max(max(row) for row in matrix) if matrix else 0.0
        if max_value == 0.0:
            max_value = 1.0

        for x_idx in range(len(LETTERS)):
            for y_idx in range(len(LETTERS)):
                value = matrix[x_idx][y_idx]
                if value <= 0:
                    continue
                xs.append(x_idx)
                ys.append(y_idx)
                sizes.append((value / max_value) * 650.0)

        ax.scatter(xs, ys, s=sizes, marker="s", c="blue", alpha=0.7)
        ax.set_xlim(-0.5, len(LETTERS) - 0.5)
        ax.set_ylim(-0.5, len(LETTERS) - 0.5)
        ax.set_xticks(range(len(LETTERS)))
        ax.set_yticks(range(len(LETTERS)))
        ax.set_xticklabels(list(LETTERS), fontsize=8)
        ax.set_yticklabels(list(LETTERS), fontsize=8)
        ax.set_xlabel("Y (second letter)")
        ax.set_ylabel("X (first letter)")
        ax.set_title(title)
        ax.grid(True, linewidth=0.2, alpha=0.3)

    print("Rendering bigram XY square-matrix plot...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, sharey=True)
    _plot_one(axes[0], cz_matrix, "CZ Bigrams: X->Y")
    _plot_one(axes[1], en_matrix, "ENG Bigrams: X->Y")
    fig.tight_layout()
    plt.show()


def plot_histograms(cz_freq: dict[str, float], en_freq: dict[str, float], title: str) -> None:
    x = list(range(len(LETTERS)))
    cz_values = [cz_freq[ch] for ch in LETTERS]
    en_values = [en_freq[ch] for ch in LETTERS]
    width = 0.42

    plt.figure(figsize=(14, 6))
    plt.bar([i - width / 2 for i in x], cz_values, width=width, color="green", label="CZ")
    plt.bar([i + width / 2 for i in x], en_values, width=width, color="blue", label="ENG")
    plt.xticks(x, list(LETTERS))
    plt.ylabel("Relative frequency (%)")
    plt.xlabel("Letter")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    print("Rendering histogram plot...")
    plt.show()


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
    args = parser.parse_args()

    try:
        cz_text = extract_text_from_pdf(args.cz_pdf, label="CZ")
        en_text = extract_text_from_pdf(args.en_pdf, label="ENG")
    except Exception as exc:
        print(f"Error reading PDFs: {exc}", file=sys.stderr)
        return 1

    print("Computing frequency distributions...")
    cz_freq = letter_frequency_az(cz_text)
    en_freq = letter_frequency_az(en_text)
    print("Computing normalized bigram matrices (26x26)...")
    cz_bigram_matrix = normalized_bigram_matrix_az(cz_text)
    en_bigram_matrix = normalized_bigram_matrix_az(en_text)

    print("Letter frequencies (%):")
    print("letter\tCZ\tENG")
    for ch in LETTERS:
        print(f"{ch}\t{cz_freq[ch]:.4f}\t{en_freq[ch]:.4f}")

    plot_histograms(cz_freq, en_freq, "a..z Letter Frequency: Czech vs English")
    plot_bigram_square_matrix(cz_bigram_matrix, en_bigram_matrix)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
