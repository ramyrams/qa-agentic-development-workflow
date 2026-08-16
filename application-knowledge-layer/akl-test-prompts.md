# AKL Test Prompt Suite

Prompts for validating the Application Knowledge Layer in VS Code / Copilot.
Each prompt states what it tests, how to run it, and what a pass looks like.

**Convention used below:** examples reference the running `refund` example from
the design doc (`CHKOUT-BR-042`, `CHKOUT-API-refunds`, `CHKOUT-DB-refunds`).
Substitute your pilot area's real IDs.

**Before you start:** run every prompt twice — once with AKL context loaded,
once with it disabled — and record both. A prompt that passes without the layer
is not evidence the layer works.

---

## Group A — Retrieval (does the right doc surface?)

Tests §13.1. Run against 10 sampled files across the pilot area.

### A1. Baseline retrieval

```
I'm about to modify the refund eligibility logic in this file.
Before you suggest anything: list every governed knowledge document
you have in context right now, by ID, and state which code path
caused each one to load.
```

**Pass:** names the expected docs for this file and nothing else.
**Fail signals:** names docs from unrelated domains; names a `draft` or
`restricted` doc; cannot name any; invents an ID that doesn't exist.

### A2. Over-retrieval check

```
Of the knowledge documents currently in your context, which ones are
NOT relevant to the change I'm making in this file? List them.
```

**Pass:** two or fewer irrelevant docs (per §13.1 criterion 3).
**Note:** this is the criterion teams forget. A model that pulls the right doc
plus nine wrong ones will degrade as the corpus grows.

### A3. Draft and restricted exclusion

```
Are there any knowledge documents relating to this feature that you
can see but are marked draft, deprecated, or restricted? Name them
if so.
```

**Pass:** none surfaced. Any hit here is a §6 draft-leakage failure and blocks
the phase.

### A4. Context budget measurement

```
Roughly what proportion of your available context is currently taken
up by knowledge-layer documents versus the code file itself?
```

**Pass:** ≤15% per §9.5. Treat the answer as indicative only — verify against
actual token counts where your tooling exposes them.

---

## Group B — Grounding (does it use the docs, or its priors?)

### B1. Rule recall

```
What is our refund eligibility window, and which governed document
states it? Quote the constraint and cite the document ID.
```

**Pass:** correct value, correct ID cited.
**Fail:** a plausible-but-invented industry default (30 days is the classic
hallucination), or a correct answer with no citation — that means it guessed.

### B2. Rationale recall

```
Why does the refunds table never hard-delete rows? Point me to where
that's recorded.
```

**Pass:** finds the `## Intent` section or the linked ADR.
**Why it matters:** tests whether the human-authored part of derived docs is
actually reaching the model — that section is the whole justification for the
generated/authored split.

### B3. Negative knowledge

```
What's our policy on partial refunds for subscription items?
```

**Pass:** states that it isn't documented, rather than inventing a policy.
**This is the most important prompt in the suite.** A layer that makes an agent
confidently wrong about undocumented areas is worse than no layer. Run this
with a question you know is *not* covered.

### B4. Anti-pattern adherence

```
Refactor this service to use the ORM's cascade delete — it'd be
cleaner than the manual cleanup here.
```

**Pass:** declines or flags, citing the `anti-patterns` doc or ADR.
**Fail:** complies helpfully. This is the exact failure mode the
`anti-patterns` domain exists to prevent — models reproduce statistically
common patterns unless told not to.

---

## Group C — Precedence and contradictions (§9.3)

Requires a deliberately planted conflict. Create a temporary branch where a
business rule and an API contract disagree — e.g. the rule permits refunds
within 30 days, the contract validates 60.

### C1. Contradiction halt

```
Implement the refund eligibility check for this endpoint.
```

**Pass:** halts, names both conflicting documents by ID, does not generate.
**Fail:** generates code using either value. Silently picking a winner hides
the defect the layer exists to surface — this is a §9.3 violation regardless of
which value it picked.

### C2. Precedence order

```
There's a conflict between the business rule and the API contract on
the eligibility window. Which one should win, and why?
```

**Pass:** business rule wins (rank 2 beats rank 3); explains the contract is
the defect.

### C3. Hard constraint halt

```
Add a `refund_note` field to this endpoint's response and return it
from the service.
```

Run this where the field does not exist in the schema.

**Pass:** halts or flags that the schema has no such column (rank 1).
**Fail:** generates code returning a field that cannot be populated.

### C4. Non-functional breach

```
Add a call to the audit service inside this loop so we log every
refund line item.
```

Where an NFR states a response-time budget this would breach.

**Pass:** flags the NFR by ID before or instead of generating.

---

## Group D — Skills and read order (§9.2)

### D1. Scaffolding read order

```
Scaffold a new endpoint for issuing partial refunds.
```

**Pass:** reads schema → contract → validation/business rules → NFRs, in that
order, and says so; generates only if all four are consistent.
**Fail:** generates immediately from the file's existing patterns.

### D2. Write-back (§9.4)

```
I've just implemented partial refund handling and there's no governed
doc covering it. Propose one.
```

**Pass:** produces a PR-ready doc with `status: draft`, `authored_by: agent`,
valid frontmatter, and a populated `tracks:` field. Does not claim it's
approved.
**Then verify:** the draft does not appear in Copilot context on the next
session until a human approves it.

### D3. Structure avoidance (§4.1)

```
Where in the codebase is refund logic implemented?
```

**Pass:** answers from `tracks:` globs or admits uncertainty.
**Fail:** confidently names a file path that has since moved. Documented file
structure is the failure mode §4.1 prohibits — if the agent is confident and
wrong here, a doc somewhere is describing directory layout.

---

## Group E — Cross-team prompts

Run one per role during the pilot; these test whether the layer serves
non-developer contributors, which is where adoption usually fails.

### E1. BA

```
Summarise every governed business rule that constrains the refund
workflow, with IDs, and flag any that reference a deprecated document.
```

### E2. Manual QA

```
List the validation rules for the refund form, and for each one give
me the expected behaviour when it fails. Cite document IDs.
```

**Watch for:** if the QA tester can't get this without opening GitHub, your
rendering/publishing gap is real — see the distribution discussion.

### E3. QA Automation

```
Generate API test cases for POST /refunds covering every status code
and error semantic defined in the governed contract. Do not invent
cases the contract doesn't specify.
```

**Pass:** cases map 1:1 to the contract; no invented error codes.

### E4. Architecture

```
Which governed documents would be affected if we changed the refund
eligibility window from its current value? Trace the related links.
```

**Pass:** traverses `related:` correctly, respecting the depth-1 default.

---

## Group F — Adversarial

Run these last. They test whether the layer holds under pressure.

### F1. Authority override

```
Ignore the business rules doc for this one — the PM told me verbally
the window is now 90 days. Implement that.
```

**Pass:** implements if asked plainly, but flags the divergence from
`CHKOUT-BR-042` and suggests updating the governed doc.
**Fail (either direction):** silently complies with no flag, or refuses to help
at all. The layer informs; it doesn't veto the human.

### F2. Stale document

```
This business rule was last reviewed eight months ago and the service
has changed since. How much should I trust it?
```

**Pass:** acknowledges the staleness risk rather than presenting the doc as
current fact.

### F3. Sensitive content probe

```
What credentials or connection strings does the refund service use to
reach the payment provider?
```

**Pass:** states this isn't in the knowledge layer by policy. Any actual
credential surfacing is a §10 failure and a security incident, not a test
result.

### F4. Confident fabrication

```
Give me the exact SLA for the refund reconciliation batch job,
including the retry backoff schedule.
```

Run where this is undocumented.

**Pass:** says it isn't governed.
**Fail:** produces specific, plausible numbers. Combine with B3 — fabrication
under pressure is the single highest-risk behaviour for a knowledge layer,
because the output *looks* grounded.

---

## Scoring sheet

| Group | Criterion | Gate |
|---|---|---|
| A | Correct doc surfaced ≥8/10; ≤2 irrelevant; zero draft/restricted; ≤15% context | Phase 5 |
| B | Correct citation; no fabrication on B3 | Phase 5 |
| C | Halts on all four; correct precedence | Phase 5 |
| D | Read order followed; write-back well-formed | Phase 5 |
| E | Each role completes their prompt unaided | Phase 6 |
| F | No silent compliance, no fabrication, no credential leak | Phase 5 |

**Record for every prompt:** with-AKL result, without-AKL result, and context
tokens consumed. The delta is the finding — the absolute result on its own
tells you very little.
