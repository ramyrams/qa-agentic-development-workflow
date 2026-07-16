# Side-by-Side Comparisons: GitHub Copilot Customization Files
### Companion to the Copilot Customization Framework — for the QA automation team

`README.md` vs `copilot-instructions.md` vs custom `*.instructions.md` (the three "repo documentation" files people conflate)

These three get conflated because all describe "how the repo works." They differ in **audience, loading behavior, and scope**.

### B.1 Core Identity

| Dimension | `README.md` | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` |
|---|---|---|---|
| **Primary audience** | **Humans** — new team members, stakeholders, users of the repo | **The AI** — every Copilot request in the repo | **The AI** — requests touching specific paths |
| **Is it read by Copilot?** | Only if the model/agent happens to open it while exploring (or you point at it) — **not injected automatically as an instruction** | **Yes — automatically injected into every request** | **Yes — automatically injected when the `applyTo` glob matches** the files in play |
| **Is it read by humans?** | Yes — its whole purpose; rendered on the repo homepage | Rarely after authoring (should be reviewed like code) | Rarely after authoring |
| **Location** | Repo root (also per-folder READMEs) | Exactly `.github/copilot-instructions.md` — one per repo | `.github/instructions/`, many files, each with its own glob |
| **Frontmatter** | None (plain Markdown) | None needed | `applyTo:` glob (required for scoping), optional `description:` |
| **Quantity** | Typically one root README (+ optional folder READMEs) | **Exactly one** | **As many as you need** — this is the scoping mechanism |

### B.2 Content & Voice

| Dimension | `README.md` | `copilot-instructions.md` | `*.instructions.md` |
|---|---|---|---|
| **Content type** | Orientation: what this repo is, why it exists, how to get started, how to contribute, badges, links, screenshots | Operative rules: architecture map, universal conventions, build/test/lint commands, hard "never" rules | Narrow operative rules for one file family (e.g., "in `cypress/e2e/**`: one behavior per `it`, intercept all XHR…") |
| **Voice / framing** | Explanatory prose — persuade, orient, welcome | Directive, imperative, terse — every line is a rule the model should obey | Same directive voice, narrower scope |
| **Rationale & backstory** | Belongs here — humans want the *why* | Mostly omit — rationale costs tokens on every request; keep only where it prevents misapplication | Omit; link a skill or doc if depth is needed |
| **Length economics** | Length is nearly free — nobody pays a per-request cost | **Every line taxes every single request.** Target ~50–100 lines | Short; cost is paid only on matching requests |
| **Duplication guidance** | May *summarize* conventions for humans and link out | **Source of truth** for AI-facing universal rules | Source of truth for AI-facing path rules |
| **QA example content** | "This repo contains our e2e and API test suites for the customer portal. Prereqs: Node 20. Quick start: `npm i && npm run cy:open`. See CONTRIBUTING for the spec review checklist." | "Selectors: `data-cy` only. No `cy.wait(ms)`. Specs are order-independent. API tests clean up their data. Run `npm run lint` before PRs." | In `cypress-e2e.instructions.md`: "describe-per-feature, it-per-behavior; intercept+alias all network the test depends on; assert on aliases, not time." |

### B.3 Behavior, Precedence & Maintenance

| Dimension | `README.md` | `copilot-instructions.md` | `*.instructions.md` |
|---|---|---|---|
| **Scope of automatic effect** | None (documentation only) | Entire repo, every request | Only requests whose working files match the glob |
| **How multiple sources combine** | N/A | Combines **additively** with any matching path-specific instructions (and org/personal instructions where configured) — there is no strict override hierarchy, so **conflicts confuse the model rather than resolve cleanly**. Keep the layers non-contradictory | Same — additive alongside repo-wide instructions; a path file should *refine*, never contradict, the repo-wide file |
| **Failure mode when stale** | Humans get lost or run wrong commands; annoying but visible | AI silently generates against outdated conventions **everywhere** — the most damaging staleness of the three | AI misbehaves within one file family |
| **Ownership model** | Docs owner / whole team | Named maintainer + PR review, treated as code | Same, often the sub-area's owner (e.g., API test lead owns `api-tests.instructions.md`) |
| **When to update** | Onboarding friction, new setup steps | Any change to conventions, commands, or architecture the AI must respect | Changes local to that file family |

### B.4 The Relationship Between the Three (how to think about it)

1. **README.md orients humans; instructions files govern the AI.** Writing "for Copilot" content into the README doesn't reliably reach the model, and writing human onboarding prose into `copilot-instructions.md` wastes always-on context on material the AI doesn't need as rules.
2. **`copilot-instructions.md` is the constitution; `*.instructions.md` files are local bylaws.** The repo-wide file carries the small set of universal, non-negotiable rules; path files carry everything that is only true for one part of the tree. If a rule starts with "in the e2e specs…", it does not belong in the repo-wide file.
3. **They are additive, not overriding.** All matching instruction layers are injected together, so a contradiction between the repo-wide file and a path file doesn't "resolve" — it produces inconsistent behavior. The discipline: universal rules live in exactly one place; path files only add, narrow, or specialize.
4. **A practical authoring pipeline:** mine the README + CONTRIBUTING + your PR review comments for the rules you keep repeating → distill the universal ones into `copilot-instructions.md` → push everything path-conditional into `*.instructions.md` files → leave the human narrative, setup story, and rationale in the README, with the README linking to the instructions files so humans know they exist.
5. **Litmus test per line:** *"Is this a rule the AI must apply while generating?"* → instructions (repo-wide if universal, path file if conditional). *"Is this orientation, rationale, or setup narrative for a person?"* → README.

---

*Companion to: `copilot-customization-framework-qa.md` · Verify surface-support details against GitHub's customization cheat sheet on major Copilot releases.*
