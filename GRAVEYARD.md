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

**Why it failed:** the README had one global Rule 0 plus a separate `0` row in each panel, making “Rule 0” ambiguous and visually padding a framework that emphasizes compression.

**Replacement:** one global Rule 0, with short reflexive checks under each panel.

**Status:** retired as numbering, preserved as behavior.

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
