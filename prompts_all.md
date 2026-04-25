# SPB-RADS Standardized Prompt Templates

All prompts follow the structure:
`[view] [modality] [protocol], [pathology], [specific anatomical/physical constraint], [clinical context]`

Identical text submitted to all models. Minor interface adaptations (e.g., character limits, content filters) are documented in study notes.

---

## Brain MRI / CT

### S01 — Acute MCA Infarct, Standard Anatomy
**Target domain failure:** Biology (infarct outside recognized territory)

```
Axial diffusion-weighted MRI (DWI, b=1000) of the brain at 1.5T, showing
acute ischemic infarction in the left middle cerebral artery (MCA) territory.
The infarct appears as a well-defined area of restricted diffusion
(hyperintense on DWI) involving the left MCA territory: lateral frontal
lobe, parietal lobe, and lateral temporal lobe. The infarct must respect
the vascular boundary and must NOT involve the occipital lobe or cerebellum,
which are supplied by different arteries. Realistic DWI noise texture and
b0 image appearance at 1.5T.
```

---

### S02 — Acute MCA Infarct + Fetal PCA Variant (Circle of Willis)
**Target domain failure:** Biology (territory not adjusted to variant anatomy)

```
Axial diffusion-weighted MRI (DWI, b=1000) of the brain at 1.5T, showing
acute right MCA territory ischemic infarction. This patient has a right
fetal-type posterior cerebral artery: the right occipital lobe is supplied
by the right internal carotid artery (ICA), NOT by the basilar artery.
Therefore the infarct is strictly confined to the right MCA territory and
must NOT extend into the right occipital lobe, which is fed by a separate
vessel in this patient. The right occipital cortex appears normal (no
restricted diffusion there). Realistic DWI noise texture at 1.5T.
```

---

### S03 — Post-Aneurysm Clip, Metallic Streak Artifact
**Target domain failure:** Physics (streak artifact absent)

```
Axial non-contrast CT of the brain, brain window (W80, L35),
post-operative appearance after surgical clipping of a right middle
cerebral artery (MCA) bifurcation aneurysm. The titanium aneurysm clip
MUST produce characteristic beam-hardening streak artifacts radiating in
all directions from the clip site — this is a physical inevitability on
any CT scanner due to the high atomic number of titanium. The streaks
must be pronounced and star-shaped, extending several centimeters from
the clip. No other pathology. Realistic CT noise texture.
```

---

## Abdominal CT

### S04 — Hemoperitoneum, Supine Patient
**Target domain failure:** Biology (fluid not in dependent spaces)

```
Axial non-contrast CT of the abdomen and pelvis, supine patient,
soft tissue window (W400, L60). Hemoperitoneum: free blood in the
peritoneal cavity. The blood MUST accumulate in the most dependent
anatomical spaces for a supine patient — primarily Morrison's pouch
(hepatorenal space between right lobe of liver and right kidney),
the pouch of Douglas (rectovesical or rectouterine space), and the
paracolic gutters. The blood appears hyperdense (50–70 HU) relative
to bowel. The fluid must NOT appear anterior to the bowel loops or
in non-dependent spaces — gravity dictates distribution in a supine
patient. Bowel loops float anteriorly. Axial slice at kidney level.
```

---

### S05 — Pneumoperitoneum, Perforated Viscus
**Target domain failure:** Physics + Biology (no free air under diaphragm, no Rigler sign)

```
Axial CT of the upper abdomen, supine patient, lung window (W1500, L-600),
showing pneumoperitoneum from a perforated hollow viscus. Free air MUST
be visible: (1) anterior to the liver and under the right hemidiaphragm —
in a supine patient, free air rises to the most non-dependent position;
(2) the Rigler sign should be present — air visible on both sides of the
bowel wall where loops are surrounded by free intraperitoneal air. The
liver parenchyma appears normal. Peritoneal fat stranding is present.
Free air must NOT appear in dependent posterior spaces. Realistic CT noise.
```

---

### S06 — Acute Necrotizing Pancreatitis
**Target domain failure:** Biology (necrosis absent or wrong distribution)

```
Axial contrast-enhanced CT of the abdomen, portal venous phase
(W400, L60), showing acute necrotizing pancreatitis. The pancreatic
body and tail show heterogeneous enhancement with areas of non-enhancement
(necrosis) — these non-enhancing areas appear hypodense relative to viable
pancreatic tissue. Peripancreatic fat stranding and inflammatory changes
surround the pancreas. The necrotic areas must be in the expected anatomical
location of the pancreas (retroperitoneal, crossing the midline at L1–L2
level). Peripancreatic fluid collections may be present in the lesser sac
and left anterior pararenal space. Realistic contrast-enhanced CT appearance.
```

---

## Abdominal Ultrasound

### S07 — Gallbladder Polyp, Pedunculated
**Target domain failure:** Biology + Physics (polyp mobile or without pedicle)

```
B-mode abdominal ultrasound of the gallbladder, transverse view, showing
a pedunculated gallbladder polyp. The polyp MUST have a visible narrow
stalk (pedicle) attaching it to the gallbladder wall, projecting into
the anechoic bile-filled lumen. It must NOT cast a posterior acoustic
shadow — polyps do not shadow, unlike gallstones, because they do not
attenuate sound the same way. It must NOT be located at the dependent
portion of the gallbladder — unlike gallstones which fall to the most
dependent point due to gravity, polyps are fixed to the wall by their
pedicle regardless of patient position. Realistic B-mode speckle texture
and depth attenuation.
```

---

### S08 — Cholelithiasis, Posterior Acoustic Shadow
**Target domain failure:** Physics (no posterior acoustic shadow)

```
B-mode abdominal ultrasound of the gallbladder showing cholelithiasis.
A bright echogenic gallstone sits at the most dependent portion of the
gallbladder (stones fall to the lowest point due to gravity). Behind the
stone there MUST be a well-defined posterior acoustic shadow — a dark
vertical band extending deep to the stone — caused by the acoustic
impedance mismatch between the stone and surrounding bile. This shadow
is a mandatory physical artifact of the impedance mismatch; it is NOT
optional. The gallbladder wall is thin and smooth. Realistic B-mode
speckle texture, depth attenuation, and echogenicity of surrounding structures.
```

---

### S09 — Free Fluid in Morrison's Pouch
**Target domain failure:** Biology + Physics (no anechoic stripe in hepatorenal space)

```
B-mode abdominal ultrasound showing free intraperitoneal fluid in Morrison's
pouch (the hepatorenal space), between the inferior edge of the right
hepatic lobe and the upper pole of the right kidney. The free fluid MUST
appear as a wedge-shaped anechoic (black) stripe in this potential space —
this is the most dependent peritoneal space in a supine patient and the
first location where free intraperitoneal fluid accumulates due to gravity.
The fluid layer tapers at the margins. The right hepatic lobe and right
kidney are clearly visible as adjacent structures. Realistic B-mode speckle
texture, depth attenuation, and organ echogenicity.
```

---

## Prompt Template for New Scenarios

```
[Anatomical view] [Imaging modality] [Sequence/protocol] of the [anatomy],
[clinical scenario / pathology].
[Specific physical constraint 1 — state what MUST be present and why].
[Specific physical constraint 2 — state what must NOT be present and why].
[Anatomical constraint — location relative to landmarks].
[Acquisition parameters — window, field strength, transducer].
Realistic [modality]-specific noise texture and image appearance.
```
