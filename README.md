# TakeMeter 🎯

TakeMeter is an AI-201 Project 3 classifier. This repository holds **everything that lives outside the Colab notebook**: the planning document, the labeled dataset, and the evaluation artifacts the notebook produces.

The notebook itself (training/evaluation code) runs in Google Colab. After each run you download the output files from Colab and drop them into [`results/`](results/) so the repo always reflects the latest evaluation.

---

## Repository structure

```
ai201-project3-takemeter/
├── planning.md            # Project spec: problem, labels, dataset plan, eval plan
├── README.md              # You are here
├── collect.py             # Pulls r/Cricket comments into data/dataset.csv (PRAW)
├── requirements.txt       # praw, python-dotenv
├── .env.example           # Template for Reddit API credentials
├── data/
│   └── dataset.csv        # Labeled dataset (input to the notebook)
└── results/               # Artifacts downloaded from Colab after each run
    ├── evaluation_results.json
    └── confusion_matrix.png
```

The community is **r/Cricket**, and the unit of classification is a **comment** (not a
post) — that's where the quality variation lives. `collect.py` pulls comments from the
threads listed in its `THREADS` array; edit that list to add a match thread and a
discussion thread alongside the anchor post so the labels stay balanced.

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

1. **Collect:** create a Reddit script app, copy `.env.example` → `.env`, add thread URLs to
   `THREADS` in [`collect.py`](collect.py), then:
   ```bash
   pip install -r requirements.txt
   python collect.py        # writes ~200+ comments to data/dataset.csv (label column blank)
   ```
2. **Read 30–40 first**, then finalize your label set in [`planning.md`](planning.md).
3. **Label:** fill in the `label` column of [`data/dataset.csv`](data/dataset.csv) and commit it.
4. Open the notebook in Colab, upload `dataset.csv`, run training + evaluation.
5. Download `evaluation_results.json` and `confusion_matrix.png` from Colab into [`results/`](results/).
6. Commit the updated artifacts so the repo shows the current results.

---

## Latest results

_Fill this in once you have your first Colab run:_

- **Accuracy:** —
- **Macro F1:** —
- **Confusion matrix:** see [`results/confusion_matrix.png`](results/confusion_matrix.png)
