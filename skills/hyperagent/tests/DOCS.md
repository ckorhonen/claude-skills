# Hyperagent Test Fixtures

These fixtures demonstrate a complete hyperagent loop optimizing a Python text summarizer.

## Files

- `target.py` — baseline summarizer (takes first sentence). Score: ~0.3333
- `target_v1.py` — picks sentence with most unique words. Score: ~0.3333 (no improvement)
- `target_v2.py` — keyword extraction via stopword removal. Score: ~0.9444 (+183%)
- `target_v3.py` — TF-IDF sentence ranking + top-2. Score: ~0.5278 (worse than v2)
- `task.sh` — benchmark runner (calls target.py, emits `METRIC score=<float>`)
- `checks.sh` — correctness gate (verifies METRIC line is present)

## Run the test suite

From a git-tracked directory, run:

```bash
SCRIPTS=path/to/hyperagent/scripts

python3 $SCRIPTS/init_session.py \
  --goal "Improve text summarizer word overlap score" \
  --metric-name score \
  --unit "overlap" \
  --direction higher \
  --task-command "bash path/to/tests/task.sh" \
  --checks-command "bash path/to/tests/checks.sh" \
  --min-improvement 5.0 \
  --warmups 1 --trials 3 \
  --scope target.py

# Baseline
python3 $SCRIPTS/run_task.py \
  --id gen-000 --hypothesis "Baseline: first-sentence" \
  --change-summary "No changes" --generation 0 --baseline | \
  python3 $SCRIPTS/log_variant.py

# Gen 1: no improvement
python3 $SCRIPTS/run_task.py \
  --id gen-001 --hypothesis "Pick sentence with most unique words" \
  --change-summary "max(sentences, key=unique_word_count)" \
  --parent gen-000 --generation 1 \
  --command "python3 path/to/tests/target_v1.py" | \
  python3 $SCRIPTS/log_variant.py

# Gen 2: +183% improvement
python3 $SCRIPTS/run_task.py \
  --id gen-002 --hypothesis "Keyword extraction via stopword removal" \
  --change-summary "Extract non-stopword tokens from full text" \
  --parent gen-000 --generation 1 \
  --command "python3 path/to/tests/target_v2.py" | \
  python3 $SCRIPTS/log_variant.py

# Gen 3: regression (discarded)
python3 $SCRIPTS/run_task.py \
  --id gen-003 --hypothesis "TF-IDF ranking, top-2 sentences" \
  --change-summary "Rank sentences by keyword density, combine top 2" \
  --parent gen-002 --generation 2 \
  --command "python3 path/to/tests/target_v3.py" | \
  python3 $SCRIPTS/log_variant.py

# Report
python3 $SCRIPTS/render_report.py
```

## Expected Results

```
gen-000: score=0.3333 → keep (baseline)
gen-001: score=0.3333 → discard (0% improvement)
gen-002: score=0.9444 → keep (+183.3%)
gen-003: score=0.5278 → discard (-44.1% vs best)
```
