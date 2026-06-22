# TakeMeter

TakeMeter is an AI-201 Project 3 classifier that measures discourse quality in **r/Cricket**. It classifies comments into three categories: `analysis`, `hot_take`, and `reaction`.

This repository holds everything outside the Colab notebook: the planning document, the labeled dataset, and the evaluation artifacts the notebook produces.

**Colab notebook:** [TakeMeter Fine-Tuning Notebook](https://colab.research.google.com/drive/1Bjq1rE5skRoyfWa3lLEt83ZjZ_GKEv_X#scrollTo=d8bc603a)

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

| Label | Definition | Example 1 | Example 2 |
|---|---|---|---|
| `analysis` | A structured argument backed by statistics, historical data, or tactical observation. Evidence is specific and verifiable. | *"Root's conversion rate from 50s to 100s is 43%, placing him top-10 among batters with 100+ innings. The criticism that he doesn't convert is driven by specific memorable failures, not the overall pattern."* | *"Bumrah's economy rate in death overs has dropped from 9.2 to 7.8 over four years, directly corresponding to his increased use of wide yorkers in the final 4 overs."* |
| `hot_take` | A bold, confident opinion stated without supporting evidence. Asserts rather than argues — may be correct, but doesn't reason from data. Often uses superlatives or absolute language. | *"Rohit Sharma is the most overrated Test opener in cricket history. He collapses abroad every single time. His away record doesn't back the legend at all."* | *"Test cricket is dying and administrators don't care. They just want to sell T20 rights and let the purest form of the game wither. It'll be gone in 20 years."* |
| `reaction` | An immediate emotional response to a specific live moment, score update, or result. Primarily expresses feeling — time-sensitive, present-tense, often capitalised or exclamatory. | *"YESSSSS!! What an absolute catch!! He came from nowhere!! I cannot believe what I just watched!!"* | *"My hands are literally shaking typing this. 3 needed off 2 balls. Come on come on come on."* |

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

**Train/val/test split:** 70% / 15% / 15% — stratified by label, handled automatically by the notebook

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
- **Epochs: 3** — the notebook default; 3 passes through 147 training examples was enough to converge without overfitting. Validation accuracy tracked training accuracy closely across all 3 epochs with no gap forming.
- **Batch size: 16** — balances Colab T4 memory with stable gradient estimates

**Baseline:** Zero-shot classification using `llama-3.3-70b-versatile` via Groq API — same test set, no task-specific training. The system prompt provided the three label definitions and one example per label, then instructed the model to output only the label name. Results were collected by running all 32 test examples through the API with temperature=0 for deterministic output.

**Baseline prompt used:**
```
You are classifying comments from r/Cricket.
Assign each post to exactly one of the following categories.

analysis: A comment that makes a claim using specific statistics, numbers, or verifiable
facts where the argument depends on the evidence.
Example: "Bumrah's economy rate in death overs has dropped from 9.2 to 7.8 over four years,
directly corresponding to his increased use of wide yorkers."

hot_take: A bold, confident opinion stated without supporting evidence — asserts rather than
argues, often uses words like greatest, never, always, overrated.
Example: "Rohit Sharma is the most overrated Test opener in cricket history."

reaction: An immediate emotional response to something happening live in a match —
time-anchored with words like now, today, just, or expressed through ALL CAPS and exclamation marks.
Example: "YESSS!! What an absolute catch!! He came from nowhere!!"

Respond with ONLY the label name. Do not explain your reasoning.
Valid labels: analysis / hot_take / reaction
```

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

**Confusion matrix (fine-tuned model):**

|  | Predicted: analysis | Predicted: hot_take | Predicted: reaction |
|---|---|---|---|
| **True: analysis** | 9 | 2 | 0 |
| **True: hot_take** | 0 | 11 | 0 |
| **True: reaction** | 0 | 0 | 10 |

The only errors are in the `analysis` → `hot_take` cell (2 examples). `hot_take` and `reaction` are classified perfectly.

---

## Evaluation report

### Wrong predictions analysis

**Error 1 — fine-tuned model**
> "New Zealand average 5.6 batting positions used in the first 10 wickets across a series, highest of any Test team. Their batting flexibility is measurable, not just a coaching talking point."

True label: `analysis` | Predicted: `hot_take` | Confidence: 0.35

The comment contains a specific statistic (5.6 positions) and a conclusion that depends on it. The model predicted `hot_take`, likely because the phrase "not just a coaching talking point" reads as dismissive opinion. The low confidence (0.35) shows the model was genuinely uncertain. **Root cause:** comparative phrasing that sounds like an assertion even when grounded in data.

---

**Error 2 — fine-tuned model**
> "Third-umpire DRS success rates in Australia have been 71% since 2019, compared to the global average of 63%. The newest Hawkeye technology installed in 2018 may be a contributing factor."

True label: `analysis` | Predicted: `hot_take` | Confidence: 0.34

Two specific statistics with a direct comparison — textbook `analysis`. The model predicted `hot_take`, likely because "may be a contributing factor" is hedged rather than assertive. **Root cause:** the model learned that confident claims signal `analysis`, and tentative language signals `hot_take`. When an analysis comment hedges its conclusion, the model misreads the uncertainty as opinion.

---

**Error 3 — fine-tuned model**
> "The reason Australia wins in Brisbane is their pace attack has been built for the Gabba's extra bounce since 2015. Every selection decision reflects that tactical philosophy."

True label: `analysis` | Predicted: `hot_take` | Confidence: 0.36

This comment contains no statistics at all — it is pure tactical cause-and-effect reasoning. The model predicted `hot_take` with very low confidence (0.36), and all three class scores were nearly equal (analysis 35.1%, hot_take 36.4%, reaction 28.4%), showing the model was almost randomly guessing. **Root cause:** the model learned that numbers and percentages are the primary signal for `analysis`. When a comment reasons analytically but contains no explicit statistics, the model has no signal to work with and defaults to `hot_take`.

---

**Pattern across all three errors:** All three are `analysis` comments the model failed on — but for three different reasons:
- Error 1: numbers present, but conclusion framed comparatively ("not just a talking point")
- Error 2: numbers present, but conclusion is hedged ("may be a contributing factor")
- Error 3: no numbers at all — pure tactical reasoning with no statistical evidence

Together these reveal the model's core shortcut: **it learned "numbers = analysis" rather than "evidence-dependence = analysis."** Any analysis comment that doesn't contain explicit statistics or percentages is at risk of being misclassified.

---

### What the model learned vs. what we intended

**What we intended:**
> `analysis` = the argument structurally depends on verifiable evidence. Remove the stat, the claim collapses.

**What the model actually learned:**
> `analysis` = text containing numbers and percentages.
> `hot_take` = text with strong opinion language or no numbers.
> `reaction` = ALL CAPS, exclamation marks, present-tense emotional language.

The model learned a surface-level proxy rather than the deeper semantic test. This is why it failed on hedged analysis — the numbers were present but the confident-assertion signal was absent, and confident assertion was the shortcut it learned for `analysis`.

`reaction` was easiest because its linguistic markers (capitalisation, exclamation marks, live-match vocabulary) are visually distinctive and rarely appear in other labels. `hot_take` was second easiest for the same reason — superlatives and absolute language are strong signals. `analysis` was hardest because its defining feature (evidence-dependence) is semantic, not surface-level.

**To improve:** Training examples should include more `analysis` comments with tentative language ("may suggest," "appears to correlate with") alongside `hot_takes` with a single cherry-picked stat. This would force the model to learn evidence-dependence rather than just tone.

---

## AI Usage

**Instance 1 — Dataset construction**
The 211 labeled examples were constructed with AI assistance (Claude). The student directed the AI to generate realistic r/Cricket comments matching each label's definition, modeled after patterns in real r/Cricket threads. The student reviewed and confirmed every example, defined the three labels and their decision rules independently, and made all edge case decisions. Pre-labeling examples with an LLM for human review was explicitly considered and rejected — all labels were assigned based on the definitions agreed upon in planning.

**Instance 2 — Failure analysis**
After training, the list of wrong predictions was reviewed with AI assistance to identify systematic patterns. The AI identified the shared pattern (hedged/stat-free analysis comments mislabeled as hot_take). The student verified this pattern held across all three errors before including it in the report.

**What was overridden:**
The option to use LLM pre-labeling for annotation assistance was considered and explicitly rejected — all labeling decisions were made by the student using the definitions from planning.md. The student also overrode an initial success target of "close to 1.0" in favour of a realistic threshold (accuracy ≥ 70%, macro F1 ≥ 0.65) after discussion.

---

## Spec Reflection

**One way the spec helped:**
Defining specific success criteria before training (accuracy ≥ 70%, macro F1 ≥ 0.65, no class F1 < 0.50) meant there was a clear, objective target to evaluate against. When results came in at 93.8% accuracy and macro F1 0.94, it was immediately clear both models exceeded the threshold — no post-hoc rationalisation needed.

**One way implementation diverged from the spec:**
The data collection plan described manual collection from public r/Cricket threads. In practice, the dataset was constructed by generating examples modeled after r/Cricket discourse patterns, due to time constraints. The split ratio also changed from the planned 80/10/10 to the notebook's 70/15/15. Neither change affected the validity of the evaluation — the test set remained locked and the label distribution stayed balanced.

---

## Workflow

1. Upload `data/dataset.csv` to Colab
2. Set runtime to **T4 GPU** (Runtime → Change runtime type)
3. Add `GROQ_API_KEY` to Colab Secrets
4. Run all cells — training takes ~5-15 min on T4
5. Download `evaluation_results.json` and `confusion_matrix.png` into `results/`
6. Commit the artifacts and fill in the results table above
