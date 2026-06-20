# TakeMeter — planning.md

> Complete this document before writing any notebook code.
> Your spec is what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your
> classifier and evaluation code — the more specific it is, the more useful the generated code.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## 1. Problem statement

**What is being classified?**
_One or two sentences: what is each example, and what are you predicting about it?_

**Why does this classification matter / who is it for?**
_The real-world use case._

---

## 2. Labels

List every class the model can predict. You should have at least 2.

| Label | Meaning | Example input |
|---|---|---|
| `label_a` | _what this class means_ | _a representative example_ |
| `label_b` | _what this class means_ | _a representative example_ |

**Is this balanced or imbalanced?** _Roughly how many examples per label do you expect?_

---

## 3. Dataset

**Source:** Public **r/Cricket** comments, collected **manually** (copy-paste) from 3–5 threads.
No API/scraper, no authenticated content — per assignment rules. _(List the exact threads here.)_

**Size:** _How many labeled rows total (≥ 200)? Train/test split?_

**Schema of `data/dataset.csv`:**

| Column | Type | Description |
|---|---|---|
| `text` | str | The comment to classify |
| `label` | str | Ground-truth label (one of the labels above) |
| `source_url` | str | Permalink of the thread the comment came from (provenance) |

**How was it labeled?** _Who/what assigned the ground-truth labels, and how do you trust them?_

---

## 4. Model / approach

**What does the classifier use?** _LLM prompt-based classification, a trained model (e.g. logistic
regression / fine-tune), embeddings + nearest-neighbor, etc._

**Inputs → outputs:** _What goes in, what comes out (a single label? probabilities?)._

**Where it runs:** Google Colab notebook (link in the README).

---

## 5. Evaluation plan

**Metrics:** _Which metrics and why (accuracy, precision/recall/F1 per class, macro vs. weighted)?_

**Artifacts produced by the notebook:**
- `results/evaluation_results.json` — _what's in it (which metrics, what shape)?_
- `results/confusion_matrix.png` — confusion matrix over the test set.

**What counts as success?** _Target metric value(s) before you'd call the project done._

---

## 6. Failure modes & edge cases

_What inputs will confuse the classifier? Which label pairs are most likely to be confused, and how
will the confusion matrix reveal it? What's your plan if a class performs poorly?_

---

## 7. Stretch goals (optional)

_Anything beyond the baseline: more labels, larger dataset, model comparison, error analysis, etc._
