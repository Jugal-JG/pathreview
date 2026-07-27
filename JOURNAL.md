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

## Week 8 — Reproduce the issue

**Classification:** Bug (not a feature gap or doc issue).

**Root cause, with exact locations:**
- `Orchestrator.__init__` creates a single `ContextManager()` instance that
  lives for the lifetime of the orchestrator (`agent/orchestrator.py:29`).
- `Orchestrator._execute_tool` checks/stores results in that cache keyed only
  by `tool_name + sha256(tool_input)`, with no TTL, no profile/session
  scoping, and no expiry (`agent/orchestrator.py:150-155`).
- `SessionStore.delete()` exists (`agent/memory/session_store.py:68-81`) but
  is never called anywhere in `agent/orchestrator.py`. `run()` only ever
  merges old session state into new state and re-saves it
  (`agent/orchestrator.py:47-49` and `:65-67`) - it never clears anything.
- Net effect: if the same `Orchestrator` instance (the normal case for a
  long-lived process) serves two review requests for the same profile with
  the same tool input (e.g. an unchanged GitHub repo name), the second
  request gets served the first request's cached result instead of running
  fresh analysis - exactly what issue #43 describes.

**Reproduction steps:**
1. Instantiate one `Orchestrator` with a fake `github_tool` whose `execute()`
   increments a call counter and returns different data each real call
   (simulating updated GitHub state, e.g. star count going up).
2. Call `orchestrator.run(profile_id, profile_data)` once - `github_tool`
   executes, `call_count == 1`.
3. Call `orchestrator.run(profile_id, profile_data)` again for the *same*
   `profile_id` with the *same* `profile_data` (simulating "user asks for
   another review").
4. Expected: `github_tool` executes again (`call_count == 2`), returning
   fresh data.
5. Actual: `github_tool.call_count` stays at `1`. The logs show
   `tool_result_cache_hit` on the second call - the stale review #1 result
   is returned instead of a fresh one.

**Proof committed:**
- [`tests/unit/test_orchestrator_session_state.py`](tests/unit/test_orchestrator_session_state.py) -
  a failing pytest test (`test_second_review_does_not_reuse_stale_tool_result`)
  that encodes the exact reproduction above. It currently fails with
  `assert 1 == 2`, confirming the bug is real and reproducible on demand.

**Reproduction confirmed:** [x] Bug reliably reproduced locally, with a
failing test pinned to the responsible code path.
