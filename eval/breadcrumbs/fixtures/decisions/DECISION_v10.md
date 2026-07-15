# DECISION.md — string_pipeline.py Architecture Decisions

This file records the architectural decisions made during autoresearch optimization.
It is a supplement to `.autoresearch/results.jsonl` — see that file for full experiment records.

---

## ADR-001: Module-level regex compilation

**Date:** 2026-03-10 | **Experiment:** exp-001 | **Status:** ACTIVE

**Decision:** Compile `_TOKEN_PATTERN` at module level, not inside `tokenize()`.

**Context:** Python's `re.split()` accepts either a pre-compiled pattern or a raw string.
When a raw string is passed, CPython checks a small internal cache but still incurs
lookup overhead on every call. For a hot-path function called 100 times per benchmark
iteration, this adds up.

**Consequence:** 18% latency reduction. The pattern is module-global; do not move it
inside any function scope. If the pattern needs to change per-call (e.g., configurable
delimiters), cache compiled patterns in a dict keyed by pattern string instead.

---

## ADR-002: Walrus operator in process_batch

**Date:** 2026-03-10 | **Experiment:** exp-002 | **Status:** ACTIVE

**Decision:** Use `[n for t in tokens if (n := t.strip().lower())]` instead of
a traditional loop calling `normalize(token)`.

**Context:** The original loop called `normalize()` once per token. Even simple function
calls carry overhead in CPython (frame creation, argument passing). The walrus operator
avoids the separate function call while keeping the filter+assign in one expression.

**Consequence:** 4% improvement. This sacrifices some readability for a consistent gain.
Do NOT refactor to `[normalize(t) for t in tokens if normalize(t)]` — that calls
`normalize()` TWICE per token (once for filter, once for the value), which is slower
than the original loop.

---

## ADR-003: Rejected — collections.Counter

**Date:** 2026-03-10 | **Experiment:** exp-004 | **Status:** REJECTED — do not retry

**Decision:** Do NOT replace `build_index` with `collections.Counter`.

**Context:** Counter is implemented in C and generally fast. However, for our workload:
- Token uniqueness rate is ~60% (3k unique out of 5k total)
- High unique-token rate means Counter's internal hash table resizes frequently
- The Python→C→Python transition overhead is not amortized over enough repeated keys

**Consequence:** Counter was 11% SLOWER than our dict loop for this workload.
This result is fundamental to our data distribution, not a transient artifact.
Revisit only if workload changes to have >80% repeated tokens.

---

## ADR-004: Local method alias pattern

**Date:** 2026-03-10 | **Experiment:** exp-005 | **Status:** ACTIVE

**Decision:** Assign `index_get = index.get` (and `merged_get = merged.get`) before
inner loops to avoid repeated attribute lookup.

**Context:** In CPython, attribute access (`obj.attr`) involves a `__getattribute__`
dispatch on every access. In a tight loop over 5k tokens, this adds up.
Assigning the bound method to a local variable makes the VM use a `LOAD_FAST`
opcode (local variable lookup) instead of `LOAD_ATTR` (attribute dispatch).

**Consequence:** 4% gain on 5k-token inputs. Small but consistent. Apply this pattern
wherever a method is called in a loop more than ~1000 times.

---

## ADR-005: Chunk size = 512

**Date:** 2026-03-10 | **Experiment:** exp-008 | **Status:** ACTIVE — hardware dependent

**Decision:** Process tokens in chunks of 512, not the full token list at once.

**Context:** `build_index` iterates over the token list and builds a dict. For 5k tokens,
the list + partial dict may exceed L1 cache (typically 32–64 KB on modern CPUs).
Cache misses in the inner loop are expensive. Breaking into 512-token chunks keeps
each working set (512 token references + partial merge dict) within L1 cache.

**Tested sizes:** 128 (6% gain), 256 (7% gain), 512 (9% gain), 1024 (5% gain — cache thrash).
512 was stable across 3 measurement runs. 256 was within noise boundary.

**Warning:** This optimization is hardware-sensitive. On machines with smaller L1 cache,
256 may outperform 512. On machines with larger caches, 1024 may be optimal.
Re-profile if deploying on different hardware. Do NOT change CHUNK_SIZE without re-profiling.

---

## ADR-006: Rejected — multiprocessing

**Date:** 2026-03-10 | **Experiment:** exp-006 | **Status:** REJECTED — only viable at 50k+ tokens

**Decision:** Do NOT use multiprocessing.Pool for parallelization.

**Context:** Process spawn overhead on this machine is ~50 ms. Our baseline is 9 ms.
The parallelization overhead completely dominates the work.

**Consequence:** Result was 58 ms (6x SLOWER). Only revisit if input size grows to
>50k tokens per call, where the speedup from parallel counting would amortize spawn cost.

---

## ADR-007: Rejected — numpy vectorization

**Date:** 2026-03-10 | **Experiment:** exp-007 | **Status:** REJECTED

**Decision:** Do NOT use numpy for token frequency counting.

**Context:** numpy's `unique()` with `return_counts=True` is vectorized but requires
converting Python string list → numpy object array → back to Python dict.
The round-trip cost (Python→numpy→Python) exceeds the vectorization benefit
for token lists under 10k elements.

**Consequence:** numpy approach was 20% SLOWER. Only viable for very large token lists
(>100k) where vectorization savings exceed conversion overhead.
