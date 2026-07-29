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

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/Jugal-JG/pathreview/commit/12338eb

**Reproduction summary:**
Instantiated one `Orchestrator` and called `run()` twice for the same profile
with identical tool input, using a fake `github_tool` that returns different
data on each real invocation. The tool executed only once (`call_count == 1`
after both calls) and the logs showed `tool_result_cache_hit` on the second
call — confirming the orchestrator's `ContextManager` cache (`agent/orchestrator.py`)
serves a stale result from the first review instead of running fresh analysis.

**PLAN.md link:** https://github.com/Jugal-JG/pathreview/blob/fix/43-clear-agent-session-state/PLAN.md

**Blockers or open questions:**
Need to decide whether the fix should scope/clear the `ContextManager` cache
per profile via the existing but unused `SessionStore.delete()`, or drop the
cross-request cache entirely — see Risks & unknowns in PLAN.md.

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Implemented the fix for issue #43: `Orchestrator.run()` now clears the
`ContextManager` cache and calls `SessionStore.delete(profile_id)` at the
start of every run, and persists only the current run's results instead
of merging with stale session state. Added `ContextManager.clear()`.
Updated `tests/unit/test_orchestrator_session_state.py` with three tests
covering the fix, session-state clearing, and in-request memoization —
all passing. This completes sub-tasks 1, 2, and 4 from PLAN.md.

**Next steps:**
Confirm `make check` and `make test-unit` pass (excluding documented
pre-existing failures), open the PR against `ascherj/pathreview`, share
it in the peer-review Slack channel, and address any feedback before
marking it ready for review.

**Blockers:**
None currently.

---
