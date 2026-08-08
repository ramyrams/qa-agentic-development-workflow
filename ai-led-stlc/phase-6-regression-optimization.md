# Phase 6 Deep Dive: Regression Optimization
### AI-Led STLC — Blueprint Phase 6 of 6

Phase 6 is the payoff phase: instead of running the full regression suite every cycle, the agent recommends a risk-based subset using the data accumulated across every prior phase — the failure ledger (Phase 1), case-quality ledger (Phase 4), defect history and complexity signals (Phase 5). It's sequenced last because it's only as good as that accumulated data, which is why every earlier phase explicitly routed its output into shared ledgers rather than isolated logs.

---

## 6.1 Goal
Given a code change or requirement diff for a release, agent recommends which regression tests must run, which can be safely skipped this cycle, and why — reducing regression cycle time without silently losing coverage on what actually matters.

## 6.2 Workflow (end to end)
1. Triggered on a release/build candidate — input is the code diff and/or the set of requirements/work items included in the release
2. **Change-impact skill** maps the diff to affected modules/components/test areas (via code ownership mapping, dependency graph, or linked work items — whichever your org already has structured)
3. **Risk-score skill** combines change-impact with the accumulated signals: historical defect density for affected areas (Phase 5), flaky/environment classification history (Phase 1 ledger — deprioritize tests that mostly fail for non-product reasons), case-quality patterns (Phase 4 ledger — areas where requirements/cases have historically been weak deserve more scrutiny, not less)
4. **Subset-recommend skill** produces the proposed regression set: must-run (high risk/high impact), recommended (moderate), safe-to-skip-this-cycle (low risk, stable history), with the rationale for each tier
5. **Human review gate**: QA lead reviews and adjusts before the subset is what actually runs in the pipeline — this is a coverage decision with the same stakes as Phase 5's test planning, treated with the same rigor
6. Actual run outcome (did a skipped-tier test area turn out to have a bug reported later) logs back into the risk-score skill's training signal — this is the one skill in the whole blueprint that should visibly improve over time as more cycles run

## 6.3 Design Points

**Default to "must-run" when uncertain, not "safe to skip."** The asymmetry matters: a false "safe to skip" that misses a real regression is far more costly than an unnecessary "must-run" that costs some extra CI time. Build this bias explicitly into the risk-score skill's thresholds, don't leave it implicit.

**Periodic full-regression cadence, independent of the optimization.** Even with a trusted subset-recommendation system, run the complete suite on a fixed cadence (e.g., weekly, or every N releases) regardless of what the agent recommends — this catches anything the risk model's blind spots might miss and gives you an ongoing accuracy check on the recommendations themselves.

**Explainability is not optional here.** Every "safe to skip" recommendation needs a stated reason (e.g., "no changes touched this module, zero defects in 6 months, no flaky history") so the human reviewer can sanity-check quickly rather than trust a black box — same principle as the healer agent's confidence explanation in Phase 1, but higher stakes here.

**Start in recommend-only/shadow mode.** For the first several cycles, run the full regression suite as normal *and* generate the subset recommendation in parallel, without actually skipping anything. Compare: did the "safe to skip" tier ever contain a test that would have caught a real issue? Only start actually skipping once you have enough shadow-mode cycles showing the recommendation was safe.

**This is where the whole ledger investment either pays off or reveals gaps.** If Phase 1's failure ledger has inconsistent classification, Phase 5's defect-history data is thin, or Phase 4's case-quality tracking wasn't maintained, this phase will surface that immediately — treat a rocky Phase 6 pilot as a signal to go back and strengthen earlier ledger discipline, not as a reason to distrust the regression-optimization skill itself.

## 6.4 GitHub Copilot Primitives Needed
| Primitive | Purpose |
|---|---|
| **Skill: change-impact** | Map code/requirement diff to affected test areas |
| **Skill: risk-score** | Combine change-impact with historical ledger/defect signals into a risk score per area |
| **Skill: subset-recommend** | Produce tiered (must-run/recommended/skip) regression set with rationale |
| **Instructions** | Risk-tiering thresholds, full-regression cadence policy, uncertainty-defaults-to-must-run rule |
| **Agent** | Orchestrates change-impact → risk-score → subset-recommend, feeds outcome back to ledgers |

## 6.5 Eval Requirements
- **change-impact**: eval against known past diffs with known-correct affected-area mappings — does it correctly identify what a change touches, including indirect/dependency-driven impact, not just direct file changes?
- **risk-score**: eval against historical releases where you know what actually broke — would the risk score have correctly flagged those areas as high-risk in hindsight?
- **subset-recommend**: shadow-mode eval is the real test here (see 6.3) — run it in parallel with full regression for several real cycles and measure whether anything in the "skip" tier would have caught a real issue
- Track this as an ongoing eval, not a one-time gate — risk-score's accuracy should be re-validated periodically as the org's codebase and defect patterns evolve, not just approved once and left alone

## 6.6 Governance/Risk Notes
- Coverage-reduction decisions carry real product-quality risk if the underlying data is wrong — this is the phase most worth being conservative about, given everything upstream feeds into it
- Track "skip tier led to missed defect" as a standing leadership metric indefinitely, not just during pilot — this is the metric that tells you whether to keep trusting the system as the org evolves
- No phase in this blueprint should ever reach full autonomy (auto-skip with no human review) — Phase 6 is the strongest temptation to do so given the maturity by this point, and the one where getting it wrong is most costly

## 6.7 Rollout Steps
1. Build change-impact + eval against historical diffs
2. Build risk-score + eval, using accumulated ledger data from Phases 1, 4, and 5 — this phase cannot start meaningfully until those ledgers have real history, not just schema
3. Build subset-recommend + eval
4. Run in shadow mode (full regression + parallel recommendation, nothing skipped) for a defined number of cycles
5. Review shadow-mode accuracy with QA leadership before enabling any actual skipping
6. Enable skip-tier for low-stakes releases first, expand as trust and data accumulate
7. Maintain the fixed full-regression cadence indefinitely as an ongoing accuracy check, even after full rollout

---

## Phase 6 — Definition of Done
- Change-impact, risk-score, and subset-recommend all have passing eval suites, re-validated periodically (not just once)
- Shadow-mode results reviewed and approved by QA leadership before any live skipping
- Fixed full-regression cadence is in place as a permanent safety net, not a temporary training-wheels measure
- "Skip tier led to missed defect" is tracked as a standing metric

---

## Closing Note: All Six Phases Now Scoped

You now have a complete, sequenced blueprint from requirement intake through regression optimization, each phase building on the data and trust established by the one before it. A few threads worth keeping visible as you execute:

- **The ledgers (Phase 1 failure ledger, Phase 4 case-quality ledger) are the actual backbone of the whole initiative** — Phases 5 and 6 are only as good as that data, so ledger discipline in the early phases isn't a minor implementation detail, it's the foundation.
- **Human review gates get more consequential, not less, as you move through the phases** — Phase 1's healer diff is low-stakes; Phase 6's regression scope decision affects product quality directly. Resist any pressure to loosen the gate as trust builds; if anything, Phase 5-6 deserve more scrutiny than Phase 1-2, not less.
- **Governance/data-boundary conversations should be running ahead of the build, not behind it** — Phase 3 was the first checkpoint for this; each subsequent phase reaches new data sensitivity and new audiences, so treat governance intake as a per-phase gate, not a one-time approval.

If it's useful, I can put together a single consolidated master document (all six phases plus the original overview) as one reference artifact for your team and leadership.
