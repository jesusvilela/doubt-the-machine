# Contributing

Contributions are welcome — especially **falsifications, counterexamples, tighter wording, and simpler tests**.

The project should improve by surviving criticism, not by collecting agreement.

## Keep changes small

Prefer one claim, one failure mode, and one inspectable change at a time. A good contribution should be easy to understand, test, and revert.

For a rule change, include:

1. **Claim** — the exact rule or statement you are challenging.
2. **Failure mode** — how it can mislead, overclaim, or break.
3. **Evidence** — a primary source, reproducible test, benchmark, derivation, or concrete counterexample.
4. **Observation** — what actually happened.
5. **Smallest useful edit** — avoid rewriting unrelated material.
6. **Falsifier** — what evidence would make *your* proposal wrong.
7. **Reversal** — how the change can be undone if it makes the framework worse.

A useful issue or PR body is:

```text
Claim:
Why I doubt it:
Failure mode:
Evidence/test:
Observed result:
Proposed change:
What would falsify my proposal:
Rollback/reversal:
```

## What makes a strong contribution

Strong contributions usually do at least one of these:

- replace an absolute statement with a more defensible operational one;
- provide a reproducible counterexample;
- distinguish correlated self-checks from independent evidence;
- define a missing baseline, metric, or condition;
- expose an omitted failure mode;
- make a rule easier to apply in practice;
- remove unnecessary complexity.

## Poster vs canonical wording

The poster is intentionally compressed. Concision can cost precision.

If poster wording and the README differ, treat the **README as canonical** unless a later commit explicitly changes that contract. `PRINCIPLES.md` contains the deeper rationale.

## Rule 0

These contribution rules are also provisional. If this process discourages useful criticism or creates needless ceremony, challenge it with the same protocol.
