# TakeMeter 🎯

TakeMeter is an AI-201 Project 3 classifier. This repository holds **everything that lives outside the Colab notebook**: the planning document, the labeled dataset, and the evaluation artifacts the notebook produces.

The notebook itself (training/evaluation code) runs in Google Colab. After each run you download the output files from Colab and drop them into [`results/`](results/) so the repo always reflects the latest evaluation.

---

## Repository structure

```
ai201-project3-takemeter/
├── planning.md            # Project spec: problem, labels, dataset plan, eval plan
├── README.md              # You are here
├── data/
│   └── dataset.csv        # Labeled dataset, collected by hand (input to the notebook)
└── results/               # Artifacts downloaded from Colab after each run
    ├── evaluation_results.json
    └── confusion_matrix.png
```

The community is **r/Cricket**, and the unit of classification is a **comment** (not a
post) — that's where the quality variation lives. Data is collected **manually** (copy-paste
of public comments) — no API or scraper, per the assignment, which keeps you close to the
text while you read it.

> The Colab notebook is **not** stored here — keep it in Google Drive / Colab and link it below.

**Colab notebook:** _(paste the shareable Colab link here)_

---

## The files

| File | What it is | Where it comes from |
|---|---|---|
| [`planning.md`](planning.md) | The project spec: problem statement, label set, dataset construction, and evaluation plan. | Written by hand before any code. |
| [`data/dataset.csv`](data/dataset.csv) | The labeled dataset — one row per example, with a text/feature column and a ground-truth label column. | Built by hand / collected, then uploaded to Colab. |
| [`results/evaluation_results.json`](results/evaluation_results.json) | Metrics from the latest evaluation run (accuracy, precision/recall/F1 per class, etc.). | Downloaded from Colab. |
| [`results/confusion_matrix.png`](results/confusion_matrix.png) | Confusion matrix visualization for the latest run. | Downloaded from Colab. |

---

## Workflow

1. **Collect (manual, ~1–2 hrs):** open 3–5 public r/Cricket threads and copy comments into a
   spreadsheet — one comment per row. Pull from a mix so the labels stay balanced:
   - the anchor milestone thread (Root's 14,000 — reaction + GOAT-debate takes)
   - a recent **match / post-match thread** (emotional reactions, selection/umpiring gripes)
   - a **discussion / debate thread** (reasoned arguments, analysis)

   Skip deleted/`[removed]` comments, AutoMod, and one-word replies. **Read as you copy** —
   this is the 30–40-comment read that tells you what your labels should be.
2. **Define labels:** once you've seen the spread, finalize the label set in [`planning.md`](planning.md).
3. **Label + export:** fill the `label` column and export to [`data/dataset.csv`](data/dataset.csv)
   (columns: `text`, `label`, `source_url`), then commit it.
4. Open the notebook in Colab, upload `dataset.csv`, run training + evaluation.
5. Download `evaluation_results.json` and `confusion_matrix.png` from Colab into [`results/`](results/).
6. Commit the updated artifacts so the repo shows the current results.

> **Collection rules (from the assignment):** public posts only — no private channels or
> authenticated content. Manual copy-paste (or a scraper if you're comfortable), but don't let
> collection become a coding project.

---

## Latest results

_Fill this in once you have your first Colab run:_

- **Accuracy:** —
- **Macro F1:** —
- **Confusion matrix:** see [`results/confusion_matrix.png`](results/confusion_matrix.png)
