# Demo Script: Presenting the `csv-analyzer` Skill
### A sequenced set of prompts to demonstrate and explain the skill live, with real expected outputs

**How to use this:** run these in order during your demo. Each one is chosen to teach a specific point about the skill — capability, flexibility, correct scoping, and honest limits — not just to show it working. Every expected output below is grounded in the real, already-verified data from `csvskill-fixture--sales_2025.csv` and `csvskill-fixture--customers.csv`, so you'll know exactly what should appear before you run anything live.

---

## Part 1 — Show the Capability (open strong)

### Prompt 1 — the hero prompt (chart)
> *"I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?"*

**Say while it runs:** "Watch — this is going to call a bundled script, not write analysis code from scratch."
**Expected real output:** a bar chart with three bars — **March ($72,000), July ($89,000), November ($95,000)** — kept in chronological left-to-right order, y-axis labeled "Revenue ($)," title "Top 3 Months by Revenue," dollar values printed above each bar.
**Explain after:** "Notice it didn't just answer in text — it produced a real artifact. That's the skill's bundled script doing deterministic work, not the model reasoning about chart-making each time."

### Prompt 2 — show flexibility (same capability, different parameter)
> *"Actually, show me the top 5 months instead."*

**Why this one:** proves the underlying script isn't hardcoded to "3" — it takes the count as a real parameter. Also a good moment to show a **follow-up** in the same conversation, not just a fresh prompt each time.
**Expected real output:** five bars instead of three, same labeling conventions, correctly re-sorted.

### Prompt 3 — show phrasing robustness (same capability, casual wording)
> *"can you visualize which months made the most money last year"*

**Why this one:** no file path stated, lowercase, no question mark — deliberately the opposite register from Prompt 1. If the skill still fires and produces a correct chart, that's a live demonstration that it isn't brittle to exact phrasing.

---

## Part 2 — Show the Second Capability (breadth, not just one trick)

### Prompt 4 — the hero prompt (data cleanup)
> *"there's a csv in my downloads called customers.csv, some rows have missing emails — can you clean it up and tell me how many were missing?"*

**Say while it runs:** "Different domain entirely now — data quality, not visualization. Same skill, second bundled script."
**Expected real output:** a cleaned CSV where three rows — **Bob Jones, David Lee, Frank Green** — now read `MISSING` in the email column instead of being silently dropped, and a reported count of **3**. All seven original rows still present.
**Explain after:** "Notice what it didn't do — it didn't just delete the incomplete rows. Silently dropping customer records would be worse than flagging them. That's a design decision baked into the skill, not something the model has to reinvent correctly every time."

### Prompt 5 — show precision-phrased variant
> *"Please identify and flag any customer records in customers.csv that are missing an email address, and report the total count."*

**Why this one:** the formal mirror of Prompt 4 — same intent, opposite register. Good pairing to show both ends of how people actually phrase requests.

---

## Part 3 — Prove It's Scoped Correctly (the credibility moment)

### Prompt 6 — a prompt that should NOT trigger this skill
> *"Can you review cypress/e2e/checkout/pay.cy.js for convention violations before I open the PR?"*

**Say while it runs:** "This is a completely different kind of request. Watch which skill actually fires."
**Expected behavior:** `cypress-code-review` fires instead (if installed) — or if it isn't installed in this demo environment, `csv-analyzer` should simply **not** engage, since nothing about this prompt matches its trigger description.
**Explain after:** "A skill that fires on everything is worse than no skill at all — this is proof it only activates when it's actually relevant, not just whenever any file or task is mentioned."

---

## Part 4 — Show the Honest Limits (builds trust, don't skip this)

### Prompt 7 — an input the skill isn't built for
> *"I have a budget.csv with columns 'category' and 'amount_spent' — can you chart the top spending categories?"*

**Expected behavior:** the skill should recognize this doesn't match what its bundled scripts expect (`month`/`revenue` columns specifically) and say so rather than forcing a mismatched file through, per its own stated scope (`SKILL.md`'s "What This Skill Does NOT Do" section).
**Explain after:** "This is the moment that actually matters most in a demo like this — a skill that admits its boundaries instead of confidently producing a wrong answer is the whole point of writing `SKILL.md` this way. If your team only remembers one thing from this demo, I'd want it to be this one."

---

## Suggested Narration Arc (if presenting to the wider team)

1. **Open with Prompt 1** — establish capability immediately, don't bury the impressive part.
2. **Prompts 2–3** — flexibility and phrasing robustness, back to back, fast.
3. **Prompt 4** — switch domains to show this isn't a one-trick skill.
4. **Prompt 5** — quick, just to reinforce robustness a second time without dwelling.
5. **Prompt 6** — slow down here; this is the "why a skill and not just a smart model" moment.
6. **Prompt 7** — close on this one. Ending on a boundary rather than a flashy success is a deliberate choice — it's what makes the rest of the demo credible in hindsight rather than feeling like a highlight reel.

**Total run time:** roughly 10–12 minutes at a comfortable pace, including narration — enough to make every point without losing the room.

---

*Grounded in: `csvskill--SKILL.md`, `csvskill--evals.json`, `csvskill-fixture--sales_2025.csv`, `csvskill-fixture--customers.csv`, and the verified real outputs in `csv-analyzer-complete-usage-guide.md`.*
