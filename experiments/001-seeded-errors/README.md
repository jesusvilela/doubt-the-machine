# Experiment 001 — seeded-error review gate

**Status:** preregistered; no result has been collected yet.

This is the first direct test of the repository’s central practical hypothesis. It is designed to separate the effect of the specific Doubt gate from the effect of merely slowing a reviewer down.

## Question

Does the five-question Doubt the Machine gate catch more important defects than both ordinary AI-assisted review and an equal-effort placebo checklist, without an unacceptable increase in false alarms or review cost?

## Cohorts

Human and agent reviewers are **different cohorts** and must never be pooled in the primary analysis.

For each cohort:

- use at least **12 distinct reviewer IDs**;
- record `reviewer_id`, `reviewer_type`, and `cohort_id` for every task;
- counterbalance conditions within reviewer where feasible;
- analyze reviewer clustering explicitly.

A later human replication cannot be presented as confirming an agent-only run, or vice versa, without reporting the cohort difference.

## The two ends: artifact origin and reviewer side

Every review has two ends, and each end has a human side and an AI side:

- the **artifact-origin end** — who or what produced the artifact under review: `human` or `agent`; and
- the **reviewer end** — who or what performs the review: the human cohort or the agent cohort.

Crossing them yields four cells: human→human, human→agent, agent→human, and agent→agent (origin→reviewer). Within one cohort run, the reviewer end is fixed, so the run covers two of the four cells; the mirrored cohort run covers the other two.

`artifact_origin` is therefore a **crossed factor, not a confound**: both origin variants exist in every condition, task family, and cohort, seeded with the identical procedure, so any origin difference is measurable rather than assumed.

## Task families

Construct matched tasks from four families:

1. factual/current-information review;
2. numerical or analytical review;
3. code-change review;
4. summarization/design review.

Each task contains zero or more deliberately seeded defects. Defects are authored before assignment and labeled by severity. Each task variant exists in both artifact-origin versions, and the defect-seeding procedure is identical for both. Reviewers do not see the answer key and are not told which origin side a task came from.

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

If the resulting uncertainty is too wide to distinguish the prespecified effect region, report the experiment as **inconclusive**. Do not extend N under the same preregistration.

## Primary estimand

**Per-defect important-defect escape probability** among preregistered medium/high-severity seeded defects.

Report the Doubt-gate difference against **both** ordinary control and active placebo. Weight the four task families equally, pool the balanced artifact-origin cells for the primary contrast, and use uncertainty that clusters by reviewer and matched task set. The origin-by-condition interaction is a preregistered secondary analysis, and results are always reported per origin side.

A secondary task-level estimand reports whether **any** important defect escaped on each task.

## Secondary metrics

- defect catch rate by severity;
- false-alarm rate on unseeded/correct items;
- review minutes per task;
- number of external checks performed;
- number of reversals after contradictory evidence;
- framing sensitivity on paired prompts where user stance changes but evidence does not.

Do not collapse these into one post-hoc utility score. Report the error/time trade-off as a typed result or Pareto comparison.

## Prespecified effect region

A positive result requires all of the following:

1. the Doubt gate has a lower important-defect escape probability than **ordinary control**;
2. it also has a lower escape probability than the **active placebo**;
3. the estimated absolute reduction versus each comparator is at least **10 percentage points**;
4. the reported uncertainty for each primary contrast excludes zero benefit;
5. false-alarm rate is not more than **10 percentage points** worse than either comparator.

Review time is reported separately. A large time cost can make the gate unattractive operationally, but it does not get converted after the fact into an invented exchange rate between minutes and escaped defects.

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

Before the main run:

1. freeze the seed inventory and answer key;
2. have at least **two judges who did not author a given seed** rate whether it resembles a plausible organic AI/human-review failure rather than an artificial puzzle artifact, for seeds on both artifact-origin sides;
3. record the ratings and disagreements, with the artifact origin of each rated seed;
4. exclude or relabel implausible seeds **before randomization**, with a preserved audit trail;
5. do not rewrite seeds after outcome collection begins.

The final report must stratify results by seed-realism rating so a result driven only by artificial-looking defects is visible.

## Prediction

The Doubt gate will reduce important-defect escape probability relative to both ordinary review and the active placebo, while increasing review time. The advantage is predicted to be directionally consistent across both artifact-origin sides; a side-specific effect narrows rather than promotes the claim.

## Kill / narrow conditions

The specific-gate effectiveness claim is killed or narrowed if any of these occur:

1. the Doubt gate does not enter the prespecified positive effect region against **both** comparators;
2. any apparent gain is explained by a substantially higher false-alarm rate;
3. the advantage disappears on held-out variants;
4. the advantage disappears when clustering by reviewer/matched task is respected;
5. framing checks increase contrarian errors rather than evidence-stable conclusions;
6. the effect is confined to low-realism seeded defects;
7. the advantage is confined to, or reverses on, one artifact-origin side — in that case the claim narrows to the surviving side instead of promoting a general result.

A failed result must be reported in `GRAVEYARD.md`; do not add new rules to rescue it before reporting the failure.

## Stop condition

Do not add a richer framework, scoring ontology, or extra checklist layer until this experiment is completed, reported inconclusive, or explicitly abandoned with a reason.

## Promotion rule

One positive internal cohort may promote only the bounded statement:

> “In Experiment 001, for the tested cohort, task distribution, and review conditions, the Doubt gate reduced important-defect escapes relative to ordinary review and an equal-effort placebo by the measured amount, at the measured false-alarm and review-time cost, on both artifact-origin sides.”

General claims such as “safer”, “better”, or “effective for AI work” require held-out replication and an independent witness.

## Files

- `preregistration.json` — machine-readable audit contract.
- `results.csv` — raw task-level observations; ships with headers only before execution.
- `retired.json` at repository root — machine-readable retired-rule ledger used by CI.

## Minimum reporting

Publish raw task rows, reviewer/cohort identity fields, artifact-origin assignment, condition assignment, seeded-defect severity, caught/missed status, false alarms, elapsed review time, exclusions/replacements, seed-realism ratings per origin side, and the exact analysis used. Negative and inconclusive results stay in the repository.
