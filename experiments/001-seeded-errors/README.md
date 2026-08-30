# Experiment 001 — seeded-error review gate

**Status:** preregistered; no result has been collected yet.

This is the first direct test of the repository’s central practical hypothesis.

## Question

Does the five-question Doubt the Machine gate catch more important defects than ordinary AI-assisted review at an acceptable verification cost?

## Design

Construct matched tasks from at least four families:

1. factual/current-information review;
2. numerical or analytical review;
3. code-change review;
4. summarization/design review.

Each task contains zero or more deliberately seeded defects. Defects are authored before assignment and labeled by severity. Reviewers do not see the answer key.

Randomly assign matched tasks to:

- **Control:** ordinary review using the reviewer’s normal workflow.
- **Doubt gate:** reviewer must explicitly answer CLAIM / FAILURE / EVIDENCE / TEST / REVERSAL before accepting or rejecting the artifact.

The same reviewer may participate in both conditions, but matched variants must be counterbalanced to reduce learning effects.

## Primary metric

**Important-defect escape rate**: fraction of seeded high- or medium-severity defects that remain accepted after review.

Lower is better.

## Secondary metrics

- defect catch rate by severity;
- false-alarm rate on unseeded/correct items;
- review minutes per task;
- number of external checks performed;
- number of reversals after contradictory evidence;
- framing sensitivity on paired prompts where user stance changes but evidence does not.

## Controls

- Equal task families and defect-severity distribution across conditions.
- Equal access to tools, sources, model, and time cap.
- Include correct/no-defect tasks so “reject everything” cannot win.
- Include held-out task variants not used while designing the gate.
- Preserve the answer key separately until scoring.

## Prediction

The Doubt gate will reduce important-defect escape rate relative to ordinary review, while increasing median review time.

The framework is useful only if the reduction in important escapes is large enough to justify that cost for the tested task class.

## Kill conditions

The practical-effectiveness claim is killed or narrowed if any of these occur after the preregistered sample:

1. important-defect escape rate is not lower than control within the reported uncertainty;
2. the gain depends on rejecting substantially more correct work;
3. review-time cost dominates the gain under the declared utility analysis;
4. the effect disappears on held-out task variants;
5. framing checks increase contrarian errors rather than evidence-stable conclusions.

A failed result must be reported in `GRAVEYARD.md`; do not add new rules to rescue it before reporting the failure.

## Stop condition

Do not add a richer framework, scoring ontology, or extra checklist layer until this experiment is either completed or explicitly abandoned with a reason.

## Promotion rule

One positive internal experiment may promote only the bounded statement:

> “In Experiment 001, under the tested task distribution and review conditions, the Doubt gate reduced important-defect escapes by the measured amount at the measured review cost.”

General claims such as “safer”, “better”, or “effective for AI work” require held-out replication and an independent witness.

## Files

- `preregistration.json` — machine-readable audit contract.
- `results.csv` — schema for raw task-level observations. It intentionally ships with headers only.

## Minimum reporting

Publish raw task rows, condition assignment, seeded-defect severity, reviewer decision, caught/missed status, false alarms, elapsed review time, and the exact analysis used. Negative results stay in the repository.
