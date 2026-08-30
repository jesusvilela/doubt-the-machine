# Falsifiers

Rule 0 is only meaningful if this framework can lose.

The claims below are deliberately narrower than “skepticism is good.” They concern whether this particular operating discipline improves AI-assisted work enough to justify its cost.

## Claim under test

> For tasks with non-trivial error cost, the Doubt the Machine gate can reduce important undetected errors without imposing verification cost that overwhelms the benefit.

**Current evidence status:** hypothesis. The repository does not yet contain a completed controlled experiment establishing this claim.

## Observations that would weaken or kill the claim

1. **No detection benefit**  
   Across preregistered matched tasks, the gated condition catches no more seeded important defects than ordinary review within uncertainty.

2. **Cost dominates benefit**  
   Any improvement in defect detection requires enough additional review time that the preregistered utility criterion is worse than ordinary review for the task class.

3. **False alarms erase the gain**  
   The gate causes materially more correct work to be rejected, rewritten, or delayed without compensating reduction in important escapes.

4. **Framing checks create contrarian failure**  
   Replacing agreement-seeking with explicit pushback causes conclusions to track requested disagreement rather than evidence. In that case the framing rule must be weakened or redesigned.

5. **The checklist is ceremonial**  
   Reviewers complete the fields but decisions do not change when falsifying evidence is presented. A process that cannot reverse a decision is verification theatre, not a falsification discipline.

6. **The framework does not generalize across task types**  
   If benefits appear only on seeded toy tasks and disappear on held-out factual, coding, summarization, or design tasks, claims must be restricted to the task families that survive replication.

## Retirement policy

A killed claim is not rescued by adding more rules or richer terminology. Record the result in `GRAVEYARD.md`, preserve the raw measurements, and either:

- narrow the claim to the surviving domain;
- replace the failed rule with a testable alternative; or
- retire the rule or framework claim.

## Promotion policy

Do not call this framework “effective”, “safer”, or “better” in general based on one internal experiment. Promotion requires:

1. a preregistered comparison against a simple baseline;
2. raw results including negative outcomes;
3. uncertainty for the primary effect;
4. at least one held-out or independently constructed task set;
5. replication by a person, model, or implementation that did not author the original benchmark.

Until then, the strongest honest description is: **a falsifiable verification and reversibility discipline under active self-test**.
