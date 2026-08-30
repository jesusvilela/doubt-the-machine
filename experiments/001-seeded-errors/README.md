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

## Task families

Construct matched tasks from four families:

1. factual/current-information review;
2. numerical or analytical review;
3. code-change review;
4. summarization/design review.

Each task contains zero or more deliberately seeded defects. Defects are authored before assignment and labeled by severity. Reviewers do not see the answer key.

## Three conditions

Randomize matched task variants to:

- **Ordinary control** — normal review workflow, with no mandatory checklist.
- **Active placebo** — complete five generic attention fields: `TASK / SUMMARY / DETAILS / ALTERNATIVE / DECISION`. This arm controls for forced deliberation and added effort without explicitly asking for falsification, independent evidence, or reversibility.
- **Doubt gate** — complete `CLAIM / FAILURE / EVIDENCE / TEST / REVERSAL` before accepting or rejecting the artifact.

All conditions receive the same model/tool entitlement, source access, and time policy.

## Fixed sample and stopping rule

For one preregistered cohort, collect exactly **216 scorable task reviews: 72 per condition, 18 per task family per condition**.

Stop when those 216 scorable reviews are complete. Do not inspect interim outcomes to decide whether to continue.

A task may be replaced only for a preregistered exclusion such as answer-key leakage, corrupted input, or tool failure that prevents review. Every replacement and exclusion must be logged before outcome analysis.

If the resulting uncertainty is too wide to distinguish the prespecified effect region, report the experiment as **inconclusive**. Do not extend N under the same preregistration.

## Primary estimand

**Per-defect important-defect escape probability** among preregistered medium/high-severity seeded defects.

Report the Doubt-gate difference against **both** ordinary control and active placebo. Weight the four task families equally and use uncertainty that clusters by reviewer and matched task set.

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

- Equal task-family and defect-severity distribution across conditions.
- Equal access to tools, sources, model, and time policy.
- Correct/no-defect tasks in every family so “reject everything” cannot win.
- Held-out task variants not used while designing the gate.
- Hidden answer key until scoring.
- Active-placebo arm to isolate generic deliberation/Hawthorne effects.
- Human and agent cohorts analyzed separately.

## Seed-realism audit

Before the main run:

1. freeze the seed inventory and answer key;
2. have at least **two judges who did not author a given seed** rate whether it resembles a plausible organic AI/human-review failure rather than an artificial puzzle artifact;
3. record the ratings and disagreements;
4. exclude or relabel implausible seeds **before randomization**, with a preserved audit trail;
5. do not rewrite seeds after outcome collection begins.

The final report must stratify results by seed-realism rating so a result driven only by artificial-looking defects is visible.

## Prediction

The Doubt gate will reduce important-defect escape probability relative to both ordinary review and the active placebo, while increasing review time.

## Kill / narrow conditions

The specific-gate effectiveness claim is killed or narrowed if any of these occur:

1. the Doubt gate does not enter the prespecified positive effect region against **both** comparators;
2. any apparent gain is explained by a substantially higher false-alarm rate;
3. the advantage disappears on held-out variants;
4. the advantage disappears when clustering by reviewer/matched task is respected;
5. framing checks increase contrarian errors rather than evidence-stable conclusions;
6. the effect is confined to low-realism seeded defects.

A failed result must be reported in `GRAVEYARD.md`; do not add new rules to rescue it before reporting the failure.

## Stop condition

Do not add a richer framework, scoring ontology, or extra checklist layer until this experiment is completed, reported inconclusive, or explicitly abandoned with a reason.

## Promotion rule

One positive internal cohort may promote only the bounded statement:

> “In Experiment 001, for the tested cohort, task distribution, and review conditions, the Doubt gate reduced important-defect escapes relative to ordinary review and an equal-effort placebo by the measured amount, at the measured false-alarm and review-time cost.”

General claims such as “safer”, “better”, or “effective for AI work” require held-out replication and an independent witness.

## Files

- `preregistration.json` — machine-readable audit contract.
- `results.csv` — raw task-level observations; ships with headers only before execution.
- `retired.json` at repository root — machine-readable retired-rule ledger used by CI.

## Minimum reporting

Publish raw task rows, reviewer/cohort identity fields, condition assignment, seeded-defect severity, caught/missed status, false alarms, elapsed review time, exclusions/replacements, seed-realism ratings, and the exact analysis used. Negative and inconclusive results stay in the repository.
