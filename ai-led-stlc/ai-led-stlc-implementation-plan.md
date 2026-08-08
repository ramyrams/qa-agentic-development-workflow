# AI-Led STLC — Implementation Plan
### Program Plan for Delivery: Governance, Staffing, Timeline, Risk

This is the execution plan that sits underneath the blueprint, the phase deep-dives, and the technical design — it answers "how do we actually run this as a program," not "what do we build." Durations below are planning estimates (t-shirt sized), to be refined once Phase 1 gives you real velocity data — they're a starting point for scheduling conversations, not commitments.

---

## 1. Program Objective

Deliver AI-assisted capability across all ten STLC stages, in six risk-sequenced phases, with a mandatory human-review gate at every stage, measurable via the metrics framework already defined, and cleared through AI governance intake before each phase's build begins.

## 2. Governance Structure

| Role | Who | Responsibility |
|---|---|---|
| **Program Sponsor** | You (QA Manager) | Overall accountability, phase go/no-go decisions, leadership reporting |
| **Steward** (new competency-ladder rung) | You, initially | Eval policy compliance, traceability enforcement, governance liaison |
| **AI Governance Team** | Enterprise governance function | Data boundary review, connector approval, per-phase intake sign-off |
| **Automation Engineering Lead** | TBD from your team | Phase 1, 2, 3, 6 technical delivery |
| **Functional Testing Lead** | TBD from your team | Phase 4, 5 pilot coordination, tester change management |
| **ADO/DevOps Admin** | Cross-team | Service principal provisioning, connector configuration, field-mapping support |
| **Business Analyst/Product Owner Sponsor** | Cross-team | Phase 5 collaboration on Definition-of-Ready and requirement-analysis rollout |

**Decision rights**: phase go/no-go sits with the Program Sponsor, informed by eval results and pilot metrics — not a committee vote, to keep the initiative moving, but governance sign-off is a hard gate for any phase that writes to ADO (Phases 3+), non-negotiable regardless of internal readiness.

## 3. RACI by Phase

| Phase | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| 1 — Execution & Reporting | Automation Eng. Lead | Program Sponsor | — | Full QA team |
| 2 — API Script Gen | Automation Eng. Lead | Program Sponsor | API service owners | Full QA team |
| 3 — ADO Defect Drafting | Automation Eng. Lead | Program Sponsor | AI Governance, ADO Admin | Automation team |
| 4 — Test Case Design | Functional Testing Lead | Program Sponsor | AI Governance, one pilot tester | Functional testing team |
| 5 — Requirement Analysis & Planning | Functional Testing Lead + Program Sponsor | Program Sponsor | AI Governance, BA/PO Sponsor | Cross-functional (BA/PO org) |
| 6 — Regression Optimization | Automation Eng. Lead | Program Sponsor | AI Governance | Full QA team, release management |

---

## 4. Timeline & Milestones (Estimated)

| Phase | Est. Duration | Key Milestone | Gate to Next Phase |
|---|---|---|---|
| Governance groundwork (parallel, pre-Phase 1) | 2–4 weeks | ADO connector governance intake submitted | Connector approved in principle (blocks Phase 3+, doesn't block Phase 1–2) |
| Phase 1 | 4–6 weeks | Healer + Allure automation live, one full weekly cycle run end-to-end | Ledger live, eval suites passing, metrics baseline captured |
| Phase 2 | 4–6 weeks | Full plan→explore→script→test cycle merged for one real API | Read-only pilot trusted, results flowing into Phase 1 ledger |
| Phase 3 | 5–7 weeks (includes governance sign-off lead time) | First AI-drafted bug filed live in ADO | Duplicate-check and draft-quality rates within agreed threshold |
| Phase 4 | 6–8 weeks (new surface: Copilot Studio build time) | First AI-drafted test case set approved and filed by a pilot tester | Case-generate quality stable, functional team onboarded |
| Phase 5 | 6–10 weeks (requires DoR formalization if not already documented) | One release planned end-to-end with AI-assisted scope | Plan-draft acceptance rate stable across multiple cycles |
| Phase 6 | 6–8 weeks + shadow-mode window | Shadow-mode results reviewed and approved by QA leadership | Zero missed-regression incidents in shadow mode before live skipping enabled |

**Total indicative runway**: roughly 12–15 months for all six phases sequentially, though Phases 1–2 and elements of governance groundwork run in parallel, and later phases can compress if a phase's eval/pilot results come in faster than estimated. Treat this as a rolling-wave plan — re-estimate the next phase's window once the current one's actuals are in, don't lock the whole calendar upfront.

## 5. Workstream Plan (Per Phase, Consistent Pattern)

Every phase follows the same execution pattern, which itself is worth stating explicitly to the team so "how we work" doesn't need to be re-explained each time:

1. **Scope & config** — confirm skill list, config files (thresholds, field mappings), and governance status
2. **Build** — skills + eval suites, per the technical design
3. **Eval validation** — pass rate against baseline before any pilot use
4. **Pilot** — one engineer/tester, tight review loop, defined cycle count
5. **Metrics review** — pilot data against the phase's defined acceptance bar
6. **Team-wide rollout** — only after metrics review passes
7. **Steady-state monitoring** — ongoing eval re-validation, ledger health checks, metrics tracked per Section 7 of the metrics framework

## 6. Dependencies & Prerequisites

| Dependency | Needed By | Owner | Status Check |
|---|---|---|---|
| ADO connector (MCP/REST) governance approval | Phase 3 | AI Governance + ADO Admin | Start intake during Phase 1 |
| Service principal, least-privilege write scope | Phase 3 | ADO Admin | Confirm scope before any write-capable code is built |
| Documented Definition of Ready | Phase 5 | Program Sponsor + BA/PO Sponsor | Formalize during Phase 4 if not already in place |
| Copilot Studio licensing/environment for functional testers | Phase 4 | IT/Platform team | Confirm during Phase 3 |
| Code-ownership or component-mapping file (for change-impact) | Phase 6 | Automation Eng. Lead | Can start as a lightweight tag-based version early; doesn't block earlier phases |
| Historical ADO defect data access (for defect-history-analyze) | Phase 5 | ADO Admin | Confirm query access and data completeness |

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ADO connector governance approval delays Phase 3+ | Medium | High | Start intake in parallel with Phase 1, not after Phase 2 completes |
| Eval suites pass in testing but don't reflect real-world data | Medium | High | Seed eval sets with real historical data wherever possible, not synthetic-only |
| Functional testers resist AI-drafted test cases (trust/adoption) | Medium | Medium | Pilot with most bought-in tester first; frame as draft assistant, not replacement (Phase 4 change management) |
| Duplicate-check floods backlog or suppresses real bugs | Medium | Medium | Shadow/pilot period with human-reviewed candidates only, never auto-suppress |
| Regression subset-recommend misses a real regression | Low (with shadow mode) | High | Mandatory shadow-mode window before live skipping; permanent full-suite safety net cadence |
| Requirement/defect history data too sparse for new modules | Medium | Medium | Explicit sparse-data fallback defaults to full coverage, not silently thin coverage |
| Sensitive data exposure via model context (logs, requirements, defect history) | Low | High | Per-phase governance data-boundary review, not a one-time approval |
| Scope creep — team tries to skip phases or shortcut review gates under delivery pressure | Medium | High | Program Sponsor holds the gate; no phase advances without its defined exit criteria met |

## 8. Communication & Reporting Cadence

- **Weekly**: internal team standup covering current phase's build/pilot status
- **Bi-weekly or per-milestone**: Program Sponsor updates AI Governance Team on phase status and upcoming intake needs
- **Per phase completion**: leadership update using the metrics framework — actual pilot data, not projections, per the leadership briefing's Section 10 recommendation
- **Ongoing**: metrics dashboard (or simple tracked spreadsheet initially) covering the Section 7 metrics from the leadership briefing, updated as each phase generates data

## 9. Change Management & Training

- Extend the existing competency ladder (User/Author/Architect/Steward) to cover every phase's skill set as it ships, not just automation-team primitives
- Functional testing team gets dedicated onboarding material for the Copilot Studio interface ahead of Phase 4 — don't reuse VS Code-oriented training material as-is
- Publish the "why this order" STLC-to-phase mapping (from the leadership briefing) internally too — the same confusion risk applies to your own team, not just leadership
- Failure ledger and case-quality ledger reviews become a standing agenda item once live, so misclassifications get caught and corrected as a routine practice, not an afterthought

## 10. Success Criteria (Program-Level)

The program is on track if, at each phase gate:
- Eval suites for that phase's skills are passing and re-validated on every update
- Pilot metrics meet the phase's defined acceptance bar (documented in that phase's deep-dive)
- Governance sign-off is in hand for any ADO-writing phase before go-live
- No unresolved high-impact risk from Section 7 is open against the phase being closed

The program is at risk if any phase advances to team-wide rollout without its pilot metrics reviewed, or if a governance gate is bypassed under schedule pressure — these are the two failure modes most likely to undermine trust in the initiative, more than any single technical miss.
