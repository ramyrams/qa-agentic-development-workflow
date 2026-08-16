# AKL Prompt Playbook — By Role

Everyday prompts for using the Application Knowledge Layer in VS Code /
Copilot. Unlike the test suite (`akl-test-prompts.md`), these are not
pass/fail checks — they're the real, recurring needs each role has, written so
you can paste and adapt them.

**How to read each entry:** *the situation* → the prompt → what good looks
like.

**Two habits that make all of these work better:**
1. Ask it to cite document IDs. If it can't cite, it guessed.
2. When it tells you something isn't governed, that's a finding — file a draft
   doc rather than moving on.

Examples below use the running `refund` example (`CHKOUT-BR-042`,
`CHKOUT-API-refunds`, `CHKOUT-DB-refunds`). Substitute your own IDs.

---

## 1. Business Analyst

### BA-1 — Before writing a new rule, check what already exists
*You're about to spec partial refunds and don't want to contradict something.*

```
I'm about to write a new business rule for partial refunds. List every
existing governed rule that touches refunds, with IDs and a one-line
summary each, and flag any that would conflict with allowing partial
refunds.
```

**Good:** a short list with IDs, plus an explicit conflict callout. This is the
single highest-value BA prompt — it prevents the contradictory-rules problem
before it reaches development.

### BA-2 — Impact analysis before a change
*A stakeholder wants the eligibility window changed.*

```
If we changed the refund eligibility window, which governed documents
would be affected? Trace the related links and group them by owning
team so I know who to talk to.
```

**Good:** names the contract, schema, validation rules and NFRs downstream, and
tells you it's Backend + QA you need in the room.

### BA-3 — Turn a requirement into a governed doc
*You've just agreed a rule in refinement.*

```
Draft a business-rule document for this requirement using our authored
domain template: refunds are not permitted once an order has shipped,
except for damaged goods, which need manager approval. Fill in
frontmatter, description, constraints, and rationale. Leave the ID for
me to assign.
```

**Good:** valid frontmatter, `status: draft`, a rationale section that captures
*why* — not just what.

### BA-4 — Find the gaps in your own domain
*You want to know where documentation is thin before an audit.*

```
For the refund workflow, which steps have a governed business rule
covering them and which don't? Show me the gaps as a list.
```

### BA-5 — Reconcile spec against reality
*You suspect the built behaviour drifted from the rule.*

```
Read CHKOUT-BR-042 and then the validation rules and API contract that
reference it. Do they all agree on the eligibility window? Show me any
discrepancy.
```

**Good:** either confirms alignment or names the exact disagreement. This is
how a BA catches drift without reading code.

### BA-6 — Onboarding a new team member
```
Explain the refund domain to someone joining the team this week: the
key business rules, the workflow, and the two or three things that
most surprise newcomers. Cite document IDs so they can read further.
```

---

## 2. API Developer

### API-1 — Build against the contract, not the caller
*You're implementing a new endpoint.*

```
Scaffold the POST /refunds/partial endpoint. Read the schema first,
then the API contract, then the validation and business rules, then
the NFRs. If any of them conflict, stop and tell me instead of
generating.
```

**Good:** it states what it read and generates only on a clean read. This is
the §9.2 read order in daily use.

### API-2 — Check a change won't break consumers
```
I want to make the `reason` field required on POST /refunds. Which
governed documents reference this endpoint, and does anything indicate
existing consumers depend on it being optional?
```

### API-3 — Error handling that matches the catalog
```
Add error handling to this handler. Use only the error codes defined
in our governed error catalog — don't invent new ones. If the case I
need isn't covered, say so.
```

**Good:** reuses existing codes, and flags the gap rather than inventing
`REFUND_ERR_017`.

### API-4 — Auth requirements without guessing
```
What authorization does POST /refunds require according to the
governed permissions doc? Show me the roles and any conditions, then
verify this implementation matches.
```

**Good:** this is one of the highest-hallucination areas for agents — the doc
should stop it guessing at role names.

### API-5 — Contract-first change
*Reminder that contracts are derived (§4).*

```
I need to add a `partial_amount` field to the refund response. Walk me
through the correct order: what do I change first, and what will
regenerate automatically versus what I have to author by hand?
```

**Good:** spec/migration first, doc regenerates, only `## Intent` is
hand-written. If your team gets this wrong, drift starts here.

### API-6 — Non-functional budget check
```
This endpoint now makes two additional downstream calls. What response
time budget does the governed NFR set for it, and does this design
risk breaching it?
```

---

## 3. UI Developer

### UI-1 — Understand a page before changing it
```
What is the governed purpose of this page, which elements does it use,
and which business rules constrain what the user can do here? Cite IDs.
```

### UI-2 — Reuse instead of rebuilding
*The most common UI knowledge failure.*

```
I need a currency input with validation for the refund amount field.
Is there an existing governed element that does this? If yes, show me
its behaviour contract. Only suggest building new if nothing fits.
```

**Good:** finds the existing element. This prompt alone justifies the
`elements` domain — duplicate component creation is expensive and invisible
until it isn't.

### UI-3 — Client-side validation matching the rules
```
Implement client-side validation for this refund form. Base every rule
on the governed validation-rules docs — list which rule each check
implements, and flag any check I'd need that isn't governed.
```

**Good:** a mapping of check → rule ID. Prevents the classic mismatch where
the UI is stricter or looser than the server.

### UI-4 — Error and empty states
```
What states does this page need to handle according to its governed
doc — loading, error, empty, disabled? For error states, what messages
does the error catalog specify?
```

### UI-5 — Accessibility and localization constraints
```
What accessibility standard and localization requirements apply here
per our governed non-functional docs? Check this component against
them.
```

### UI-6 — Navigation impact
```
If I remove the refund entry point from the order detail page, which
governed workflows break? Trace it.
```

---

## 4. Database Developer

### DB-1 — Understand the intent before altering
*The single most important DB prompt.*

```
Before I alter the refunds table: what does the Intent section of its
governed doc say about why the current constraints exist? I don't want
to undo a deliberate decision.
```

**Good:** surfaces the "never hard-delete, see DEC-004" style rationale that
would otherwise be lost.

### DB-2 — Migration impact across domains
```
I'm adding a `partial_amount` column to refunds. Which governed API
contracts, business rules, and validation rules reference this table,
and would any of them need updating?
```

### DB-3 — Confirm what regenerates
```
After I merge this migration, what happens to the governed db-schema
doc? What will I still need to write by hand?
```

**Good:** the table regenerates; only `## Intent` needs a human. Worth running
once per developer so the derived model is understood, not assumed.

### DB-4 — PII and data lifecycle
```
Which columns in the refunds and orders tables are flagged as PII or
sensitive in the governed docs, and what retention rules apply to them?
```

### DB-5 — Constraint archaeology
*Legacy constraint nobody remembers.*

```
There's a check constraint on refund status transitions that looks
overly restrictive. Is it explained in any governed doc or linked ADR,
or is it undocumented?
```

**Good:** either finds the rationale or tells you plainly it's undocumented —
which is your cue to file a doc before changing anything.

### DB-6 — Proposed change against the rules
```
The business wants refunds retained for seven years. Does that
conflict with anything in our governed data-lifecycle or non-functional
docs?
```

---

## 5. Manual / Functional Tester

### QA-1 — What should this actually do?
*Replaces "let me go ask the BA."*

```
I'm testing the refund form. What are the governed business rules and
validation rules that define correct behaviour here? Give me each one
with its ID and the expected outcome when it fails.
```

### QA-2 — Bug or intended behaviour?
*The daily question.*

```
The form lets me submit a refund 45 days after purchase. Is that
correct per the governed rules, or is it a defect? Cite the rule.
```

**Good:** a definitive answer with a citation you can paste into the defect
ticket. This is the prompt that saves QA the most time.

### QA-3 — Build a test checklist from the rules
```
Generate a functional test checklist for the refund workflow, with
each test case traced to the governed rule or validation rule it
verifies. Don't include cases that aren't backed by a governed doc —
list those separately as coverage gaps.
```

**Good:** two lists — traced cases, and gaps. The gaps list is genuinely
valuable to the BA.

### QA-4 — Edge cases from the state machine
```
According to the governed entity-lifecycle doc, what are the valid
refund status transitions? Which invalid transitions should I attempt
as negative tests?
```

### QA-5 — Expected error messages
```
What user-facing messages does the governed error catalog specify for
refund failures? I want to verify the exact wording, not approximate.
```

### QA-6 — Regression scope after a change
```
The eligibility window changed from 30 to 45 days. Which governed
documents changed, and what should I regression test as a result?
```

---

## 6. QA Automation Engineer

### AUT-1 — Generate tests from the contract, not the UI
```
Generate API test cases for POST /refunds from the governed contract.
Cover every status code and error semantic it defines. Do not invent
cases the contract doesn't specify — list anything you think is
missing separately.
```

**Good:** 1:1 mapping to the contract, plus a gap list. Grounding here is the
whole point — scraped-from-UI expectations are what make suites brittle.

### AUT-2 — Validation-driven test data
```
Based on the governed validation rules for the refund form, generate
boundary test data: valid, just-invalid, and clearly-invalid values for
each field. Cite the rule each dataset targets.
```

### AUT-3 — Diagnose a failure against the rules
*A test just went red.*

```
This test asserts refunds are rejected after 30 days and it's now
failing. Check the governed business rule — has the rule changed, or is
this a genuine regression?
```

**Good:** distinguishes "the world changed" from "the code broke." This is the
grounding that makes healing agents viable rather than guesswork.

### AUT-4 — Find brittle assumptions in an existing suite
```
Review this spec file. Which assertions encode behaviour that isn't
backed by a governed rule or contract? Those are the ones likely to
break on the next change.
```

**Good:** surfaces the assumed-not-governed assertions — the usual source of
flakiness.

### AUT-5 — Async/event coverage
```
What events does the refund flow publish per the governed events doc?
Generate test cases verifying each is emitted with the correct schema.
```

### AUT-6 — Keep tests aligned after a rule change
```
CHKOUT-BR-042 changed this sprint. Which of our existing tests
reference behaviour governed by it, and which need updating?
```

---

## 7. Architect

### ARC-1 — Blast radius
```
We're considering splitting the refund service. Which governed
documents, domains, and owning teams would be affected? Group by team.
```

### ARC-2 — Check a proposal against existing decisions
```
Before I write an ADR proposing event-driven refund processing: which
existing governed decisions or NFRs would this contradict or supersede?
```

### ARC-3 — Non-functional coverage audit
```
Which parts of the refund domain have governed non-functional
requirements and which don't? I'm looking for unstated performance and
security expectations.
```

### ARC-4 — Record an anti-pattern
```
Draft an anti-patterns doc: we deliberately don't use the ORM's
cascade delete on refunds because of the audit retention requirement.
Link it to the relevant decision and schema docs.
```

**Good:** this is the cheapest high-value doc an architect can write — it stops
a recurring class of well-intentioned refactors.

### ARC-5 — Integration failure modes
```
What third-party integrations does the refund flow depend on per the
governed integrations docs, and what failure modes and retry semantics
are documented for each?
```

### ARC-6 — Deprecation trace
```
Which governed documents are marked deprecated but still referenced by
approved documents? That's my cleanup list.
```

---

## 8. Tech / Delivery Manager

### MGR-1 — Coverage snapshot
```
For the refund pilot area: how many governed documents exist per
domain, how many are draft versus approved, and which are flagged
stale?
```

### MGR-2 — Onboarding readiness
```
If a new developer joined the refund team tomorrow, what could they
learn from the governed docs alone, and what would still require a
conversation with someone?
```

**Good:** an honest gap list. This is a better adoption metric than doc count.

### MGR-3 — Ownership check
```
List the governed documents in the refund area with no clear owner, a
missing fallback owner, or an owner who's left the team.
```

### MGR-4 — Staleness by team
```
Which governed docs are past their review SLA or flagged by churn
detection, grouped by owning team? I want to know where to apply
pressure.
```

### MGR-5 — Change readiness
```
We're planning to change refund eligibility next quarter. Based on the
governed docs, which teams need to be involved and roughly what's the
documentation impact?
```

---

## Quick reference card

Worth pinning for the team — one prompt per role that delivers most of the
value:

| Role | The one prompt |
|---|---|
| BA | "List every existing governed rule that touches X, and flag conflicts with what I'm about to write." |
| API Dev | "Read schema → contract → rules → NFRs. If they conflict, stop and tell me." |
| UI Dev | "Is there an existing governed element that does this? Only suggest building new if nothing fits." |
| DB Dev | "What does the Intent section say about why these constraints exist?" |
| Tester | "Is this behaviour correct per the governed rules, or is it a defect? Cite the rule." |
| Automation | "Generate tests from the governed contract. Don't invent cases it doesn't specify." |
| Architect | "Which existing governed decisions would this proposal contradict?" |
| Manager | "What's draft vs. approved vs. stale, by team?" |
