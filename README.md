# TakeMeter

TakeMeter is an AI-201 Project 3 classifier that measures discourse quality in **r/Cricket**. It classifies comments into three categories: `analysis`, `hot_take`, and `reaction`.

This repository holds everything outside the Colab notebook: the planning document, the labeled dataset, and the evaluation artifacts the notebook produces.

**Colab notebook:** _(paste the shareable Colab link here after training)_

---

## Repository structure

```
ai201-project3-takemeter/
├── planning.md            # Project spec: problem, labels, dataset plan, eval plan
├── README.md              # You are here
├── data/
│   └── dataset.csv        # Labeled dataset (input to the notebook)
└── results/               # Artifacts downloaded from Colab after each run
    ├── evaluation_results.json
    └── confusion_matrix.png
```

---

## Label taxonomy

The classifier distinguishes three types of discourse in r/Cricket comments:

| Label | Definition | Example |
|---|---|---|
| `analysis` | A structured argument backed by statistics, historical data, or tactical observation. Evidence is specific and verifiable. | *"Root's conversion rate from 50s to 100s is 43%, placing him top-10 among batters with 100+ innings. The criticism that he doesn't convert is driven by specific memorable failures, not the overall pattern."* |
| `hot_take` | A bold, confident opinion stated without supporting evidence. Asserts rather than argues — may be correct, but doesn't reason from data. Often uses superlatives or absolute language. | *"Rohit Sharma is the most overrated Test opener in cricket history. He collapses abroad every single time. His away record doesn't back the legend at all."* |
| `reaction` | An immediate emotional response to a specific live moment, score update, or result. Primarily expresses feeling — time-sensitive, present-tense, often capitalised or exclamatory. | *"YESSSSS!! What an absolute catch!! He came from nowhere!! I cannot believe what I just watched!!"* |

These three labels are mutually exclusive and cover the vast majority of r/Cricket discourse. The distinction matters to people in the community: members genuinely value analytical posts differently from hot takes, and both differently from live match reactions.

---

## Dataset

**Source:** r/Cricket — comments drawn from three thread types:
- Milestone and GOAT-debate threads (Root's 14,000 runs, Kohli records, era comparisons)
- Series discussion threads (India vs England 2024, Ashes 2023)
- Live match and post-match reaction threads

**Size:** 211 labeled examples

**Label distribution:**

| Label | Count | % |
|---|---|---|
| `analysis` | 70 | 33.2% |
| `hot_take` | 71 | 33.6% |
| `reaction` | 70 | 33.2% |

**Train/val/test split:** 80% / 10% / 10% — stratified by label (handled in the notebook)

**Labeling process:** Each comment was assigned a label according to the definitions above. The key decision rule for the hardest boundary (analysis vs. hot_take when a stat is present): if the statistic is the central argument — you'd lose the claim without it — label `analysis`. If the stat is decorative, appended to what is fundamentally an opinion, label `hot_take`.

---

## Hard labeling decisions (genuine edge cases)

**1.** *"Kohli's century drought from 2020 to 2022 proves he needed that break. He came back refreshed and immediately started scoring. Mental health in cricket is real."*
→ **`hot_take`** — strong causal claim asserted with zero data. Framed as insight but no statistical support for the drought-break-form chain.

**2.** *"Root's record against left-arm spin (28.4) vs right-arm spin (44.6) reveals a consistent technical weakness — he plays across the line against deliveries that angle away from him."*
→ **`analysis`** — specific, verifiable numbers are the primary substance. The technique inference follows directly from the stat rather than being asserted independently.

**3.** *"He's so good. Honestly. When he's in form like this I would pay anything just to watch him bat today."*
→ **`reaction`** — the phrasing "right now" and "like this" signals an in-the-moment response to live play. When a comment is anchored to the present moment rather than making a general judgment, prefer `reaction` over `hot_take`.

---

## Model

**Base model:** `distilbert-base-uncased` (HuggingFace)

**Training approach:** Standard sequence classification fine-tuning using the `transformers` library. The `[CLS]` token representation feeds into a 3-way classification head.

**Key hyperparameter decisions:**
- **Learning rate: 2e-5** — standard for DistilBERT on small datasets; 3e-5 risks overshooting on 168 training examples
- **Epochs: 5** — enough to converge without memorising a 168-example training set
- **Batch size: 16** — balances Colab T4 memory with stable gradient estimates

**Baseline:** Zero-shot classification using `llama-3.3-70b-versatile` via Groq API — same test set, no task-specific training.

---

## Latest results

| Metric | Fine-tuned DistilBERT | Zero-shot Groq baseline |
|---|---|---|
| Accuracy | **93.8%** | 100% |
| Macro F1 | **0.94** | 1.00 |
| Wrong predictions | 2 / 32 | 0 / 32 |

**Per-class (fine-tuned model):**

| Label | Precision | Recall | F1 |
|---|---|---|---|
| analysis | 1.00 | 0.82 | 0.90 |
| hot_take | 0.85 | 1.00 | 0.92 |
| reaction | 1.00 | 1.00 | 1.00 |

Confusion matrix: see [`results/confusion_matrix.png`](results/confusion_matrix.png)

**Note on baseline vs fine-tuned:** The zero-shot Groq baseline used `llama-3.3-70b-versatile` (70B parameters) with a detailed prompt. The fine-tuned model used `distilbert-base-uncased` (66M parameters) trained on 147 examples. The 2-example gap on a 32-example test set is not statistically significant — both models well exceed the 70% accuracy / 0.65 macro F1 success criteria.

---

## Workflow

1. Upload `data/dataset.csv` to Colab
2. Set runtime to **T4 GPU** (Runtime → Change runtime type)
3. Add `GROQ_API_KEY` to Colab Secrets
4. Run all cells — training takes ~5-15 min on T4
5. Download `evaluation_results.json` and `confusion_matrix.png` into `results/`
6. Commit the artifacts and fill in the results table above
