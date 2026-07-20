## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/43

**Issue title:** Agent session state is not cleared between reviews for the same user

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The agent session store currently caches review state by user ID. If a user updates
their portfolio and asks for another review, the orchestrator can reuse tool results
from the earlier review instead of gathering fresh information. This affects the
agent session-management code in `agent/memory/session_store.py` and can leave users
with feedback that no longer matches their portfolio. A successful fix will clear or
refresh the relevant session state so each subsequent review uses current tool results.

**Branch name:** fix/43-clear-agent-session-state

**Selection notes:**
- I can explain the issue: a second portfolio review for the same profile can
  retain data from the first review, so the user may receive stale feedback
  after changing their portfolio. The desired behavior is for a new review to
  use fresh tool results rather than prior session state.
- I located and read `agent/memory/session_store.py` and the surrounding
  `Orchestrator.run()` flow in `agent/orchestrator.py`. `SessionStore` already
  has a `delete()` method, while the orchestrator loads and saves state by
  profile ID without clearing it.
- The issue is labeled Tier 1 and estimated at 3–4 hours. The likely change is
  localized to the agent session lifecycle, making it a realistic first
  contribution; the issue shows no assignee, relationships, or dependencies.
- There is no existing session-store or orchestrator unit-test file. I read
  `tests/unit/test_readme_scorer.py` to confirm the project's pytest fixture
  and assertion style, and will add focused mocked-Redis tests for the chosen
  session-reset behavior.

**Setup confirmation:** [ ] App runs locally at localhost:5173 (not yet confirmed: Docker is unavailable in this environment)

**Cohort ledger:** [ ] Issue added to cohort ledger (the shared ledger requires signing in before I can add the claim)
