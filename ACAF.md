# ACAF — fuzzing the Rule 0 contract

Rule 0 says this framework must get harder to fool as people try to break it. That is an
empirical claim about `scripts/check_rule0.py`, and until now nothing measured it.

`scripts/acaf_ambigator.py` measures it.

## The triad, mapped onto this repository

| ACAF component | Here |
|---|---|
| **Actor** | `scripts/check_rule0.py` — the self-audit contract that CI runs |
| **Critic** | the labelled oracle: every mutation is declared `MUST_CATCH` or `MUST_PASS` **before** the Actor runs |
| **Ambigator** | mutation generators spanning the repository's surface space — README rules, poster labels, retired wording, preregistration constants, API contract, results schema, required artifacts |
| **Fuzzer** | the sweep runner: applies each mutation to a throwaway copy and records whether the Actor failed |

The Critic's labels are fixed in code before execution, so a result cannot be
rationalised afterwards. The working tree is never mutated.

## What is measured

Deliberately the same Pareto pair Experiment 001 uses, and for the same reason:

```text
escape_rate       = MUST_CATCH mutations the checker passed   (undetected important defects)
false_alarm_rate  = MUST_PASS  mutations the checker rejected (rejected correct work)
```

The two are **not** collapsed into a single score. A checker with `escape_rate 0` and
`false_alarm_rate 1` rejects everything and is useless; the reverse is the string-presence
checker this harness was written to falsify. `summarize()` has a test asserting no scalar
score is emitted.

## Mutation families

`MUST_CATCH` — semantics-breaking, CI must reject:
`rule_deletion`, `panel_deletion`, `rule_retitle` (semantic inversion), `poster_gutting`,
`poster_rule_drop`, `poster_relabel`, `retired_reintroduction` (any surface),
`prereg_numeric_drift`, `effect_region_softening`, `seed_audit_weakening`,
`contract_drift`, `results_corruption`, `rule_zero_removal`, `falsifier_softening`,
`graveyard_erasure`, `artifact_deletion`, `codex_approval_widening`.

`MUST_PASS` — benign, CI must not block:
`benign_prose`, `benign_meaning_edit`, `benign_graveyard_entry`, `benign_valid_result_row`,
`benign_evidence_source`, `benign_whitespace`, `benign_new_test`.

## Running it

```bash
python scripts/acaf_ambigator.py --seeds 3
python scripts/acaf_ambigator.py --seeds 25 --json acaf.json
python scripts/acaf_ambigator.py --seeds 3 --max-escape-rate 0.0 --max-false-alarm-rate 0.0
```

The required `self-audit-contract` runs 3 seeds/family on every PR, so an ACAF failure is
merge-blocking under the repository ruleset. `.github/workflows/acaf.yml` runs 25 seeds/family
nightly and writes the measured rates to the run summary.

## Measured result from the handoff audit

| Checker state | Mutations | Escape rate | False-alarm rate |
|---|---:|---:|---:|
| Before hardening (string-presence checks) | 72 | **0.373** (19/51) | 0.000 (0/21) |
| After hardening, same sweep | 72 | **0.000** (0/51) | 0.000 (0/21) |
| After hardening, 12 seeds/family | 288 | **0.000** (0/204) | 0.000 (0/84) |

These measurements were produced by the co-developer's clean local harness before this work was
pushed to GitHub. The landed harness is rerun by CI; do not substitute the table above for the
current workflow result.

Escapes in the baseline were concentrated exactly where the checker tested for tokens
rather than structure: `rule_deletion` 3/3, `rule_retitle` 3/3, `panel_deletion` 3/3,
`poster_relabel` 3/3, `poster_gutting` 2/3, `poster_rule_drop` 2/3,
`retired_reintroduction` 2/3, `graveyard_erasure` 1/3. Every numeric family — the
preregistration constants, the API contract, the results schema, required artifacts —
escaped 0/3 both before and after. The weakness was not in the arithmetic.

## What this result does not establish

Read this before quoting the 0.000.

1. **Correlated checking** (PRINCIPLES §11). The mutation space and the hardened checker
   were authored in the same development loop. A fuzzer written by the same process that wrote the
   fix will preferentially generate mutations that fix catches. `escape_rate = 0` over
   *this* mutation space is a much weaker claim than "the checker cannot be fooled".
2. **The span is declared, not exhaustive.** Anything outside the seventeen `MUST_CATCH`
   families is unmeasured. Notably: the *operational meaning* column of each rule is not
   pinned by `rules.json`, so a rule's title can survive while its explanation is
   inverted. That is a known, deliberate gap — pinning prose would raise the false-alarm
   rate — and it is the first place to attack this harness.
3. **A passing sweep is not evidence the framework works.** It is evidence that the
   repository's own contract checker rejects the contract violations it declares. That is
   `P`-level for the inspectable checker contract and says nothing about Experiment 001's
   `H`-level effectiveness claim.

The useful contribution is an adversarial generator whose mutations do not inspect the checker's
implementation. It is still not an independent replication witness when authored in the same loop.

## Extending it

Add a generator method to `Ambigator`, label it, and register it in `generators()`. A new
`MUST_CATCH` family that immediately escapes is a finding, not a bug in the harness —
report it, then decide whether to harden the checker or narrow its claim.

## Rollback

Reverting is ordered, because the release pipeline consumes the harness:

```bash
git revert <ci/cd commit>     # first: removes ACAF from required/release workflows
git revert <tock-004 commit>  # then: removes rules.json, the harness, and hardening
```

Reverting the tock alone while workflows still call the harness leaves CI pointing at a deleted
script. No active rule wording is restored or lost by this tock; it changes verification only.
