"""Reproduction test for issue #43: stale agent session state between reviews.

See JOURNAL.md (Week 8) for the reproduction narrative. This test is expected
to FAIL until the orchestrator clears/scopes cached tool results between
separate review requests for the same profile.
"""

import pytest

from agent.orchestrator import Orchestrator


class _FakeToolResult:
    def __init__(self, data):
        self.data = data


class _FakeGithubTool:
    """Simulates github_tool: same input (repo name), but the underlying
    GitHub data changes between calls, as it would after a user updates
    their portfolio and requests a fresh review."""

    name = "github_tool"

    def __init__(self):
        self.call_count = 0

    def execute(self, tool_input):
        self.call_count += 1
        return _FakeToolResult({"stars": 10 * self.call_count, "call_count": self.call_count})


@pytest.mark.unit
class TestOrchestratorSessionState:
    """Reproduces issue #43: cached tool results leak across separate
    review requests for the same profile instead of being cleared."""

    def test_second_review_does_not_reuse_stale_tool_result(self):
        github_tool = _FakeGithubTool()
        orchestrator = Orchestrator(tools={"github_tool": github_tool})

        profile_id = "user-123"
        profile_data = {
            "github_username": "octocat",
            "projects": [{"github_repo": "octocat/hello-world"}],
        }

        # Review #1: initial portfolio review.
        orchestrator.run(profile_id, profile_data)
        assert github_tool.call_count == 1

        # Review #2: user requests another review of the same profile.
        # The tool should execute again to produce fresh results, not
        # reuse the cached result from review #1.
        orchestrator.run(profile_id, profile_data)

        assert github_tool.call_count == 2, (
            "github_tool was not re-executed on the second review - "
            "Orchestrator's ContextManager cache (agent/orchestrator.py) "
            "served a stale result from the first review instead of "
            "running fresh analysis."
        )
