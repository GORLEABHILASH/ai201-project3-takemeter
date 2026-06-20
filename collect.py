"""Collect r/Cricket comments into data/dataset.csv for TakeMeter labeling.

Pulls every comment (including nested replies) from each thread in THREADS,
filters out the unusable ones, de-duplicates, and writes a `text,label` CSV
with the `label` column left blank for you to fill in by hand.

Setup
-----
1. Create a free Reddit "script" app:  https://www.reddit.com/prefs/apps
   -> "create another app" -> type: script -> note the client id + secret.
2. Copy .env.example to .env and fill in the four values.
3. pip install -r requirements.txt
4. python collect.py
"""

import csv
import os
import re

import praw
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Threads to pull from. Anchor on the Root milestone post, then add a match
# thread and a discussion thread so the dataset isn't all praise/reaction.
# Paste full URLs or just the permalink path — both work.
# ---------------------------------------------------------------------------
THREADS = [
    "https://www.reddit.com/r/Cricket/comments/1uaxafc/joe_root_gets_to_14000_runs_in_test_cricket/",
    # "https://www.reddit.com/r/Cricket/comments/XXXXXXX/...",  # a match / post-match thread
    # "https://www.reddit.com/r/Cricket/comments/XXXXXXX/...",  # a discussion / debate thread
]

OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
MIN_WORDS = 5  # drop comments too short to classify

# Authors that produce non-discourse text we never want as examples.
SKIP_AUTHORS = {"AutoModerator"}
# Bodies that mean the comment is gone.
SKIP_BODIES = {"[deleted]", "[removed]", ""}


def clean(text: str) -> str:
    """Collapse whitespace so each comment is a single tidy CSV cell."""
    return re.sub(r"\s+", " ", text).strip()


def usable(comment) -> bool:
    body = (comment.body or "").strip()
    if body in SKIP_BODIES:
        return False
    author = str(comment.author) if comment.author else ""
    if author in SKIP_AUTHORS:
        return False
    if len(body.split()) < MIN_WORDS:
        return False
    return True


def main() -> None:
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ.get("REDDIT_USER_AGENT", "takemeter-research/0.1"),
    )
    reddit.read_only = True

    seen = set()
    rows = []
    for url in THREADS:
        submission = reddit.submission(url=url)
        submission.comments.replace_more(limit=None)  # expand "load more comments"
        kept = 0
        for comment in submission.comments.list():
            if not usable(comment):
                continue
            text = clean(comment.body)
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append(text)
            kept += 1
        print(f"  {kept:4d} comments kept  <-  {submission.title!r}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for text in rows:
            writer.writerow([text, ""])

    print(f"\nWrote {len(rows)} comments to {OUT_PATH}")
    if len(rows) < 200:
        print("WARNING: fewer than 200 rows — add more threads to THREADS.")


if __name__ == "__main__":
    main()
