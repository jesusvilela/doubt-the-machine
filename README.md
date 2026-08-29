# Doubt the Machine

**A five-minute operating manual for using AI without confusing fluency with evidence.**

> **Rule 0:** apply this framework to itself. Doubt it, measure it, test it, and revert it when it fails.

![Doubt the Machine poster](assets/doubt-the-machine.svg)

```text
DOUBT → MEASURE → TEST → REVERT → REPEAT
```

AI is useful precisely because it can generate plausible answers, alternatives, code, summaries, and plans extremely quickly. That same property creates the central failure mode this project is about: **confidence can move faster than evidence**.

Doubt the Machine is not an argument for using AI less. It is a small discipline for using it **more aggressively without outsourcing judgment**.

The framework separates three surfaces that are easy to mix together:

1. **Doubt the machine** — interaction and authority: do not confuse agreement, criticism, tone, or confidence with evidence.
2. **Doubt the bits** — information and uncertainty: track provenance, inference, compression, context, sampling, and baselines.
3. **Doubt the build** — execution and operations: generated code is a proposal until it survives tests, inspection, observation, and rollback.

The poster is deliberately compressed and memorable. **This README is the canonical five-minute version.** The deeper rationale lives in [PRINCIPLES.md](PRINCIPLES.md).

## Use it in 60 seconds

Before accepting an AI-assisted claim or change, ask five things:

```text
1. CLAIM      What exactly am I being asked to believe or merge?
2. FAILURE    What is one plausible way it could be wrong?
3. EVIDENCE   What evidence is meaningfully independent of the model?
4. TEST       What is the cheapest test that could falsify it?
5. REVERSAL   If I am wrong, can I undo the decision cheaply?
```

Then act on the result:

**accept → revise → test again → or revert.**

The amount of verification should be proportional to the cost of being wrong. A low-stakes brainstorming prompt does not need a forensic process. A production migration, financial decision, medical claim, security change, or irreversible action does.

## Match the evidence to the claim

| Claim | Better evidence |
|---|---|
| Current factual claim | Primary or live source; check date and scope |
| Number or calculation | Recompute independently; inspect units and assumptions |
| Code behavior | Reproducible run, tests, edge cases, logs, CI |
| “Best”, “faster”, “SOTA” | Named baseline, metric, dataset, environment, uncertainty |
| Summary | Compare against the source; inspect omissions and changed qualifiers |
| Design recommendation | Alternatives, trade-offs, failure modes, constraints |
| High-stakes decision | Primary evidence plus qualified human review where appropriate |

The important word is **independent**. Asking the same model to certify its own answer can expose inconsistencies, but it is not equivalent to an external check.

## Panel 1 — Doubt the machine

**The AI is a tool, not a judge.** Treat its social signals as interface behavior, not epistemic authority.

| # | Rule | Operational meaning |
|---|---|---|
| 1 | **Don’t trust the praise** | Approval does not make a claim more likely to be true. |
| 2 | **Don’t trust the criticism either** | Push back. Good criticism should survive a counterargument. |
| 3 | **Sounding right is not being right** | Fluency is presentation quality, not verification. |
| 4 | **Ask how it could be wrong** | Request failure modes, hidden assumptions, and counterexamples. |
| 5 | **Make it prove it** | Ask for evidence appropriate to the claim: source, derivation, test, or falsifier. |
| 6 | **Ask again in fresh context** | A fresh run can reveal context anchoring. It is another sample, not guaranteed independence. |
| 7 | **Check outside the AI** | Use primary sources, executable tests, benchmarks, data, or people with relevant expertise. |
| 8 | **Notice what it leaves out** | Missing alternatives, qualifiers, and objections often matter more than polished prose. |
| 9 | **Count how often it disagrees with you** | If disagreement never happens, explicitly test for sycophancy and framing bias. |
| 0 | **Doubt this list too** | A useful framework must remain editable by evidence. |

The point is not reflexive skepticism. It is **calibration**: agreement and confidence should rise only when the quality of evidence rises.

## Panel 2 — Doubt the bits

**Generated information is not self-authenticating.** Separate what is sourced, inferred, compressed, sampled, or guessed.

| # | Rule | Operational meaning |
|---|---|---|
| 1 | **An AI predicts; treat output as a proposal, not proof** | Avoid metaphysical debates about “knowing”; operationally, generated text does not certify itself. |
| 2 | **Fluent does not mean true** | Readability can increase trust without increasing accuracy. |
| 3 | **Generated detail needs provenance** | Models can derive new consequences, but unsupported specifics still need evidence. |
| 4 | **Every rewrite can lose something** | Compression changes information. Check dropped conditions, exceptions, and uncertainty. |
| 5 | **Long chats get noisy** | Earlier assumptions, errors, and goals can bias later answers. Re-state the current task when needed. |
| 6 | **Repeat what matters** | Restate critical constraints, invariants, definitions, and non-negotiables. |
| 7 | **One answer is one sample** | Re-sample when variance matters; compare methods, not only wording. |
| 8 | **Confident tone is not accuracy** | Separate style from evidence and, when available, measured confidence. |
| 9 | **“Best” needs a baseline** | No superlative without a comparator, metric, data, and conditions. |
| 0 | **Doubt the compression** | This panel is itself a lossy model of a much larger problem. |

A useful habit is to label important statements as **source / inference / hypothesis / unknown**. That small distinction prevents many arguments about different things from collapsing into one confident paragraph.

## Panel 3 — Doubt the build

**Generated code still has to survive reality.** The unit of trust is not the explanation; it is the observed behavior of the system under the conditions you care about.

| # | Rule | Operational meaning |
|---|---|---|
| 1 | **“The AI says it works” means nothing** | Run it in the real environment or a faithful reproduction. |
| 2 | **No test, no merge** | Tests need to cover the changed behavior and relevant failure paths. |
| 3 | **Own every changed line** | Review the diff at the right level; generation does not transfer responsibility. |
| 4 | **Make retries safe** | Prefer idempotency, explicit state transitions, bounded retries, and recoverable operations. |
| 5 | **Add logs, not only features** | Instrument success and failure paths so reality can disagree visibly. |
| 6 | **Ask it to delete, not just add** | Generated systems accumulate code easily. Remove dead paths, duplicate abstractions, and speculative complexity. |
| 7 | **Prefer inspectable dependencies** | Familiar, documented, maintained tools are easier to verify; novel tools need stronger checking, not automatic rejection. |
| 8 | **Assume partial failure** | Network, storage, permissions, data, dependencies, and users fail independently. Design for that. |
| 9 | **Small changes, easy rollback** | Keep blast radius low. A reversible improvement beats an impressive rewrite you cannot safely undo. |
| 0 | **Test this list too** | Process rules are hypotheses about better engineering, not commandments. |

A compact merge gate is:

```text
reproduce → test → inspect diff → exercise failure → observe → rollback-plan → merge
```

## Rule 0 is the important one

Without Rule 0, a checklist against blind trust can become another object of blind trust.

So this project has a simple contract:

- rules may be challenged;
- wording may be tightened when it overclaims;
- counterexamples are first-class contributions;
- memorable slogans may be less precise than the canonical explanation;
- changes should be small enough to inspect and revert;
- no rule is protected from deletion.

The target is not permanent agreement. It is a framework that **gets harder to fool as people try to break it**.

## What this is — and is not

This is a compact **verification and reversibility discipline** for human–AI work.

It is not a claim that AI is uniquely unreliable, that humans are reliable by default, or that every output requires heavyweight verification. Humans hallucinate, anchor, compress, omit, and rationalize too. The useful asymmetry is speed: AI can produce more plausible material per minute than a human can carefully verify. The workflow therefore needs an explicit braking mechanism.

That mechanism is intentionally boring:

**doubt the claim → measure what matters → test the failure mode → revert cheaply when reality disagrees.**

## Contributing

The best contribution is not “I like this.” It is a case where a rule fails, overreaches, conflicts with another rule, or misses an important failure mode.

See [CONTRIBUTING.md](CONTRIBUTING.md). For the assumptions underneath the framework, see [PRINCIPLES.md](PRINCIPLES.md).

## License

Text and visual framework: [CC BY 4.0](LICENSE.md). Reuse, remix, and improve it with attribution.

---

**Rule 0:** this README was assembled with AI assistance. Doubt it too.
