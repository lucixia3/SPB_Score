# SPB-RADS: Signal–Physics–Biology Radiology Assessment and Data System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Evaluation of Synthetic Radiological Images: A Critical Review of Current Metrics and the SPB-RADS Framework for Clinical Plausibility Assessment**


---

## What is SPB-RADS?

SPB-RADS is a structured clinical plausibility framework for evaluating AI-generated synthetic medical images. Unlike statistical fidelity metrics (FID, SSIM, IS), which measure distributional resemblance, SPB-RADS evaluates images across three domains that determine whether an image is clinically usable:

| Domain | What it assesses |
|--------|-----------------|
| **S — Signal** | Does the image behave as a measurement of the physical quantity it represents? (tissue contrast, noise texture, inter-tissue signal consistency) |
| **P — Physics** | Is the image physically possible under the laws of the imaging system? (beam-hardening artifacts, acoustic shadowing, geometric constraints) |
| **B — Biology** | Does the image depict a real disease process as it manifests in the human body? (vascular territory logic, gravitational fluid distribution, pathological morphology) |

Each domain is scored 0–3. Total score (0–9) maps to four grades:

| Grade | Score | Clinical use |
|-------|-------|-------------|
| **A** | 9 | Unrestricted |
| **B** | 7–8 | Conditional (with caveats) |
| **C** | 6 | Restricted |
| **D** | <6, or any domain = 0 | Avoid |

> **Critical minimum rule:** any domain score of 0 → Grade D, regardless of total.

---

## Repository Structure

```
spb_rads/
├── README.md
├── LICENSE
│
├── spb_rads_rubric.md          # Full scoring rubric (human-readable)
├── spb_rads_rubric.csv         # Machine-readable rubric
└── scoring_sheet_template.xlsx # Excel template for radiologist annotation
│

├── prompts_all.md              # All 9 standardized prompts
└── prompt_template.md          # Template for new scenarios
│
├── compute_metrics.py          # FID, SSIM, IS computation
├── spb_rads_stats.py           # ICC, kappa, Spearman analysis
├── requirements.txt
└── README_eval.md
│
└── spb_rads_framework.pdf      # Full framework document

```

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/[username]/spb-rads.git
cd spb-rads
```

### 2. Install dependencies
```bash
pip install -r evaluation/requirements.txt
```

### 3. Compute statistical metrics (FID, SSIM, IS)
```bash
python evaluation/compute_metrics.py \
    --real_dir /path/to/real_images \
    --synth_dir /path/to/synthetic_images \
    --modality brain_mri \
    --output results/metrics.csv
```

### 4. Score images with SPB-RADS
Use the scoring sheet in `scoring/scoring_sheet_template.xlsx` with the rubric in `scoring/spb_rads_rubric.md`.

### 5. Analyse inter-rater reliability and metric-SPB-RADS discordance
```bash
python evaluation/spb_rads_stats.py \
    --scores_dir results/scores/ \
    --metrics_csv results/metrics.csv \
    --output results/analysis/
```

---

## Proposed Validation Scenarios

Nine clinical imaging scenarios are proposed as a structured benchmark:

| ID | Modality | Scenario | Expected failure domain |
|----|----------|----------|------------------------|
| S01 | Brain MRI DWI | Acute MCA infarct, standard anatomy | Biology |
| S02 | Brain MRI DWI | Acute MCA infarct + fetal PCA (CoW variant) | Biology |
| S03 | Brain NCCT | Post-aneurysm clip, streak artifact | Physics |
| S04 | Abdominal CT | Hemoperitoneum, supine patient | Biology |
| S05 | Abdominal CT | Pneumoperitoneum, perforated viscus | Physics + Biology |
| S06 | Abdominal CT | Acute necrotizing pancreatitis | Biology |
| S07 | Ultrasound | Gallbladder polyp, pedunculated | Biology + Physics |
| S08 | Ultrasound | Cholelithiasis, posterior acoustic shadow | Physics |
| S09 | Ultrasound | Free fluid in Morrison's pouch | Biology + Physics |

See `prompts/prompts_all.md` for full standardized prompt text for each scenario.

---

## Reference Datasets (Open Access)

| Modality | Dataset | URL |
|----------|---------|-----|
| Brain MRI DWI | ISLES 2022 | https://isles-challenge.org |
| Brain MRI lesion | ATLAS v2.0 | https://openneuro.org |
| Brain NCCT | CQ500 | https://headctstudy.qure.ai |
| Abdominal CT | CT-ORG (TCIA) | https://cancerimagingarchive.net |
| Abdominal US | Gallbladder US dataset | https://kaggle.com |



---

## License

MIT License. See [LICENSE](LICENSE).

## Contacts

Josep Munuera · jmunuera@santpau.cat · Hospital de la Santa Creu i Sant Pau, Barcelona
Lucia Borrego · lborrego@santpau.cat · Hospital de la Santa Creu i Sant Pau, Barcelona

