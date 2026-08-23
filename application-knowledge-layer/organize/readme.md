Centralizing this well comes down to three separate problems — where it lives, how people actually get the current version, and how to browse it without needing git — so let me take them in order.

## 1. One canonical repo, not per-team copies

Create a single dedicated repo for this knowledge layer — not folders scattered inside each application's own repo. Given the design spans multiple services (UI, API, DB, business rules) that don't all live in one codebase, a standalone repo is the only structure that avoids the same page/endpoint/table ending up duplicated or drifting across several places.

- Platform: Azure DevOps Repos or GitHub Enterprise (whichever your org already standardizes on) — keeps it inside the same governance/access-control model as your other code.
- `main` branch = the single source of truth. Nothing else claims to be current.
- Branch protection: required PR review + the CI schema/referential-integrity checks from earlier before anything merges to `main`. This is what makes "latest information" actually mean something — a merged PR has passed validation, not just been typed up.

## 2. How developers/QA/architects actually get "latest"

For the audience using this inside VS Code with Copilot (your primary consumers), the mechanism is simply: clone the central repo, `git pull` before a session. The gap worth closing is that nothing currently stops someone from working off a week-old local checkout without realizing it. Two lightweight fixes:

- Add a check to the start of every skill prompt (`capture-page`, `query-knowledge-base`, etc.): "confirm the local repo is up to date with `main` before proceeding, and warn me if not."
- Or: a scheduled CI job that tags releases of the knowledge repo, so a stale local copy is visibly behind a version number, not just silently old.

## 3. A browsable, always-current view for people who don't want to clone a repo

Not everyone doing app dev work wants to `git clone` a YAML repo just to look something up. Generate a static docs site (MkDocs, Docusaurus, or similar) from the repo's content, auto-rebuilt and republished on every merge to `main` via CI, hosted internally. This gives anyone a searchable, current view of pages, journeys, API contracts, and rules — no VS Code, no git — while the repo stays the actual source of truth underneath it. This is also the natural feed for the WorkIQ connector from the last answer, so both audiences (technical, via repo; broader, via WorkIQ/Teams) draw from the same generated output rather than two divergent copies.

## 4. Split access for sensitive content

The exposure-surface index and any security/role-permission records shouldn't have the same access as page records and API contracts. Put them in a separate folder (or separate repo, if your access-control tooling works better at repo granularity) with restricted permissions, so "centralized for everyone" doesn't accidentally mean "everyone can see which tables hold PII." This is worth routing through your own governance review rather than deciding informally.

## 5. Keep the auto-generated layers actually fresh

The DDL-imported DB records and the OpenAPI-imported API baseline are the two most likely to silently rot, since nothing forces someone to re-run those imports. Put both on a scheduled CI pipeline (weekly, or tied to your release cadence) that re-imports and opens a PR if anything changed, rather than relying on someone remembering to do it manually — the same discipline as the reconciliation step from the API/DB design, just running on a timer instead of only after a UI capture session.

**Net structure:** one central repo (source of truth, PR+CI gated) → auto-published docs site (browsable, always current, feeds WorkIQ) → scheduled re-imports for the laye


s that would otherwise go stale silently. Everyone touches the same underlying data; the access method just differs by role.


Good follow-up — the mechanics differ a lot depending on whether a given service's backend repo is one you can reach, which ties directly back to your earlier "partial access" constraint. Here's how the wiring actually works.

## 1. Repos stay separate — the knowledge repo doesn't merge into or replace any dev repo

Each application team keeps their own repo(s) exactly as-is. The knowledge repo sits alongside them, not inside them. What connects them isn't a submodule or shared codebase — it's a set of reference fields on every knowledge record pointing back to exactly what produced it:

```yaml
# added to every page/api/db record:
source_repo: "org/checkout-frontend"
source_commit: "a3f9c1e"
source_path: "src/pages/CheckoutShipping.tsx"
```

This is the actual glue. Without it, "is this record still accurate" is a guess; with it, you can programmatically compare `source_commit` against the app repo's current HEAD for that path.

## 2. Two integration paths, split by the access constraint you already have

| | Backend source reachable | Backend source not reachable |
|---|---|---|
| **Trigger mechanism** | CI webhook on the app repo — fires on merges touching tracked paths (routes, controllers, migrations, OpenAPI spec files) | None available — no CI hook you can install |
| **What runs** | Auto re-run of `reconcile-api-contract` or `code-trace-api`, scoped to the changed paths only | Nothing automated |
| **Staleness detection** | Scheduled job diffs `source_commit` vs. current HEAD for every tracked path; flags drift as "possible staleness," doesn't auto-invalidate (avoids false-positive spam on unrelated commits) | Manual review cadence — e.g., quarterly check-in with whoever owns that service |
| **Who closes the loop** | Mostly automated, human reviews the flagged PR | A person, on a schedule you set |

The reachable-service path is where real integration value shows up — the unreachable path stays a process discipline, not tooling, and that's fine; don't over-invest in trying to automate what you don't have access to.

## 3. UI capture is different — it can't be webhook-triggered

Page capture needs a live browser session and a human supplying purpose/validation/test-data — nothing in a git webhook can do that part. The realistic integration point is a **PR checklist item** in each frontend repo's PR template:

```
- [ ] If this PR adds/changes a page, route, or user-facing form,
      open a companion capture in the knowledge repo (or note why not).
```

Start this as a soft, non-blocking reminder rather than a hard CI gate — forcing every frontend PR to wait on a knowledge-repo capture will get the checklist ignored or the gate disabled within a month. Tighten it into an actual gate later, once people are already doing it voluntarily and you can see how much friction it adds.

## 4. Companion-PR pattern for API/DB changes

For reachable backend repos, the same soft-checklist idea applies to schema/endpoint changes: adding a migration or a new route is the trigger for "open or update the matching knowledge-repo record," surfaced via the webhook from #2 as a suggested PR rather than requiring the developer to remember on their own.

## 5. What this looks like end to end

```
[App repo: PR merged, touches CheckoutShippingController.ts]
        ↓ webhook
[CI job in knowledge repo: re-run code-trace-api scoped to that file]
        ↓
[Opens a PR in knowledge repo: "api/post-checkout-shipping.yaml — 
 tables_touched confirmed unchanged, source_commit updated"]
        ↓
[Human reviews, merges]
        ↓
[Docs site + WorkIQ connector pick up the update automatically]
```

The developer in the app repo never has to open the knowledge repo directly for this class of change — the webhook does it; they just review the resulting PR if one gets opened.

Want me to write the webhook/CI job spec for the reachable-service path, or the PR-template checklist wording for the frontend repos, as concrete next artifacts?

