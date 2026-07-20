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

**Setup confirmation:** [ ] App runs locally at localhost:5173 (not yet confirmed: Docker is unavailable in this environment)

**Cohort ledger:** [ ] Issue added to cohort ledger (no cohort ledger is available in this repository)
