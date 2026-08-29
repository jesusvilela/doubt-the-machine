# Principles

Doubt the Machine is intentionally small. These notes hold the assumptions that would make the five-minute README too heavy.

## 1. Treat outputs as proposals

A generated answer can be useful, original, correct, partially correct, or wrong. None of those properties follows from fluency alone. The operational stance is therefore simple: **an output is a proposal whose acceptance depends on evidence appropriate to the claim**.

This avoids an unproductive shortcut: arguing about whether a model “really knows.” Whatever philosophical position one takes, generated text does not authenticate itself.

## 2. Evidence is claim-relative

There is no universal verification ritual. Different claims require different evidence.

- A current factual claim benefits from a primary, dated source.
- A numerical claim benefits from independent recomputation.
- A software claim benefits from execution, tests, and observability.
- A comparative claim benefits from a named baseline, metric, dataset, and environment.
- A summary benefits from comparison against the source and inspection of omissions.
- A high-stakes recommendation benefits from domain-qualified review in addition to model output.

Verification effort should scale with **uncertainty × consequence × irreversibility**.

## 3. Independence matters

Self-critique can be useful, but the same model reviewing its own answer is not the same thing as independent evidence. Re-prompting, changing temperature, or starting a fresh chat may reveal variance and contradictions, yet common training data, architecture, tools, or framing can preserve correlated errors.

Prefer evidence that can disagree for a different reason: primary sources, executable tests, independent measurements, alternative implementations, or people with relevant expertise.

## 4. Falsification beats reassurance

“Is this right?” invites confirmation. “What observation would show this is wrong?” creates a testable boundary.

A strong AI-assisted workflow seeks:

1. a precise claim;
2. at least one plausible failure mode;
3. a test that discriminates between success and failure;
4. an observable result;
5. a reversible next step.

The goal is not philosophical certainty. It is to move from vague plausibility to better-calibrated belief and safer action.

## 5. Compression is transformation

Summaries, rewrites, abstractions, embeddings, and context reduction are not neutral copies. They preserve some structure and discard other structure.

The important question is not “did anything get lost?” Something almost always did. The question is: **did the transformation lose information relevant to the decision being made?**

For critical material, preserve access to the source and check qualifiers, exceptions, units, dates, and scope.

## 6. Sampling exposes variance, not truth

Multiple answers can reveal instability, anchoring, and alternative hypotheses. Agreement across samples can be useful evidence about model consistency, but repeated agreement is not independent proof of correctness.

Use re-sampling to answer: “How sensitive is this output to context and generation?” Use external evidence to answer: “Is the claim actually supported?”

## 7. Baselines make superlatives meaningful

Words such as *best*, *faster*, *safer*, *SOTA*, and *better* are incomplete without a comparison frame.

A defensible comparison names:

- the baseline;
- the metric;
- the dataset or workload;
- the environment;
- relevant uncertainty or variance;
- and the conditions under which the result holds.

Without those, a superlative is rhetoric, not measurement.

## 8. Reversibility is part of correctness

A change can be locally correct and still be operationally dangerous if it is difficult to undo. For AI-assisted engineering, prefer:

- small diffs;
- explicit state transitions;
- feature flags where useful;
- idempotent operations;
- bounded retries;
- backups and migrations with rollback plans;
- observability before scale-up.

Reversibility lowers the cost of discovering that your model, test, or assumption was wrong.

## 9. Humans remain in the failure model

This project does not assume humans are reliable referees. Humans anchor, hallucinate, omit, overfit to narratives, and reward confidence too.

The point of the framework is therefore not “human good, AI bad.” It is to build **systems of disagreement** in which claims can be checked by evidence, tests, measurements, and reviewers with different failure modes.

## 10. Rule 0 prevents dogma

Every rule in this repository is provisional.

A rule should be weakened, rewritten, split, or removed when a reproducible counterexample or stronger formulation warrants it. The framework succeeds when it becomes easier to criticize over time, not harder.

The governing loop is the same loop the framework recommends:

```text
DOUBT → MEASURE → TEST → REVERT → REPEAT
```
