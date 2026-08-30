# Graveyard

A framework that says “revert when it fails” should preserve the evidence that caused reversals.

This file records formulations that were removed, weakened, or replaced. A graveyard entry is not an embarrassment; it is evidence that Rule 0 has been exercised.

## 2026-08-30 — first explicit self-audit

### Retired: “Count how often it disagrees with you”

**Why it failed:** raw disagreement is not evidence. Optimizing for disagreement can create reverse sycophancy or performative contrarianism.

**Replacement:** **Test framing invariance** — ask materially equivalent questions under supportive, opposing, and neutral framing and check whether conclusions track evidence rather than the user stance.

**Status:** retired as a general-purpose diagnostic.

---

### Retired: “No test, no merge”

**Why it failed:** the repository itself says evidence is claim-relative. Runtime tests are appropriate for behavioral claims, but documentation, proofs, metadata, provenance changes, and some configuration changes require different evidence.

**Replacement:** **No unverified behavior, no merge** — match the evidence to the claim made by the change.

**Status:** retired as an absolute formulation.

---

### Retired: “Own every changed line”

**Why it failed:** it expresses responsibility but scales poorly as an operational rule for high-throughput agentic changes. Exhaustive line inspection can become ceremonial while important behavioral invariants remain underspecified.

**Replacement:** **Own every changed behavior** — specify invariants, inspect risk-bearing paths directly, test changed behavior and failure paths, preserve provenance, and sample lower-risk generated surfaces when exhaustive human inspection is not credible.

**Status:** narrowed and replaced; direct line review remains appropriate when risk or scale warrants it.

---

### Retired: `uncertainty × consequence × irreversibility`

**Why it failed:** written as a multiplication, the expression implied a quantitative model without defined units, calibration, or a justified multiplicative relationship.

**Replacement:** verification effort should **increase with uncertainty, consequence, and irreversibility**. Quantitative policies must define domain-specific axes and thresholds explicitly.

**Status:** pseudo-equation retired; qualitative ordering retained.

---

### Retired: three local “Rule 0” rows

The exact retired poster labels were:

- `0  Doubt this list too`
- `0  Doubt the compression`
- `0  Test this list too`

**Why it failed:** the README had one global Rule 0 plus a separate `0` row in each panel, making “Rule 0” ambiguous and visually padding a framework that emphasizes compression.

**Replacement:** one global Rule 0, with short unnumbered reflexive checks under each panel.

**Status:** retired as numbering, preserved as behavior.

## 2026-08-30 — external peer-review hardening

### Retired: poster drift as an acceptable compression difference

**Failure mode:** the v1.1 SVG still distributed three formulations that the canonical README and this graveyard had already retired. The CI contract inspected README and correction history but not the most shareable artifact.

**Evidence / counterexample:** direct inspection of `assets/doubt-the-machine.svg` found “Count disagreement”, “No test, no merge”, “Own every changed line”, and the retired local Rule-0 numbering after those formulations had been removed from the README.

**Replacement:** poster v1.2 uses the canonical replacements, preserves the re-sampling/non-independence caveat, and CI now evaluates poster surfaces through `retired.json`.

**Status:** corrected implementation drift.

---

### Retired: two-arm Experiment 001 as sufficient evidence for the specific gate

**Failure mode:** ordinary review versus the Doubt gate cannot distinguish the gate’s epistemic content from generic slowing-down, attention, or Hawthorne effects.

**Replacement:** add an equal-effort five-field active placebo (`TASK / SUMMARY / DETAILS / ALTERNATIVE / DECISION`) and require the Doubt gate to outperform both comparators.

**Status:** original causal interpretation retired; three-arm interpretation preregistered before data collection.

---

### Retired: undefined “utility analysis” as a kill condition

**Failure mode:** no preregistered exchange rate existed between escaped defects and review minutes, leaving the decision boundary open to post-hoc choice.

**Replacement:** keep important-defect escape, false alarms, and review time as separate coordinates. Pin a minimum 10-point escape-rate improvement and maximum 10-point false-alarm penalty; report review-time cost without inventing a scalar utility after seeing results.

**Status:** retired as an undefined decision rule.

---

### Retired: open-ended Experiment 001 sample size

**Failure mode:** no fixed N, reviewer count, or optional-stopping rule made a negative or positive result difficult to interpret.

**Replacement:** exactly 216 scorable task reviews per cohort, 72 per condition, 18 per task family per condition, at least 12 reviewer IDs, no outcome-driven extension. If uncertainty remains too wide, report inconclusive under a new preregistration rather than extending the same run.

**Status:** retired before result collection.

## Machine-readable retirement source

`retired.json` is the machine-readable ledger used by CI to prevent retired wording from reappearing on declared public surfaces. This human-readable graveyard preserves the reasons, evidence, and replacements.

## Entry template

```text
Date:
Rule / claim retired:
Failure mode:
Evidence / counterexample:
Replacement, if any:
Status: weakened | replaced | retired
Reversal of the replacement:
```
