# Doubt the Machine

**Thirty practical rules for using AI without being fooled.**

> **Rule 0 applies to everything:** doubt this list too.

![Doubt the Machine poster](assets/doubt-the-machine.svg)

The operating loop is deliberately simple:

**DOUBT → MEASURE → TEST → REVERT → repeat**

This repository turns the poster into a small, forkable checklist for three different failure surfaces:

1. **Doubt the machine** — the AI is a tool, not a judge.
2. **Doubt the bits** — every answer is a guess; fluency is not truth.
3. **Doubt the build** — generated code still fails; run it, test it, and keep rollback cheap.

## 1. Doubt the machine

| # | Rule | Why it matters |
|---|---|---|
| 1 | Don't trust the praise | An AI will compliment almost anything. |
| 2 | Don't trust the criticism either | Push back and see if it holds. |
| 3 | Sounding right is not being right | Smooth text is not checked text. |
| 4 | Ask how it could be wrong | Better than asking only “is this right?” |
| 5 | Make it prove it | Run the test. Show the counterexample. |
| 6 | Ask again in a fresh chat | Old context bends the answer. |
| 7 | Check with something outside the AI | A person, a test, a benchmark, a primary source. |
| 8 | Notice what it leaves out | The real objections often hide there. |
| 9 | Count how often it disagrees with you | Never? Something is off. |
| 0 | Doubt this list too | It came from an AI-assisted process. |

## 2. Doubt the bits

| # | Rule | Why it matters |
|---|---|---|
| 1 | An AI predicts. It does not know | Its mechanism is prediction, not privileged access to truth. |
| 2 | Fluent means predictable, not true | Easy to read is not the same as correct. |
| 3 | It can't add facts it never had | Ask where the information came from. |
| 4 | Every rewrite loses something | Summaries drop what they do not expect to matter. |
| 5 | Long chats get noisy | Old context can drown the new question. |
| 6 | Repeat what matters | Redundancy protects against misreading. |
| 7 | One answer is one sample | Ask again; compare outputs and methods. |
| 8 | Confident tone is not accuracy | Same guess, louder voice. |
| 9 | “Best” can't be proven in the abstract | Usually it only means “better than the tested baseline.” |
| 0 | Doubt the compression | This panel is itself a compressed account. |

## 3. Doubt the build

| # | Rule | Why it matters |
|---|---|---|
| 1 | “The AI says it works” means nothing | Run it. Reproduce it yourself. |
| 2 | No test, no merge | AI code without tests is a guess with syntax. |
| 3 | Read every line before you ship | Generated code hides shortcuts and assumptions. |
| 4 | Ask it to make things safe to retry | Idempotency and recovery rarely appear by default. |
| 5 | Make it add logs, not only features | You need to watch it fail. |
| 6 | Ask it to delete, not just add | Generation tends toward accretion. |
| 7 | Prefer boring, well-known tools | Novel-tool hallucinations and API drift are common. |
| 8 | Assume it half-works | Plan for edge cases, partial failure, and bad inputs. |
| 9 | Small changes, easy rollback | Never let it rewrite everything at once. |
| 0 | Test this list too | The reviewer is still you. |

## A minimal working protocol

Before accepting an AI-assisted claim or change:

```text
1. State the claim.
2. State at least one plausible failure mode.
3. Identify evidence that is independent of the model.
4. Run the cheapest falsifying test first.
5. Record the result.
6. Keep the change reversible.
7. Re-test after integration.
```

For code, a compact merge gate is:

```text
reproduce → test → inspect diff → observe → rollback-plan → merge
```

## What this is not

This is not an anti-AI manifesto. It is a **calibration discipline**: use AI aggressively, but move confidence only when evidence moves.

The goal is not distrust for its own sake. The goal is to preserve agency, falsifiability, and reversibility while gaining the speed and creative leverage of modern models.

## Contributing

Disagree with a rule? Good. Open an issue or PR with:

- the rule you challenge,
- a concrete counterexample,
- evidence or a reproducible test,
- and a proposed replacement.

The repository should improve by surviving criticism, not by collecting agreement.

---

**Rule 0:** this README was assembled with AI assistance. Doubt it too.
