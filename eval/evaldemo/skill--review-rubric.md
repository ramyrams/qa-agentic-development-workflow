# Cypress/JS Test Review Rubric
### Judgment-based criteria — apply these AFTER the pre-scan script's mechanical checks

## Blocking (policy violations — from .github/instructions/)

**Test independence.** Does the test rely on execution order or leftover state from another test? A test must pass when run alone via `--spec`. Evidence: shared mutable state across `it` blocks, missing `beforeEach` setup, assumptions about a previous test's side effects.

**Assertion strength.** Would this test actually fail if the feature broke? A test that only checks an element exists, without checking its meaningful state/content/behavior, is close to asserting nothing. Ask: "if a developer reverted the fix this test covers, would this test go red?" If the honest answer is no, it's a blocking finding, not a suggestion.

**Negative-path coverage (feature-level, not test-level).** Does the spec file as a whole cover at least one failure/invalid-input case for the feature under test, not just the happy path? Missing entirely is blocking; present but weak is a suggestion.

**Data handling.** Is test data from a fixture or a data-seeding helper, never invented/hardcoded inline in a way that duplicates what a fixture should own? Check for magic strings that look like they should be shared fixture data.

## Suggestions (quality — not a stated policy violation)

**Naming clarity.** Does the `it(...)` description read as user-visible behavior ("shows an error for an invalid discount code") rather than implementation detail ("calls applyPromo and checks response")?

**Structural conventions.** `describe` per feature, `context` per state, `it` per behavior — is the file organized this way? A flat pile of unrelated `it` blocks under one `describe` is a suggestion, not a blocker, unless it actively causes an independence violation (which would be blocking).

**Page-object usage.** Is element access going through the page object layer rather than raw `cy.get()` calls scattered through the spec? (Note: this is separate from the pre-scan's selector-policy check, which only checks *what kind* of selector is used, not *where* the call lives.)

**Redundant/duplicate coverage.** Does this test cover ground an existing test already covers, with no new signal? Flag for consolidation, don't block on it.

**Setup complexity.** Is the `beforeEach`/setup block doing more than the test needs, suggesting a missing shared helper or a test that's trying to do too much at once?

## How to Weigh a Borderline Case

When a finding could plausibly be either severity: check whether it's traceable to a specific stated rule in `.github/instructions/`. Traceable to a stated rule → blocking. Not traceable, but clearly an improvement → suggestion. When genuinely unsure, say so in the finding rather than silently picking one — a review that hedges visibly is more useful than one that guesses confidently.
