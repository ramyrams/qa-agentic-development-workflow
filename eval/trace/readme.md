Eval Series
Ep 1: How to read traces? https://www.youtube.com/watch?v=vULNPHtuCqQ



I rebuilt the lab around a real Copilot custom agent and skill, and ran the whole loop once myself to check it works. It needs no simulated agent, no API keys and no packages, only VS Code, Copilot and Node.

**How it works:**
- **The agent and skill under test:** a custom agent called *Maple Support* handles 12 support cases using its skill, `maple-support/SKILL.md`, running on Claude Sonnet 5.
- **Where the traces come from:** the skill includes a small tool script, and every action the agent takes goes through it. The script writes each call to a trace file, one per case. Each trace also stores a fingerprint of the SKILL.md version that produced it.
- **The flaws to find:** the first version of SKILL.md has five planted problems. One instruction retries lookups in a loop, one invents a delivery date, one refunds gold-tier customers above the $500 limit, one says the address update "always succeeds", and nothing checks that the customer owns the order.
- **Helper agents:** *Trace Investigator* (read-only), *eval-writer* and *skill-fixer*. They hand off to each other, and each can only touch its own files. The skill-fixer can edit only SKILL.md, so it can't pass the tests by weakening them.
- **Regression tests (`npm test`):** they fail if a test case's trace came from an older SKILL.md. Any change to the skill therefore forces the cases to be run again before the tests can pass.

**What I validated:** I acted as the agent and followed each version of SKILL.md literally, calling the same tool script Copilot calls. I then checked the whole flow again from the packaged zip files.

| Stage | Result |
|---|---|
| Skill v1, one starter eval | Tests pass 7 of 7, even though the skill is broken |
| Skill v1, five evals | 5 of 12 cases fail, one for each planted problem |
| Simple detection rules | Catch only 2 of the 5 failures |
| SKILL.md edited, cases not yet re-run | All 12 test cases reported as out of date |
| Fixed skill, cases re-run | 12 of 12 pass |
| Skill "tidied" so the $500 rule is removed | The two large-refund cases fail |

**Limits of this check:** I'm a different model running outside Copilot, and I followed each instruction to the letter. Claude Sonnet 5 in Copilot will sometimes ignore a bad instruction and sometimes follow it. The lab treats that variation as a teaching point: even when a flaw doesn't show up in one run, the skill is still wrong and the eval still protects you. I can't confirm from here how Copilot treats the tool names in the agent files, or how often it asks you to approve terminal commands. Do one dry run on a team machine before lab day.

**What's in the files:**
- **Lab guide:** the published page, rewritten in place for this design. Ten steps, about 100 minutes.
- **Starter zip:** the repo learners open. It includes my recorded first-version run as a fallback for anyone without Copilot access.
- **Facilitator kit zip:**
  - an answer key linking each flawed instruction to its case and eval
  - the reference evals
  - each version of SKILL.md with the diff between them
  - replay scripts and traces from my run
  - a 15-minute demo script

These replace the previous zip files.
