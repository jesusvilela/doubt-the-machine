# ACAF — fuzzing the Rule 0 contract

Rule 0 says this framework must get harder to fool as people try to break it. That is an
empirical claim about `scripts/check_rule0.py`, and until ACAF nothing measured it.

`scripts/acaf_ambigator.py` measures the broad mutation span. `scripts/acaf_meaning_matrix.py`
attacks one narrower semantic-direction gap deterministically across all 27 active rules.

## The triad, mapped onto this repository

| ACAF component | Here |
|---|---|
| **Actor** | `scripts/check_rule0.py` — the self-audit contract that CI runs |
| **Critic** | labelled oracles fixed before execution: base mutations are `MUST_CATCH` or `MUST_PASS`; each rule meaning declares one inversion and one paraphrase |
| **Ambigator** | mutation generators spanning README rules, poster labels, retired wording, preregistration constants, API contract, results schema, required artifacts, plus the operational-meaning matrix |
| **Fuzzer** | the sweep runner and meaning matrix: apply mutations to throwaway copies and record whether the Actor failed |

The Critic's labels are fixed before the Actor runs, so a result cannot be rationalised after
seeing the checker outcome. The working tree is never mutated.

## What is measured

The base sweep keeps the same Pareto pair as Experiment 001:

```text
escape_rate       = MUST_CATCH mutations the checker passed   (undetected important defects)
false_alarm_rate  = MUST_PASS  mutations the checker rejected (rejected correct work)
```

The operational-meaning matrix keeps an analogous pair without collapsing it into the base score:

```text
inversion_escape_rate         = inverted meaning cells the checker passed
paraphrase_false_alarm_rate   = declared meaning-preserving paraphrases the checker rejected
```

None of these coordinates is collapsed into a scalar utility. A checker that rejects all prose
could score zero inversion escapes and still be useless because its paraphrase false-alarm rate
would be one.

## Base mutation families

`MUST_CATCH` — semantics-breaking, CI must reject:
`rule_deletion`, `panel_deletion`, `rule_retitle` (semantic inversion), `poster_gutting`,
`poster_rule_drop`, `poster_relabel`, `retired_reintroduction` (any surface),
`prereg_numeric_drift`, `effect_region_softening`, `seed_audit_weakening`,
`contract_drift`, `results_corruption`, `rule_zero_removal`, `falsifier_softening`,
`graveyard_erasure`, `artifact_deletion`, `codex_approval_widening`.

`MUST_PASS` — benign, CI must not block:
`benign_prose`, `benign_meaning_edit`, `benign_graveyard_entry`, `benign_valid_result_row`,
`benign_evidence_source`, `benign_whitespace`, `benign_new_test`.

The base Ambigator remains a 24-family span. `check_acaf_generators.py` independently verifies that
every declared base mutation applies, changes the throwaway tree, and contributes to the expected
denominator before the sweep is interpreted.

## Operational-meaning matrix

`rules.json` v3 no longer pins rule identity only. Each active rule also carries a deliberately
**low-resolution directional contract**:

- required concept groups — at least one wording variant from each group must remain present;
- forbidden inversion phrases — explicit opposite-direction formulations that must be rejected;
- one declared `paraphrase_example` that must pass; and
- one declared `inversion_example` that must fail.

Operational prose is still not byte-pinned. The checker normalizes wording and permits the declared
paraphrases. The matrix then changes only the third README column while keeping panel, number, and
rule title fixed. It executes exactly:

```text
27 inversion cases   MUST_CATCH
27 paraphrase cases  MUST_PASS
54 total cases
```

This closes the specific failure where a title survives while the explanation is replaced by one
of the declared opposite-direction meanings. It does **not** implement general natural-language
entailment, contradiction detection, or semantic equivalence.

## Running it

```bash
python scripts/check_acaf_generators.py --seeds 3
python scripts/acaf_ambigator.py --seeds 3 --max-escape-rate 0.0 --max-false-alarm-rate 0.0
python scripts/acaf_meaning_matrix.py --max-inversion-escape-rate 0.0 --max-paraphrase-false-alarm-rate 0.0
```

The required `self-audit-contract` runs all three on every PR. `.github/workflows/acaf.yml` runs the
25-seed base sweep plus the complete 54-case meaning matrix nightly. Tagged releases rerun the same
boundaries before publishing.

## Measured result from the original handoff audit

| Checker state | Mutations | Escape rate | False-alarm rate |
|---|---:|---:|---:|
| Before hardening (string-presence checks) | 72 | **0.373** (19/51) | 0.000 (0/21) |
| After hardening, same sweep | 72 | **0.000** (0/51) | 0.000 (0/21) |
| After hardening, 12 seeds/family | 288 | **0.000** (0/204) | 0.000 (0/84) |

These measurements were produced by the co-developer's clean local harness before this work was
pushed to GitHub. They describe the historical 24-family base span only; the operational-meaning
matrix did not yet exist. The landed harness is rerun by CI, so do not substitute this table for a
current workflow result.

Escapes in that baseline were concentrated exactly where the checker tested for tokens rather than
structure: `rule_deletion` 3/3, `rule_retitle` 3/3, `panel_deletion` 3/3,
`poster_relabel` 3/3, `poster_gutting` 2/3, `poster_rule_drop` 2/3,
`retired_reintroduction` 2/3, `graveyard_erasure` 1/3. Every numeric family — the
preregistration constants, API contract, results schema, required artifacts — escaped 0/3 both
before and after. The weakness was not in the arithmetic.

## What the current checks do not establish

Read this before quoting any zero.

1. **Correlated checking** (PRINCIPLES §11). The mutation space, meaning contracts, examples, and
   hardened checker were authored in the same development loop. A same-author zero preferentially
   covers the mutations the author thought to declare; it is not independent replication.
2. **The span is declared, not exhaustive.** The base sweep is 24 mutation families. The meaning
   matrix adds 27 declared inversions and 27 declared paraphrases. An adversarial rewording outside
   those concept groups or forbidden phrases can still escape. The checker is deliberately not a
   natural-language inference model.
3. **Concept anchors are lossy.** They protect coarse semantic direction while allowing prose to
   move. That is the design trade-off: exact sentence hashes would catch every edit but turn benign
   clarification into a false alarm. The matrix measures this declared compromise; it does not prove
   the compromise is optimal.
4. **A passing sweep is not evidence the framework works.** It establishes only that the repository
   checker rejects the declared contract violations while permitting the declared controls.
   Experiment 001's effectiveness claim remains `H` and requires separately powered evidence.

The useful contribution is a progressively harder-to-game local contract with explicit negative and
benign controls. It is still not an independent reproduction witness when authored in the same loop.

## Extending it

For structural or numeric coverage, add a generator method to `Ambigator`, label it, and register it
in `generators()`. For operational meaning, strengthen a rule's concept groups or add an adversarial
phrase only when a concrete escape demonstrates the need. A new escaping case is a finding: preserve
it before hardening the checker.

Do not rescue an escaped semantic mutation by exact-string pinning unless the false-alarm trade-off
is measured first.

## Rollback

Revert workflow wiring before removing a checker or matrix script that CI consumes. Preserve the
historical measurements and correction record; this tock changes verification, not active rule
wording.
