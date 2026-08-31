# Experiment 001 — seeded-error review gate

**Status:** preregistered **design pilot**; no result has been collected yet.

The original preregistration is preserved byte-for-byte in `preregistration.json`. A prospective pre-data amendment, `amendment-2026-08-31-pilot.json`, governs the effective execution contract. The amendment was added while `results.csv` still contained only its header.

Experiment 001 remains the first randomized three-condition self-test of the repository, but it is **not a confirmatory effectiveness trial**. Its purpose is to measure the design quantities that were missing from the original power story: the realized important-defect denominator, arm/family/origin escape rates, reviewer and matched-task dependence, false alarms, review time, and seed-realism retention. Those frozen pilot estimates must be used to preregister a separate powered replication before any effectiveness decision.

## Pilot question

Can the three-arm protocol be executed with matched controls and enough measurable signal to design a powered replication, and what baseline/denominator/dependence quantities does that replication need?

The original directional question remains exploratory: does the five-question Doubt the Machine gate show lower important-defect escape than both ordinary AI-assisted review and an equal-effort placebo checklist, and at what false-alarm and review-time cost?

## Why this is a pilot

The original primary estimand is **per important seeded defect**, but the preregistration fixed task-review counts rather than the number of important defects contributed by each task. Before any result existed, the repository also lacked empirical values for baseline escape probability and reviewer/matched-task dependence. With those quantities unspecified, confirmatory power and decidability were unknown.

The correction is not to invent assumptions after the fact. Experiment 001 keeps its fixed randomized design and becomes a planning pilot. It may report exploratory contrasts, but it cannot promote or kill the H-level effectiveness claim as a confirmatory result.

## Cohorts

Human and agent reviewers are **different cohorts** and must never be pooled in the primary pilot summaries.

For each cohort:

- use at least **12 distinct reviewer IDs**;
- record `reviewer_id`, `reviewer_type`, and `cohort_id` for every task;
- counterbalance conditions within reviewer where feasible;
- preserve reviewer and matched-task identifiers so dependence can be estimated for replication planning.

The pilot minimum of 12 reviewer IDs is not treated as evidence that small-cluster confirmatory intervals have adequate coverage. Dependence estimates are planning inputs, not a license to promote the effectiveness claim.

## The two-ended mind experiment

Every review is treated as a two-ended mind experiment. Each end has a human side and an AI side:

- the **artifact-origin end** — who or what produced the artifact under review: `human` or `agent`; and
- the **reviewer end** — who or what performs the review: the human cohort or the agent cohort.

Crossing them yields the preregistered endpoint matrix:

| Artifact origin | Reviewer side | Cell |
| --- | --- | --- |
| `human` | `human` | `human→human` |
| `human` | `agent` | `human→agent` |
| `agent` | `human` | `agent→human` |
| `agent` | `agent` | `agent→agent` |

Within one cohort run, the reviewer end is fixed, so the run covers two of the four cells; the mirrored cohort run covers the other two. A human-reviewer cohort covers `human→human` and `agent→human`. An agent-reviewer cohort covers `human→agent` and `agent→agent`.

`artifact_origin` remains a **crossed factor, not a confound**: both origin variants exist in every condition, task family, and cohort, seeded with the identical procedure, so origin differences can be measured rather than assumed.

## Task families

Construct matched tasks from four families:

1. factual/current-information review;
2. numerical or analytical review;
3. code-change review;
4. summarization/design review.

Each task contains zero or more deliberately seeded defects. Defects are authored before assignment and labeled by severity. Each task variant exists in both artifact-origin versions, and the defect-seeding procedure is identical for both. Reviewers do not see the answer key and are not told which origin side a task came from.

The pilot must report the **realized number of important seeded defects** per task, condition, family, and origin side. That observed denominator is one of the quantities needed to power the replication.

## Three conditions

Randomize matched task variants to:

- **Ordinary control** — normal review workflow, with no mandatory checklist.
- **Active placebo** — complete five generic attention fields: `TASK / SUMMARY / DETAILS / ALTERNATIVE / DECISION`. This arm controls for forced deliberation and added effort without explicitly asking for falsification, independent evidence, or reversibility.
- **Doubt gate** — complete `CLAIM / FAILURE / EVIDENCE / TEST / REVERSAL` before accepting or rejecting the artifact.

All conditions receive the same model/tool entitlement, source access, and time policy.

## Fixed sample and stopping rule

For one preregistered cohort, collect exactly **432 scorable task reviews: 144 per condition, 36 per task family per condition, and 18 per task family per condition per artifact-origin cell** (two origin sides × 216 = 432).

If both the human-reviewer and agent-reviewer cohorts run, the full crossed-endpoint plan contains **864 scorable reviews**.

Stop when those 432 scorable reviews are complete. Do not inspect interim outcomes to decide whether to continue.

A task may be replaced only for a preregistered exclusion such as answer-key leakage, corrupted input, or tool failure that prevents review. Every replacement and exclusion must be logged before outcome analysis.

The fixed 432-review plan is now a **pilot sample**, not a claim of 80% power or any other confirmatory power level. Do not extend N under the pilot amendment to chase a desirable result. Freeze and report the planning estimates, then design a separate replication.

## Pilot planning estimands

The original per-defect escape quantity is retained as a **descriptive planning estimand**:

- observed important-defect escape probability by condition;
- realized important-defect denominator per condition, task family, and artifact-origin side;
- task-level any-escape probability;
- false-alarm rate;
- review minutes and external checks;
- reviewer-level and matched-task dependence diagnostics;
- seed-realism retention and strata sizes.

Report exploratory Doubt-gate differences against **both** ordinary control and active placebo. Weighting and origin stratification remain as preregistered, but these contrasts are not confirmatory effectiveness tests.

Do not collapse error, false-alarm, and time coordinates into one post-hoc utility score.

## Reference effect region — not a pilot promotion gate

The original preregistration preserves a 10-percentage-point escape-reduction target against each comparator and a maximum 10-point false-alarm penalty. Those thresholds remain visible as correction history and a **reference for replication planning**.

Experiment 001 cannot claim that the gate “passed” this effect region, even if the point estimates happen to cross it. Confirmatory use of an effect region requires a separately powered and preregistered replication.

## Controls

- Equal task-family and defect-severity distribution across conditions, within each artifact-origin cell.
- Equal access to tools, sources, model, and time policy.
- Correct/no-defect tasks in every family, condition, and origin cell so “reject everything” cannot win.
- Both artifact-origin variants in every condition and family; reviewers blinded to origin.
- Held-out task variants not used while designing the gate.
- Hidden answer key until scoring.
- Active-placebo arm to isolate generic deliberation/Hawthorne effects.
- Human and agent cohorts analyzed separately.

## Seed-realism audit

Before the pilot run:

1. freeze the seed inventory and answer key;
2. have at least **two judges who did not author a given seed** rate whether it resembles a plausible organic AI/human-review failure rather than an artificial puzzle artifact, for seeds on both artifact-origin sides;
3. record the ratings and disagreements, with the artifact origin of each rated seed;
4. exclude or relabel implausible seeds **before randomization**, with a preserved audit trail;
5. do not rewrite seeds after outcome collection begins.

The pilot report must stratify results by seed-realism rating. Realism retention and resulting stratum sizes are themselves replication-planning inputs.

## Exploratory prediction

The original directional hypothesis is preserved rather than rewritten: the Doubt gate may show lower important-defect escape probability than ordinary review and the active placebo, with a review-time cost, and the direction may differ by artifact-origin side.

This is an exploratory prediction in Experiment 001. A null, adverse, or apparently positive result must be reported, but none is by itself a confirmatory promote-or-kill decision on the effectiveness claim.

## Pilot failure / design-retirement conditions

Retire or narrow the **experimental design** if any of these occur:

1. randomization or matched-control parity cannot be preserved;
2. the seed-realism audit leaves an unusable or severely distorted defect inventory;
3. endpoint coverage collapses on either artifact-origin side;
4. record integrity is insufficient to recover the realized important-defect denominator;
5. reviewer/matched-task identifiers are insufficient to estimate dependence for replication planning;
6. exclusions or tool failures make the fixed pilot sample uninterpretable.

Exploratory adverse or null effects are still evidence and must be reported. They may motivate doubt or narrowing, but this pilot does not label them a confirmatory kill of the H-level effectiveness claim.

## Stop condition

Do not add a richer framework, scoring ontology, or extra checklist layer until this pilot is completed, reported, or explicitly abandoned with a reason.

After the fixed pilot stops, freeze its planning estimates before choosing the confirmatory replication sample size, primary inferential method, or any changed effect criterion. The replication must have its own preregistration before its outcomes exist.

## Promotion rule

Experiment 001 may promote only **measured pilot-design statements**, such as:

- the realized important-defect denominator;
- observed arm/family/origin escape and false-alarm rates;
- dependence diagnostics;
- review-time and external-check distributions;
- seed-realism and feasibility findings.

It may **not** promote the Doubt gate as effective, safer, better, or as having passed the original effect region. Any effectiveness promotion requires a separately powered preregistration and later independent replication.

## Files

- `preregistration.json` — original machine-readable preregistration, preserved byte-for-byte.
- `amendment-2026-08-31-pilot.json` — prospective effective pilot amendment and power/decidability contract.
- `results.csv` — raw task-level observations; ships with headers only before execution.
- `retired.json` at repository root — machine-readable retired-rule ledger used by CI.

## Minimum reporting

Publish raw task rows, reviewer/cohort identity fields, artifact-origin assignment, condition assignment, seeded-defect severity, **realized important-defect denominator**, caught/missed status, false alarms, elapsed review time, external checks, exclusions/replacements, seed-realism ratings per origin side, and dependence diagnostics used for replication planning.

Negative and inconclusive exploratory results stay in the repository. The pilot report must end with the frozen planning inputs that a future powered preregistration uses—or state that the protocol is not viable enough to justify one.
