# TakeMeter — Learning Notes

Everything we discussed while building this project, in plain English.

---

## 1. What did we build?

A text classifier that reads r/Cricket comments and assigns one of three labels:

- **analysis** — comment makes a claim using specific stats or verifiable facts. The argument depends on the evidence.
- **hot_take** — strong opinion stated without supporting evidence. Asserts rather than argues.
- **reaction** — immediate emotional response to a live match moment. Time-anchored (now, today, just). ALL CAPS, exclamation marks.

**The key decision rule:**
> Remove the stat. Does the argument collapse? If yes → analysis. If the opinion still stands → hot_take.

---

## 2. The hardest label boundary

**hot_take vs reaction** is the trickiest pair.

Both can be emotional and strong. The separator is **time anchoring**:
- "Kohli is the most overrated batter ever" → no time anchor → hot_take
- "How did he drop that!! Right now!! Unbelievable!!" → happening live → reaction

Signal words for reaction: now, today, just, ALL CAPS, !!
Signal words for hot_take: greatest, never, always, overrated, should be dropped

---

## 3. What are the evaluation metrics?

### Accuracy
Out of every prediction, what percentage was correct?
> 30 correct out of 32 = 93.8% accuracy

Simple but hides problems. If all examples were hot_take and the model always guessed hot_take, accuracy looks good but the model is useless.

### Precision (per label)
Out of all the times the model said "this is analysis" — how many were actually analysis?
> Model called 10 comments analysis. Only 7 were right. Precision = 7/10 = 70%

"When the model makes a call, how often is it right?"

### Recall (per label)
Out of all the comments that actually ARE analysis — how many did the model find?
> 20 real analysis comments exist. Model found 14. Recall = 14/20 = 70%

"Out of all the real examples, how many did it catch?"

### F1 Score
One number combining precision and recall:
> F1 = 2 × (Precision × Recall) / (Precision + Recall)

High F1 = both precision and recall are good at the same time.

### Per-class F1
F1 calculated separately for each label. This is the most useful metric because it shows WHICH label the model struggles with.

### Macro F1
Average of all per-class F1 scores. Equal weight for each label.

### Confusion Matrix
A grid showing where the model gets confused:

|  | Predicted: analysis | Predicted: hot_take | Predicted: reaction |
|---|---|---|---|
| True: analysis | 9 ✓ | 2 ✗ | 0 |
| True: hot_take | 0 | 11 ✓ | 0 |
| True: reaction | 0 | 0 | 10 ✓ |

Read row by row. The diagonal = correct. Off-diagonal = mistakes.

**Our result:** 2 analysis comments were called hot_take. Everything else was perfect.

---

## 4. What is fine-tuning?

DistilBERT comes in two stages:

**Stage 1 — Pre-training (done by researchers)**
The model was trained on millions of Wikipedia articles and books. It learned what words mean, how sentences work, what numbers and percentages are. But it has no idea what analysis/hot_take/reaction means.

**Stage 2 — Fine-tuning (what we did)**
We added a new classification layer on top and trained it on our 147 labeled examples. The model used its existing language knowledge to learn the new task.

**Analogy:**
- Pre-training = teaching someone to read English fluently
- Fine-tuning = then showing them 147 cricket comments with labels and saying "learn the pattern"

---

## 5. How does training actually work?

### Weights
The model has millions of numbers inside it called weights. These determine how it classifies text. At the start of fine-tuning, the classification weights are random.

Training = adjusting those weights until the model gets the right answer most of the time.

### One training step (with batch size 16):

**Step 1 — Forward pass**
Model reads 16 comments and guesses a label for each one.

**Step 2 — Calculate loss**
For each comment, calculate how wrong the guess was. Average the 16 losses together.
- Confident and correct → low loss
- Wrong or uncertain → high loss

**Step 3 — Backward pass (backpropagation)**
Model works backwards through its own layers, figuring out which weights caused the error and by how much. This is called backpropagation.

**Step 4 — Update weights**
```
new_weight = old_weight - (learning_rate × gradient)
new_weight = old_weight - (0.00002 × gradient)
```

---

## 6. What is a gradient?

The gradient answers two questions for every single weight:
- **Which direction** should this weight move? (sign: + or -)
- **How much** did this weight contribute to the error? (size: big or small)

```
Weight A: gradient = +0.8  → caused a lot of error → move DOWN
Weight B: gradient = -0.3  → small contribution   → move UP a little
Weight C: gradient = +0.001 → barely mattered     → almost no change
```

**If analysis is always wrong:**
The weights responsible for the analysis decision get large gradients — they caused the most error. The model automatically focuses its adjustment on those weights.

**Analogy:**
10 people built a faulty bridge. Investigate backwards — the engineer who designed the foundations gets most of the blame (large gradient). The painter gets almost none (tiny gradient).

---

## 7. What is a learning rate?

The learning rate (2e-5 = 0.00002) controls how big each weight adjustment is.

**Too large (0.1):** Big jumps, overshoots the right answer, never settles down.
**Too small (0.000001):** Tiny steps, takes forever to learn anything.
**Just right (2e-5):** Small enough to be stable, large enough to learn in 3 epochs.

This value (2e-5) is the standard for DistilBERT — discovered by researchers through years of experimentation.

---

## 8. What is an epoch?

One epoch = the model goes through all 147 training examples once.

We used 3 epochs = the model sees all 147 examples 3 times.

**Why go through more than once?**
The first time you see something you don't fully learn it. Seeing it again reinforces the pattern.

**Our training loop:**
```
Epoch 1: 147 examples ÷ 16 per batch = ~9 batches → check validation
Epoch 2: same 147 examples again → check validation
Epoch 3: same 147 examples again → check validation
Done. Pick the best epoch.
```

---

## 9. What is overfitting?

**Analogy:**
Studying for an exam by memorising last year's exact questions. You get 100% on those questions but fail when the exam has slightly different ones.

Overfitting = model memorised the 147 training examples instead of learning the general pattern.

**How you detect it:**
```
Epoch 1:  Train 65%,  Val 63%  ← both improving, good
Epoch 2:  Train 82%,  Val 80%  ← both improving, good
Epoch 3:  Train 94%,  Val 93%  ← close together, good
Epoch 10: Train 99%,  Val 71%  ← GAP = overfitting
```

Training accuracy keeps rising. Validation accuracy stops or drops. That gap is the signal.

**How we prevented it:**
1. Only 3 epochs (not 20)
2. Validation set — model never trains on these, only checks itself
3. Weight decay (0.01) — penalises weights for getting too large
4. `load_best_model_at_end=True` — saves the epoch with the best validation score

---

## 10. Why did the giant model beat the fine-tuned one?

| | Groq llama-3.3-70b | Fine-tuned DistilBERT |
|---|---|---|
| Parameters | 70 billion | 66 million |
| Training data | Entire internet | Our 147 examples |
| Accuracy | 100% | 93.8% |
| Cost per request | Expensive | Almost free |
| Speed | Slower (network call) | Very fast (local) |
| Needs internet | Yes | No |

The giant model has already read millions of cricket discussions. With a good description it immediately understood the labels.

The small model learned from 147 examples — impressive for its size, but 1000x fewer parameters.

**Fine-tuning still wins when:**
- You need to classify 50,000 comments per day cheaply
- You need it to run offline or privately
- The task is very specific and not in general internet text

---

## 11. What did the model actually learn vs. what we intended?

**What we intended:**
> analysis = argument structurally depends on verifiable evidence

**What it actually learned:**
> analysis = text containing numbers and percentages
> hot_take = strong opinion language, no numbers
> reaction = ALL CAPS, exclamation marks, live-match words

It learned surface shortcuts, not the deep meaning.

**Why it made 2 mistakes:**
Both wrong predictions were analysis comments with hedged language:
- "may be a contributing factor"
- "not just a coaching talking point"

Numbers were present but the tone was tentative. The model learned "confident + numbers = analysis" — so tentative language with numbers confused it into predicting hot_take.

---

## 12. Our final results

| Metric | Fine-tuned DistilBERT | Groq baseline |
|---|---|---|
| Accuracy | 93.8% | 100% |
| Macro F1 | 0.94 | 1.00 |
| Wrong predictions | 2 / 32 | 0 / 32 |

**Success criteria we set before training:**
- Accuracy ≥ 70% ✓ (got 93.8%)
- Macro F1 ≥ 0.65 ✓ (got 0.94)
- No class F1 < 0.50 ✓ (lowest was 0.90)

Both models exceeded all criteria. The project is complete.
