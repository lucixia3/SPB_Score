# SPB-RADS Scoring Rubric

## Overview

Each image is scored independently across three domains. Each domain receives a score of 0–3.
**Total score = S + P + B (max 9)**

| Grade | Total score | Clinical use |
|-------|-------------|-------------|
| A | 9 | Unrestricted use |
| B | 7–8 | Conditional use (document caveats) |
| C | 6 | Restricted use |
| D | <6, OR any domain = 0 | Avoid |

> ⚠️ **Critical minimum rule:** If ANY domain receives a score of 0, the image is automatically Grade D, regardless of the total score.

---

## Domain S — Signal

*Does the image behave as a measurement of the physical quantity it purports to represent?*

| Score | Label | Criteria | Examples |
|-------|-------|----------|---------|
| 3 | Correct | Correct modality contrast; realistic noise texture; consistent inter-tissue signal relationships for the stated sequence | Correct T1/T2 gray-white matter contrast; HU values within expected tissue ranges; appropriate MRI echo time effects |
| 2 | Minor deviation | Minor contrast deviation from expected; tissue signal relationships near-correct but not perfect | Slightly elevated background noise; minor inter-sequence inconsistency |
| 1 | Moderate error | Moderate signal errors; inconsistent inter-tissue relationships for the stated modality/sequence | Gray-white matter contrast reversed; FLAIR signal partially unsuppressed in non-pathological CSF |
| 0 | Critical failure | Wrong modality signal behavior; image does not behave as a measurement of the stated physical quantity | Inverted FLAIR contrast throughout; ultrasound image without depth attenuation; CT with MRI-like soft tissue contrast |

---

## Domain P — Physics

*Is the image physically possible under the known laws of the imaging system?*

| Score | Label | Criteria | Examples |
|-------|-------|----------|---------|
| 3 | Correct | All expected acquisition artifacts present; geometry consistent with acquisition parameters; reconstruction features appropriate to stated modality and protocol | Beam-hardening streak artifact adjacent to titanium clip; posterior acoustic shadow behind gallstone; correct geometric distortion pattern |
| 2 | Minor deviation | Minor artifact mismatch; expected artifacts present but displaced or reduced; geometry mostly preserved | Streak artifact present but less pronounced than expected for clip size; minor geometric distortion |
| 1 | Moderate error | Expected artifact absent or incorrectly placed; moderate physics violation | Streak artifact absent but image otherwise consistent; acoustic shadow displaced from stone location |
| 0 | Critical failure | Physically impossible under stated acquisition constraints; geometry violates scanner physics | No beam hardening adjacent to stated titanium clip; no posterior acoustic shadow behind gallstone; free air in dependent spaces in supine patient |

---

## Domain B — Biology

*Does the image depict a real disease process as it manifests in the human body?*

| Score | Label | Criteria | Examples |
|-------|-------|----------|---------|
| 3 | Correct | Anatomically coherent; pathology morphologically and spatially plausible; pathophysiology consistent with known disease mechanisms | Infarct confined to MCA territory; free fluid in Morrison's pouch and paracolic gutters; gallstone at dependent gallbladder pole |
| 2 | Minor deviation | Minor anatomical inconsistency; pathology recognizable and mostly plausible; minor spatial implausibility | Infarct predominantly but not exclusively in MCA territory; fluid distribution mostly correct with minor extension |
| 1 | Moderate error | Moderate biological error; pathology partially implausible in location or morphology | Infarct extending into adjacent territory without variant anatomy justification; fluid in partially incorrect anatomical spaces |
| 0 | Critical failure | Biologically impossible; pathology outside known physiopathology; anatomy inconsistent with any known variant | Infarct outside any recognizable vascular territory; free blood anterior to bowel loops in supine patient (gravity violation); gallbladder polyp mobile at dependent pole (fixed by pedicle in reality) |

---

## Scoring Instructions for Raters

1. Evaluate each domain independently — do not let one domain influence another.
2. Apply the rubric to the specific clinical scenario specified in the prompt, not to generic imaging standards.
3. If the scenario specifies an anatomical variant (e.g., fetal PCA), evaluate Biology based on whether the image is consistent with that variant, not with standard anatomy.
4. For Physics domain: evaluate whether the stated acquisition (modality, protocol, implant) produces the physically expected artifacts. An image without a metallic implant should not be penalized for absent streak artifact.
5. Record any specific failure features observed for each domain score ≤ 1.
6. Apply the critical minimum rule: any domain score of 0 → Grade D.

---

## Inter-Rater Calibration Cases

Before formal rating, all raters should complete the calibration set (9 cases, 3 per modality) provided separately. Discussion of disagreements ≥ 2 points is mandatory before proceeding to formal rating.

---

## Version

SPB-RADS v1.0 — [Date]
Developed at Hospital de la Santa Creu i Sant Pau, Barcelona, Spain.
