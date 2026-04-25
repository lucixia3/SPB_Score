"""
SPB-RADS Statistical Analysis
==============================
Computes:
  - Inter-rater reliability (ICC, Fleiss' kappa)
  - Spearman correlation between SPB-RADS and statistical metrics
  - Discordant case identification
  - Kruskal-Wallis + Dunn post-hoc across modalities

Usage:
    python spb_rads_stats.py \
        --scores_dir results/scores/ \
        --metrics_csv results/metrics.csv \
        --output results/analysis/

Input format:
    scores_dir: directory of CSV files, one per rater, columns:
        image_id, scenario, modality, model, S_score, P_score, B_score
    metrics_csv: output from compute_metrics.py

Output:
    - icc_results.csv
    - kappa_results.csv
    - spearman_results.csv
    - discordant_cases.csv
    - kruskal_dunn_results.csv
"""

import argparse
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import spearmanr, kruskal
import scikit_posthocs as sp
from sklearn.metrics import cohen_kappa_score

warnings.filterwarnings("ignore")


# ── Inter-rater reliability ───────────────────────────────────────────────────

def compute_icc(ratings_matrix: np.ndarray, icc_type: str = "ICC(2,1)") -> dict:
    """
    Compute ICC for a ratings matrix (images x raters).
    Implements two-way mixed model, absolute agreement (ICC(2,1)).
    """
    n, k = ratings_matrix.shape  # n images, k raters
    grand_mean = ratings_matrix.mean()

    # Sum of squares
    ss_rows = k * np.sum((ratings_matrix.mean(axis=1) - grand_mean) ** 2)
    ss_cols = n * np.sum((ratings_matrix.mean(axis=0) - grand_mean) ** 2)
    ss_total = np.sum((ratings_matrix - grand_mean) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    # Mean squares
    ms_rows = ss_rows / (n - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    # ICC(2,1) absolute agreement
    icc = (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error)

    # 95% CI using F distribution
    f = ms_rows / ms_error
    df1 = n - 1
    df2 = (n - 1) * (k - 1)
    alpha = 0.05

    f_lower = f / stats.f.ppf(1 - alpha / 2, df1, df2)
    f_upper = f * stats.f.ppf(1 - alpha / 2, df2, df1)

    icc_lower = (f_lower - 1) / (f_lower + k - 1)
    icc_upper = (f_upper - 1) / (f_upper + k - 1)

    return {
        "icc": round(icc, 4),
        "ci_lower": round(icc_lower, 4),
        "ci_upper": round(icc_upper, 4),
        "n_images": n,
        "n_raters": k,
    }


def fleiss_kappa(ratings_df: pd.DataFrame,
                 grade_col: str = "grade",
                 image_col: str = "image_id",
                 rater_col: str = "rater_id") -> float:
    """Compute Fleiss' kappa for categorical grade agreement."""
    categories = sorted(ratings_df[grade_col].unique())
    images = sorted(ratings_df[image_col].unique())
    n = len(images)
    k = len(categories)

    # Build matrix n_images x n_categories
    matrix = np.zeros((n, k))
    for i, img in enumerate(images):
        img_ratings = ratings_df[ratings_df[image_col] == img][grade_col].values
        for rating in img_ratings:
            j = categories.index(rating)
            matrix[i, j] += 1

    n_raters = matrix.sum(axis=1)
    n_raters_per_image = n_raters[0]  # assume same number per image

    # Proportion of ratings in each category
    p_j = matrix.sum(axis=0) / (n * n_raters_per_image)

    # P_i for each image
    P_i = (np.sum(matrix ** 2, axis=1) - n_raters_per_image) / (
        n_raters_per_image * (n_raters_per_image - 1)
    )

    P_bar = P_i.mean()
    P_e = np.sum(p_j ** 2)

    kappa = (P_bar - P_e) / (1 - P_e)
    return round(kappa, 4)


# ── Spearman correlation ───────────────────────────────────────────────────────

def compute_spearman_correlations(merged_df: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman rho between SPB-RADS total and FID, SSIM, IS."""
    results = []
    for metric in ["fid", "ssim_mean", "is_mean"]:
        if metric not in merged_df.columns:
            continue
        df_clean = merged_df[["spb_total", metric]].dropna()
        if len(df_clean) < 5:
            continue
        rho, pval = spearmanr(df_clean["spb_total"], df_clean[metric])
        results.append({
            "metric": metric,
            "spearman_rho": round(rho, 4),
            "p_value": round(pval, 4),
            "n": len(df_clean),
        })
    return pd.DataFrame(results)


# ── Discordant cases ───────────────────────────────────────────────────────────

def identify_discordant_cases(merged_df: pd.DataFrame,
                               fid_percentile: float = 25.0,
                               ssim_percentile: float = 75.0) -> pd.DataFrame:
    """
    Discordant: high statistical fidelity (FID <= 25th pct, SSIM >= 75th pct)
    AND SPB-RADS grade D.
    """
    df = merged_df.copy()

    fid_threshold = np.nanpercentile(df["fid"].dropna(), fid_percentile) \
        if "fid" in df.columns else None
    ssim_threshold = np.nanpercentile(df["ssim_mean"].dropna(), ssim_percentile) \
        if "ssim_mean" in df.columns else None

    conditions = df["grade"] == "D"
    if fid_threshold is not None:
        conditions &= df["fid"] <= fid_threshold
    if ssim_threshold is not None:
        conditions &= df["ssim_mean"] >= ssim_threshold

    discordant = df[conditions].copy()
    discordant["fid_threshold"] = fid_threshold
    discordant["ssim_threshold"] = ssim_threshold

    return discordant


# ── Kruskal-Wallis + Dunn ─────────────────────────────────────────────────────

def kruskal_dunn_by_modality(df: pd.DataFrame) -> dict:
    """
    Test whether SPB-RADS total differs across modalities.
    Kruskal-Wallis + Dunn post-hoc with Bonferroni correction.
    """
    modalities = df["modality"].unique()
    groups = [df[df["modality"] == m]["spb_total"].dropna().values
              for m in modalities]

    stat, pval = kruskal(*groups)

    # Dunn post-hoc
    dunn = sp.posthoc_dunn(
        df, val_col="spb_total", group_col="modality", p_adjust="bonferroni"
    )

    return {
        "kruskal_stat": round(stat, 4),
        "kruskal_pval": round(pval, 6),
        "dunn_matrix": dunn,
        "modalities": list(modalities),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SPB-RADS statistical analysis"
    )
    parser.add_argument("--scores_dir", required=True,
                        help="Directory of rater score CSV files")
    parser.add_argument("--metrics_csv", required=True,
                        help="Metrics CSV from compute_metrics.py")
    parser.add_argument("--output", default="results/analysis/",
                        help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load scores ────────────────────────────────────────────────────────
    score_files = list(Path(args.scores_dir).glob("*.csv"))
    if not score_files:
        print(f"No score CSV files found in {args.scores_dir}")
        return

    all_scores = []
    for i, f in enumerate(score_files):
        df = pd.read_csv(f)
        df["rater_id"] = f.stem
        all_scores.append(df)
    scores_df = pd.concat(all_scores, ignore_index=True)

    # Compute SPB total and grade
    scores_df["spb_total"] = (scores_df["S_score"] +
                               scores_df["P_score"] +
                               scores_df["B_score"])
    scores_df["grade"] = scores_df.apply(
        lambda r: "D" if (r["spb_total"] < 6 or
                          r["S_score"] == 0 or
                          r["P_score"] == 0 or
                          r["B_score"] == 0)
        else ("C" if r["spb_total"] == 6
              else ("B" if r["spb_total"] <= 8
                    else "A")),
        axis=1
    )

    # ── ICC on total score ─────────────────────────────────────────────────
    print("\n── Inter-Rater Reliability ──")
    rater_ids = scores_df["rater_id"].unique()
    image_ids = scores_df["image_id"].unique()

    icc_results = []
    for modality in ["all"] + list(scores_df["modality"].unique()):
        subset = scores_df if modality == "all" \
            else scores_df[scores_df["modality"] == modality]

        images_mod = subset["image_id"].unique()
        raters_mod = subset["rater_id"].unique()

        if len(raters_mod) < 2 or len(images_mod) < 5:
            continue

        # Build images x raters matrix of total scores
        matrix_rows = []
        for img in images_mod:
            row = []
            for r in raters_mod:
                val = subset[(subset["image_id"] == img) &
                             (subset["rater_id"] == r)]["spb_total"].values
                row.append(val[0] if len(val) > 0 else np.nan)
            if not any(np.isnan(row)):
                matrix_rows.append(row)

        if len(matrix_rows) < 5:
            continue

        matrix = np.array(matrix_rows)
        icc_res = compute_icc(matrix)
        icc_res["modality"] = modality
        icc_results.append(icc_res)
        print(f"  ICC ({modality}): {icc_res['icc']} "
              f"[{icc_res['ci_lower']}–{icc_res['ci_upper']}]")

    icc_df = pd.DataFrame(icc_results)
    icc_df.to_csv(output_dir / "icc_results.csv", index=False)

    # ── Fleiss' kappa ─────────────────────────────────────────────────────
    kappa = fleiss_kappa(scores_df)
    print(f"\n  Fleiss' kappa (grade): {kappa}")
    pd.DataFrame([{"fleiss_kappa": kappa}]).to_csv(
        output_dir / "kappa_results.csv", index=False
    )

    # ── Merge with metrics ─────────────────────────────────────────────────
    metrics_df = pd.read_csv(args.metrics_csv)
    # Average scores across raters per image
    avg_scores = scores_df.groupby(
        ["image_id", "scenario", "modality", "model"]
    ).agg(
        spb_total=("spb_total", "mean"),
        grade=("grade", lambda x: x.mode()[0])
    ).reset_index()

    merged = avg_scores.merge(
        metrics_df, on=["scenario", "modality", "model"], how="left"
    )

    # ── Spearman correlations ──────────────────────────────────────────────
    print("\n── Spearman Correlations (SPB-RADS total vs metrics) ──")
    spearman_df = compute_spearman_correlations(merged)
    print(spearman_df.to_string(index=False))
    spearman_df.to_csv(output_dir / "spearman_results.csv", index=False)

    # ── Discordant cases ───────────────────────────────────────────────────
    print("\n── Discordant Cases (high fidelity, grade D) ──")
    discordant_df = identify_discordant_cases(merged)
    print(f"  N discordant: {len(discordant_df)} / {len(merged)} "
          f"({100*len(discordant_df)/len(merged):.1f}%)")
    discordant_df.to_csv(output_dir / "discordant_cases.csv", index=False)

    # ── Kruskal-Wallis ─────────────────────────────────────────────────────
    print("\n── Kruskal-Wallis (SPB-RADS total by modality) ──")
    kw_results = kruskal_dunn_by_modality(merged)
    print(f"  H = {kw_results['kruskal_stat']}, "
          f"p = {kw_results['kruskal_pval']}")
    print("\n  Dunn post-hoc (Bonferroni):")
    print(kw_results["dunn_matrix"].round(4))

    kw_results["dunn_matrix"].to_csv(output_dir / "dunn_posthoc.csv")
    pd.DataFrame([{
        "kruskal_stat": kw_results["kruskal_stat"],
        "kruskal_pval": kw_results["kruskal_pval"],
    }]).to_csv(output_dir / "kruskal_results.csv", index=False)

    print(f"\nAll results saved to: {output_dir}")


if __name__ == "__main__":
    main()
