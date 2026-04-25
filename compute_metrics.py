"""
SPB-RADS Evaluation — Statistical Fidelity Metrics
====================================================
Computes FID, SSIM, and IS for synthetic vs real medical images.

Usage:
    python compute_metrics.py \
        --real_dir /path/to/real_images \
        --synth_dir /path/to/synthetic_images \
        --modality brain_mri \
        --output results/metrics.csv

Requirements: see requirements.txt
"""

import argparse
import os
import json
import csv
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim_func
from torch_fidelity import calculate_metrics


# ── Modality-specific preprocessing ──────────────────────────────────────────

MODALITY_PRESETS = {
    "brain_mri": {
        "window_width": 80,
        "window_level": 35,
        "single_channel": False,
        "description": "Brain MRI — no windowing applied, convert to RGB"
    },
    "brain_ncct": {
        "window_width": 80,
        "window_level": 35,
        "single_channel": False,
        "description": "Brain NCCT brain window W80 L35"
    },
    "abdominal_ct": {
        "window_width": 400,
        "window_level": 60,
        "single_channel": False,
        "description": "Abdominal CT soft tissue window W400 L60"
    },
    "ultrasound": {
        "window_width": None,
        "window_level": None,
        "single_channel": True,
        "description": "Abdominal ultrasound — grayscale, triplicate for FID"
    },
}


def load_image_rgb(path: Path, single_channel: bool = False) -> np.ndarray:
    """Load image and convert to RGB numpy array (H, W, 3) uint8."""
    img = Image.open(path).convert("L" if single_channel else "RGB")
    if single_channel:
        img = Image.fromarray(
            np.stack([np.array(img)] * 3, axis=-1)
        )
    return np.array(img.convert("RGB"))


def compute_ssim_pair(real_path: Path, synth_path: Path) -> float:
    """SSIM between one real and one synthetic image (grayscale)."""
    real = np.array(Image.open(real_path).convert("L"))
    synth = np.array(Image.open(synth_path).convert("L"))

    # Resize synth to real if sizes differ
    if real.shape != synth.shape:
        synth_pil = Image.open(synth_path).convert("L").resize(
            (real.shape[1], real.shape[0]), Image.LANCZOS
        )
        synth = np.array(synth_pil)

    score = ssim_func(
        real, synth,
        data_range=255,
        win_size=7,
        gaussian_weights=True,
        sigma=1.5
    )
    return float(score)


def compute_ssim_dataset(real_dir: Path, synth_dir: Path) -> dict:
    """Compute SSIM for all image pairs. Pairs by sorted filename order."""
    real_files = sorted(list(real_dir.glob("*.png")) +
                        list(real_dir.glob("*.jpg")) +
                        list(real_dir.glob("*.jpeg")))
    synth_files = sorted(list(synth_dir.glob("*.png")) +
                         list(synth_dir.glob("*.jpg")) +
                         list(synth_dir.glob("*.jpeg")))

    n = min(len(real_files), len(synth_files))
    if n == 0:
        return {"ssim_mean": None, "ssim_std": None, "n_pairs": 0}

    scores = [
        compute_ssim_pair(real_files[i], synth_files[i])
        for i in range(n)
    ]
    return {
        "ssim_mean": float(np.mean(scores)),
        "ssim_std": float(np.std(scores)),
        "n_pairs": n,
        "ssim_scores": scores
    }


def compute_fid_is(real_dir: Path, synth_dir: Path) -> dict:
    """
    Compute FID and IS using torch-fidelity.
    Images resized to 299x299, converted to RGB for InceptionV3.
    """
    metrics = calculate_metrics(
        input1=str(real_dir),
        input2=str(synth_dir),
        fid=True,
        isc=True,       # Inception Score
        verbose=False,
    )
    return {
        "fid": metrics.get("frechet_inception_distance"),
        "is_mean": metrics.get("inception_score_mean"),
        "is_std": metrics.get("inception_score_std"),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compute FID, SSIM, IS for synthetic vs real medical images"
    )
    parser.add_argument("--real_dir", required=True,
                        help="Directory of real reference images")
    parser.add_argument("--synth_dir", required=True,
                        help="Directory of synthetic images")
    parser.add_argument("--modality", required=True,
                        choices=list(MODALITY_PRESETS.keys()),
                        help="Imaging modality preset")
    parser.add_argument("--output", default="results/metrics.csv",
                        help="Output CSV file path")
    parser.add_argument("--scenario", default="",
                        help="Scenario ID (e.g. S01) for labeling output")
    parser.add_argument("--model", default="",
                        help="Model name for labeling output")
    args = parser.parse_args()

    real_dir = Path(args.real_dir)
    synth_dir = Path(args.synth_dir)

    if not real_dir.exists():
        raise FileNotFoundError(f"Real image directory not found: {real_dir}")
    if not synth_dir.exists():
        raise FileNotFoundError(f"Synthetic image directory not found: {synth_dir}")

    preset = MODALITY_PRESETS[args.modality]
    print(f"\nModality: {args.modality} — {preset['description']}")
    print(f"Real images: {real_dir}")
    print(f"Synthetic images: {synth_dir}")

    # FID + IS
    print("\nComputing FID and IS (torch-fidelity)...")
    fid_is = compute_fid_is(real_dir, synth_dir)
    print(f"  FID  = {fid_is['fid']:.4f}" if fid_is["fid"] else "  FID  = N/A")
    print(f"  IS   = {fid_is['is_mean']:.4f} ± {fid_is['is_std']:.4f}"
          if fid_is["is_mean"] else "  IS   = N/A")

    # SSIM
    print("\nComputing SSIM (pairwise, sorted order)...")
    ssim_results = compute_ssim_dataset(real_dir, synth_dir)
    print(f"  SSIM = {ssim_results['ssim_mean']:.4f} ± {ssim_results['ssim_std']:.4f}"
          f"  (n={ssim_results['n_pairs']})"
          if ssim_results["ssim_mean"] is not None else "  SSIM = N/A (no image pairs)")

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "scenario": args.scenario,
        "model": args.model,
        "modality": args.modality,
        "fid": fid_is.get("fid"),
        "is_mean": fid_is.get("is_mean"),
        "is_std": fid_is.get("is_std"),
        "ssim_mean": ssim_results.get("ssim_mean"),
        "ssim_std": ssim_results.get("ssim_std"),
        "n_ssim_pairs": ssim_results.get("n_pairs"),
    }

    write_header = not output_path.exists()
    with open(output_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    print(f"\nResults saved to: {output_path}")

    # Also save per-image SSIM scores
    if ssim_results.get("ssim_scores"):
        ssim_detail_path = output_path.parent / "ssim_per_image.json"
        existing = {}
        if ssim_detail_path.exists():
            with open(ssim_detail_path) as f:
                existing = json.load(f)
        key = f"{args.scenario}_{args.model}_{args.modality}"
        existing[key] = ssim_results["ssim_scores"]
        with open(ssim_detail_path, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"Per-image SSIM saved to: {ssim_detail_path}")


if __name__ == "__main__":
    main()
