"""
File: test_core_contracts_depth.py
Path: tests/test_core_contracts_depth.py
Role: Deeper unit tests for exo-brain-core-contracts (events, capabilities, tool_io).
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-brain-core-contracts
"""

from __future__ import annotations

from exo_brain_core_contracts import (
    ProviderCapabilityMap,
    RiskTier,
    RuntimeEvent,
    RuntimeEventType,
    ToolCallContext,
    ToolStatus,
    blocked_result,
)


def test_runtime_event_factory_helpers() -> None:
    call = ToolCallContext(
        schema_version="1.0",
        call_id="tc1",
        session_id="sess",
        run_id="run1",
        job_id="job",
        task_id="task",
        agent_id="agent",
        provider_id="echo",
        tool_name="demo",
        arguments={},
    )
    intent = RuntimeEvent.tool_intent("sess", "run1", call, correlation_id="corr")
    assert intent.event_type == RuntimeEventType.TOOL_INTENT
    assert intent.correlation_id == "corr"
    assert intent.tool_call is call

    delta = RuntimeEvent.output_delta("sess", "run1", "hello")
    assert delta.payload["text"] == "hello"
    assert delta.correlation_id == "run1"

    progress = RuntimeEvent.tool_progress(
        "sess",
        "run1",
        call_id="tc1",
        tool_name="demo",
        state="running",
        tool_status="ok",
        error_code="",
        job_id="j1",
        correlation_id="corr2",
    )
    assert progress.event_type == RuntimeEventType.TOOL_PROGRESS
    assert progress.payload["state"] == "running"

    complete = RuntimeEvent.run_complete("sess", "run1", output={"status": "done"})
    assert complete.event_type == RuntimeEventType.RUN_COMPLETE
    assert complete.payload["status"] == "done"

    err = RuntimeEvent.error("sess", "run1", "E_CODE", "boom")
    assert err.event_type == RuntimeEventType.ERROR
    assert err.payload == {"code": "E_CODE", "message": "boom"}


def test_provider_capability_map_should_force_deterministic() -> None:
    hybrid = ProviderCapabilityMap(provider_id="p1", reliability_score=5)
    assert hybrid.should_force_deterministic() is False

    echo_like = ProviderCapabilityMap(
        provider_id="echo",
        supports_structured_output=False,
        reliability_score=3,
    )
    assert echo_like.should_force_deterministic() is True

    no_tools = ProviderCapabilityMap(
        provider_id="p2",
        supports_function_calling=False,
    )
    assert no_tools.should_force_deterministic() is True


def test_blocked_result_sets_policy_fields() -> None:
    call = ToolCallContext(
        schema_version="1.0",
        call_id="tc-block",
        session_id="sess",
        run_id="run",
        job_id="job",
        task_id="task",
        agent_id="agent",
        provider_id="openai",
        tool_name="write_file",
        arguments={"path": "/tmp/x"},
        risk_tier=RiskTier.HIGH,
    )
    result = blocked_result(call, "TENANT_DENIED", "not allowed")
    assert result.status == ToolStatus.BLOCKED
    assert result.error.code == "POLICY_BLOCKED"
    assert result.error.details == {"reason_code": "TENANT_DENIED"}
