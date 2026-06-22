# TakeMeter — planning.md

> Complete this document before writing any notebook code.
> Your spec is what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your
> classifier and evaluation code — the more specific it is, the more useful the generated code.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## 1. Problem statement

**Community: r/Cricket — and why it's a good fit**
r/Cricket is a large, active subreddit with genuinely varied discourse. Three meaningfully
different types of comments coexist in every major thread: stat-backed tactical arguments,
bold unsupported opinions, and live emotional reactions. These three types are easy to
distinguish at the extremes but genuinely hard to separate at the boundary — which makes
the task interesting for a classifier. The community is also text-heavy (not image-driven),
public, and consistent enough in vocabulary that patterns are learnable. A classifier that
works here could surface high-quality analytical content from the noise of reactions and
hot takes at scale.

**What is being classified?**
Each example is a comment from r/Cricket. The model predicts whether the comment is an
`analysis` (structured argument backed by specific statistics or historical evidence),
a `hot_take` (bold confident opinion stated without supporting evidence), or a
`reaction` (immediate emotional response to a specific live moment or result).

**Why does this classification matter / who is it for?**
Moderators and community researchers can use this classifier to automatically surface
substantive analytical content from the noise of live-match reactions and unsupported
opinions — useful for aggregating discourse quality signals at scale across r/Cricket threads.

---

## 2. Labels

| Label | Meaning | Example input |
|---|---|---|
| `analysis` | A structured argument backed by statistics, historical data, or tactical observation. Evidence is specific and verifiable. Multiple data points, or a single stat placed in analytical context. | "Root's conversion rate (50s to 100s) is 43%, placing him top-10 among batters with 100+ innings. The criticism that he doesn't convert is driven by memory of specific failures, not the overall pattern." |
| `hot_take` | A bold, confident opinion stated without supporting evidence. The post asserts rather than argues — may be correct, but does not reason from evidence. Strong declarative framing, often with superlatives or absolute language. | "Rohit Sharma is the most overrated Test opener in history. He collapses abroad every single time. People treat him like a legend but his away record doesn't back it up." |
| `reaction` | An immediate emotional response to a specific live moment, score update, or result. Little to no argument — the comment is expressing a feeling, often time-sensitive and in the moment. | "YESSS!! What an absolute catch!! He came from nowhere!! I cannot believe it!!" |

**Is this balanced or imbalanced?**
By design: 70 examples per label, balanced at ~33% each. Total: 210 examples.

---

## 3. Dataset

**Source:** r/Cricket — dataset constructed from patterns observed across three thread types:
(1) milestone / GOAT-debate threads (Root's 14,000 runs, Kohli records, etc.),
(2) ongoing series discussion threads (India vs England 2024, Ashes 2023),
(3) post-match and live match reaction threads.

Examples were built by reading real r/Cricket thread patterns and writing comments that
reflect the actual vocabulary, argument structures, and emotional registers used in the community.

**Size:** 211 labeled examples total.
**Split:** 70% train (~148), 15% validation (~32), 15% test (~32) — handled automatically by the notebook, stratified by label.

**Schema of `data/dataset.csv`:**

| Column | Type | Description |
|---|---|---|
| `text` | str | The comment to classify |
| `label` | str | Ground-truth label: `analysis`, `hot_take`, or `reaction` |
| `source_url` | str | Representative thread type the example was drawn from |

**How was it labeled?**
Labels were assigned by the author based on the definitions above. The three-way
distinction is operationally clear: `analysis` requires specific verifiable evidence;
`hot_take` makes a strong claim without evidence; `reaction` is purely emotional/situational.

**Label distribution:**
- `analysis`: 70 examples
- `hot_take`: 71 examples
- `reaction`: 70 examples

---

## 4. Hard labeling decisions (3 genuine edge cases)

**Edge case 1:**
> "Kohli's century drought from 2020 to 2022 proves he needed that break. He came back
> refreshed and immediately started scoring. Mental health in cricket is real."

Could be `hot_take` (strong claim about why something happened) or `analysis` (causal reasoning about form).
**Decision: `hot_take`** — the causal claim is asserted with zero data. There's no statistical
support for the drought-break-refresh chain; it's a confident interpretation dressed as insight.

**Edge case 2:**
> "Root's record against left-arm spin (28.4) vs right-arm spin (44.6) reveals a consistent
> technical weakness — he plays across the line against deliveries that angle away from him."

Could be `hot_take` (strong opinion about technique) or `analysis` (cites stats).
**Decision: `analysis`** — specific, verifiable numbers are the primary substance. The technique
inference follows directly from the stat rather than being asserted independently.

**Decision rule for analysis vs. hot_take when a stat is present:**
If the stat is the central argument (you'd lose the claim without it), label `analysis`.
If the stat is decorative — one cherry-picked number appended to what is fundamentally
an opinion — label `hot_take`. The test: would you remove the stat and the opinion still
stand as the main point?

**Edge case 3:**
> "He's so good. Honestly. When he's in form like this, I'd pay anything just to watch him bat."

Could be `hot_take` (strong opinion) or `reaction` (emotional live response).
**Decision: `reaction`** — the phrasing "right now" and "like this" signals an in-the-moment
observation responding to what's happening in a game, not a deliberate judgment about the
player's overall quality. When the comment is anchored to the present moment, prefer `reaction`.

---

## 5. Model / approach

**What does the classifier use?**
Fine-tuned `distilbert-base-uncased` on the labeled dataset. Baseline comparison:
zero-shot classification using `llama-3.3-70b-versatile` via Groq API.

**Inputs → outputs:**
Raw comment text → one of {`analysis`, `hot_take`, `reaction`} plus confidence scores.

**Where it runs:** Google Colab notebook (T4 GPU runtime).

**Key hyperparameter decisions:**
- **Learning rate: 2e-5** — standard for DistilBERT fine-tuning. 3e-5 risks overshooting
  on only 168 training examples; 1e-5 would train too slowly to converge in 5 epochs.
- **Epochs: 5** — at 168 training examples, 3 epochs risks underfitting; 10 risks
  memorizing the training set. 5 is the empirical sweet spot for small-dataset BERT fine-tuning.
- **Batch size: 16** — balances GPU memory on Colab T4 with stable gradient estimates at
  this dataset size. 32 would produce only ~5 updates per epoch, which is too few.

---

## 6. Evaluation plan

**Metrics:**
- Overall accuracy (primary, for direct comparison with zero-shot baseline)
- Per-class F1, precision, recall (to diagnose which label is hardest)
- Macro-averaged F1 as the headline metric (classes are balanced, so macro = micro here)
- Confusion matrix on test set — primary diagnostic for label pair confusions

**Artifacts produced by the notebook:**
- `results/evaluation_results.json` — accuracy, macro F1, and per-class precision/recall/F1
  for both fine-tuned model and zero-shot Groq baseline
- `results/confusion_matrix.png` — confusion matrix on the test set (fine-tuned model)

**What counts as success?**
- Fine-tuned model accuracy ≥ 70% on the test set (random chance = 33%)
- Fine-tuned model macro F1 ≥ 0.65
- No single class with F1 < 0.50
- Fine-tuned model macro F1 > zero-shot Groq baseline macro F1 (fine-tuning must add measurable value)

---

## 7. Failure modes & edge cases

**Most likely confusion pairs:**

1. **`analysis` vs `hot_take`**: Posts with a single cherry-picked stat used rhetorically
   rather than analytically. The model may over-classify any stat-mentioning comment as
   `analysis`, missing that the framing is still primarily opinion.

2. **`hot_take` vs `reaction`**: Strong emotional opinions about an in-match decision
   (e.g., "that captain is an idiot for that review") sit at the boundary. The model may
   struggle to distinguish declarative in-game opinions from live emotional reactions.

3. **Short `reaction` vs short `hot_take`**: Very short comments ("Terrible decision."
   vs "We're done.") may be hard to distinguish — the model needs enough text to find
   evidence of temporal anchoring (reaction) vs. general opinion framing (hot_take).

**The confusion matrix will reveal it if:** `analysis`↔`hot_take` cells are high
(stat-cherry-picking problem) or `hot_take`↔`reaction` cells are high (in-game opinion problem).

**Plan if a class performs poorly:**
- If `analysis` F1 < 0.50: add more varied evidence patterns to training (more formats,
  more historical comparisons, not just batting stats)
- If `reaction` F1 < 0.50: ensure enough live-match linguistic markers (ALL CAPS, !!,
  exclamations, present-tense emotional verbs) are represented in training

---

## 8. AI Tool Plan

**Label stress-testing: YES**
Before annotating, use Claude to generate 10 boundary-case comments that sit exactly between
`hot_take` and `analysis` (a stat present but used rhetorically) and between `hot_take` and
`reaction` (strong emotional opinion during a live match). If any generated comment cannot be
cleanly classified, tighten the decision rule before labeling more examples.

Prompt to use:
> "Generate 5 cricket comments that sit exactly on the boundary between analysis and hot_take —
> where a stat is present but used as decoration rather than as the core argument. Then generate
> 5 that sit between hot_take and reaction — strong opinion statements during a live match."

**Annotation assistance: NO**
All labels were assigned by the author manually without LLM pre-labeling. This ensures the
ground-truth labels reflect human judgment, not an AI's interpretation of the definitions.

**Failure analysis: YES**
After training, paste the full list of wrong predictions into Claude with this prompt:
> "Here are comments the model got wrong. Each shows the actual label and the predicted label.
> Identify any systematic pattern — is there a type of comment the model consistently
> misclassifies? Be specific about the linguistic or structural feature causing the error."

Verify the pattern yourself: check that at least 3 of the identified wrong predictions actually
fit the pattern before including it in the evaluation report.

---

## 9. Stretch goals (optional)

- [ ] **Error pattern analysis:** Identify systematic patterns in wrong predictions beyond
  listing individual errors (e.g., "model consistently misclassifies posts with one stat as analysis").
- [ ] **Confidence calibration:** Check if 90% confident predictions are actually right 90%
  of the time — or if the model is systematically overconfident on `hot_take`.
- [ ] **Deployed interface:** Streamlit app that accepts a comment, classifies it, and
  shows the label + confidence score.
- [ ] **Inter-annotator reliability:** Have a second person label 30+ examples and compute
  Cohen's kappa. Predicted disagreement zone: `hot_take` vs `reaction` boundary.
