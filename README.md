# Doubt the Machine

**A five-minute operating manual for using AI without confusing fluency with evidence.**

> **Rule 0:** apply this framework to itself. Doubt it, measure it, test it, and revert it when it fails.

![Doubt the Machine poster](assets/doubt-the-machine.svg)

```text
DOUBT → MEASURE → TEST → REVERT → REPEAT
```

AI can generate plausible answers, code, summaries, and plans much faster than we can verify them. That creates the core failure mode this project addresses:

> **confidence can move faster than evidence.**

Doubt the Machine is not an argument for using AI less. It is a small discipline for using it **more aggressively without outsourcing judgment**.

There are three surfaces:

1. **Doubt the machine** — interaction and authority.
2. **Doubt the bits** — information and uncertainty.
3. **Doubt the build** — execution and operations.

The poster is compressed for memory. **This README is the canonical five-minute version.** The rationale underneath it lives in [PRINCIPLES.md](PRINCIPLES.md).

## Use it in 60 seconds

Before accepting an AI-assisted claim or change:

```text
1. CLAIM      What exactly am I being asked to believe or merge?
2. FAILURE    What is one plausible way it could be wrong?
3. EVIDENCE   What evidence is meaningfully independent of the model?
4. TEST       What is the cheapest test that could falsify it?
5. REVERSAL   If I am wrong, can I undo the decision cheaply?
```

Then **accept, revise, test again, or revert**.

Verification effort should scale with the cost of being wrong. Brainstorming needs little ceremony. Production, security, medical, financial, or irreversible decisions need much more.

## Match the evidence to the claim

| Claim | Better evidence |
|---|---|
| Current fact | Primary or live source; check date and scope |
| Number | Recompute; inspect units and assumptions |
| Code behavior | Reproducible run, tests, edge cases, logs, CI |
| “Best”, “faster”, “SOTA” | Baseline, metric, dataset, environment, uncertainty |
| Summary | Compare with source; inspect omissions and changed qualifiers |
| Design recommendation | Alternatives, constraints, trade-offs, failure modes |
| High-stakes decision | Primary evidence plus qualified human review where appropriate |

The key word is **independent**. A model critiquing its own answer can reveal inconsistencies; it is not the same as an external check.

## 1 — Doubt the machine

**The AI is a tool, not a judge.** Social signals are not evidence.

| # | Rule | Operational meaning |
|---|---|---|
| 1 | **Don’t trust the praise** | Approval does not make a claim true. |
| 2 | **Don’t trust the criticism either** | Push back. Good criticism should survive a counterargument. |
| 3 | **Sounding right is not being right** | Fluency is presentation, not verification. |
| 4 | **Ask how it could be wrong** | Request failure modes, assumptions, and counterexamples. |
| 5 | **Make it prove it** | Ask for a source, derivation, test, or falsifier. |
| 6 | **Ask again in fresh context** | Expose anchoring; remember this is another sample, not guaranteed independence. |
| 7 | **Check outside the AI** | Use primary sources, tests, benchmarks, data, or relevant expertise. |
| 8 | **Notice what it leaves out** | Missing alternatives and qualifiers can matter more than polished prose. |
| 9 | **Count how often it disagrees with you** | If never, test explicitly for sycophancy and framing bias. |
| 0 | **Doubt this list too** | Rules remain editable by evidence. |

## 2 — Doubt the bits

**Generated information is not self-authenticating.** Separate source, inference, hypothesis, and unknown.

| # | Rule | Operational meaning |
|---|---|---|
| 1 | **Treat output as a proposal, not proof** | Generated text does not certify itself. |
| 2 | **Fluent does not mean true** | Readability can increase trust without increasing accuracy. |
| 3 | **Generated detail needs provenance** | New reasoning is possible; unsupported specifics still need evidence. |
| 4 | **Every rewrite can lose something** | Check dropped conditions, exceptions, and uncertainty. |
| 5 | **Long chats get noisy** | Old assumptions and errors can bias later answers. Re-state the task when needed. |
| 6 | **Repeat what matters** | Restate critical constraints, invariants, and definitions. |
| 7 | **One answer is one sample** | Re-sample when variance matters; compare methods, not only wording. |
| 8 | **Confident tone is not accuracy** | Separate style from evidence. |
| 9 | **“Best” needs a baseline** | No superlative without comparator, metric, data, and conditions. |
| 0 | **Doubt the compression** | This panel is itself a lossy model. |

## 3 — Doubt the build

**Generated code still has to survive reality.** Trust observed behavior, not the explanation around it.

| # | Rule | Operational meaning |
|---|---|---|
| 1 | **“The AI says it works” means nothing** | Run it in the real environment or a faithful reproduction. |
| 2 | **No test, no merge** | Cover changed behavior and relevant failure paths. |
| 3 | **Own every changed line** | Review the diff; generation does not transfer responsibility. |
| 4 | **Make retries safe** | Prefer idempotency, explicit state, bounded retries, and recovery. |
| 5 | **Add logs, not only features** | Instrument failure so reality can disagree visibly. |
| 6 | **Ask it to delete, not just add** | Remove dead paths, duplicate abstractions, and speculative complexity. |
| 7 | **Prefer inspectable dependencies** | Familiar, documented tools are easier to verify; novelty needs stronger checking. |
| 8 | **Assume partial failure** | Network, storage, permissions, data, dependencies, and users fail independently. |
| 9 | **Small changes, easy rollback** | Keep blast radius low and reversal cheap. |
| 0 | **Test this list too** | Process rules are hypotheses, not commandments. |

For code, the compact gate is:

```text
reproduce → test → inspect diff → exercise failure → observe → rollback-plan → merge
```

## Rule 0 is the important one

Without Rule 0, a checklist against blind trust can become another object of blind trust.

So:

- challenge every rule;
- prefer counterexamples over agreement;
- tighten wording when it overclaims;
- keep changes small and reversible;
- protect no rule from deletion.

The target is a framework that **gets harder to fool as people try to break it**.

## What this is — and is not

This is a compact **verification and reversibility discipline** for human–AI work.

It does not assume humans are reliable by default. Humans also anchor, omit, overclaim, and rationalize. The useful asymmetry is speed: AI can produce plausible material faster than a human can carefully verify it.

The braking mechanism is intentionally boring:

**doubt the claim → measure what matters → test the failure mode → revert cheaply when reality disagrees.**

## Contributing

Found a counterexample or overclaim? Good. See [CONTRIBUTING.md](CONTRIBUTING.md) and challenge it with evidence. The deeper assumptions are in [PRINCIPLES.md](PRINCIPLES.md).

## License

Text and original visual framework: [CC BY 4.0](LICENSE.md). Reuse, remix, and improve it with attribution.

---

**Rule 0:** this README was assembled with AI assistance. Doubt it too.
