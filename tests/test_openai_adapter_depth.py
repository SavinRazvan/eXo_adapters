"""
File: test_openai_adapter_depth.py
Path: tests/test_openai_adapter_depth.py
Role: Additional OpenAI adapter behavior tests (planned tool intent, tool wiring, errors).
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-adapter-openai, exo-brain-core-contracts
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Iterable

from exo_adapter_openai import OpenAIAgentsRuntimeAdapter
from exo_adapter_openai.tool_wiring import build_agent_tools
from exo_brain_core_contracts import (
    NormalizedError,
    RiskTier,
    RuntimeEventType,
    ToolCallContext,
    ToolResult,
    ToolStatus,
)


@dataclass
class _Descriptor:
    name: str
    description: str = "demo tool"
    parameters_schema: dict[str, Any] | None = None
    risk_tier: RiskTier = RiskTier.LOW
    is_state_changing: bool = False


class _Registry:
    def __init__(self, descriptors: list[_Descriptor]) -> None:
        self._descriptors = descriptors

    def list_descriptors(self) -> Iterable[_Descriptor]:
        return list(self._descriptors)


@dataclass
class _ExecResult:
    status: ToolStatus
    result: dict[str, Any] | None = None
    error: Any = None


class _Executor:
    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self._payload = payload or {"value": "ok"}
        self.calls: list[ToolCallContext] = []

    def execute(self, call: ToolCallContext) -> _ExecResult:
        self.calls.append(call)
        return _ExecResult(status=ToolStatus.SUCCESS, result=self._payload)


def test_planned_tool_call_yields_tool_intent() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-planned")

    async def _collect() -> list[str]:
        await adapter.start_session("sess-planned")
        types: list[str] = []
        async for event in adapter.run_turn(
            session_id="sess-planned",
            user_input="run tool",
            context={
                "run_id": "run-planned",
                "planned_tool_call": {
                    "tool_name": "demo_tool",
                    "arguments": {"x": 1},
                    "risk_tier": "low",
                },
            },
        ):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
        return types

    event_types = asyncio.run(_collect())
    assert event_types == ["tool_intent"]


def test_run_turn_invalid_user_input_yields_error_event() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-err")

    async def _collect() -> tuple[list[str], dict[str, Any] | None]:
        await adapter.start_session("sess-err")
        types: list[str] = []
        payload: dict[str, Any] | None = None
        async for event in adapter.run_turn(
            session_id="sess-err",
            user_input=123,  # type: ignore[arg-type]
            context={"run_id": "run-err"},
        ):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
            if event.event_type == RuntimeEventType.ERROR:
                payload = dict(event.payload)
        return types, payload

    event_types, error_payload = asyncio.run(_collect())
    assert event_types == ["error"]
    assert error_payload is not None
    assert error_payload.get("code") == "RUNTIME_TURN_ERROR"


def test_build_agent_tools_invokes_executor() -> None:
    registry = _Registry([_Descriptor(name="alpha", parameters_schema={"type": "object", "properties": {}})])
    executor = _Executor(payload={"value": {"n": 42}})
    tools = build_agent_tools(
        tool_registry=registry,
        tool_executor=executor,
        session_id="sess-tools",
        agent_id="agent-1",
        provider_id="openai",
        tenant_id="tenant-1",
    )
    assert len(tools) == 1

    async def _invoke() -> str:
        return await tools[0].on_invoke_tool(None, json.dumps({"k": "v"}))

    output = asyncio.run(_invoke())
    assert executor.calls
    assert executor.calls[0].tool_name == "alpha"
    assert executor.calls[0].tenant_id == "tenant-1"
    parsed = json.loads(output)
    assert parsed["n"] == 42


def test_submit_tool_results_continues_with_runner_when_api_key(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class _RunResult:
        final_output = "final after tools"

    async def _fake_run(agent, user_input):  # noqa: ARG001
        return _RunResult()

    monkeypatch.setattr("agents.Runner.run", _fake_run)

    registry = _Registry([_Descriptor(name="alpha")])
    executor = _Executor()
    adapter = OpenAIAgentsRuntimeAdapter(
        provider_id="openai-submit",
        tool_registry=registry,
        tool_executor=executor,
    )

    async def _collect() -> tuple[list[str], str | None]:
        await adapter.start_session(
            "sess-submit",
            metadata={"agent_id": "a1", "model": "gpt-4o-mini", "instructions": "help"},
        )
        async for _ in adapter.run_turn("sess-submit", "what is 2+2?", {"run_id": "run-submit"}):
            pass
        types: list[str] = []
        text: str | None = None
        result = ToolResult(
            schema_version="1.0",
            call_id="tc1",
            tool_name="alpha",
            status=ToolStatus.SUCCESS,
            result={"value": {"answer": 4}},
        )
        async for event in adapter.submit_tool_results("sess-submit", "run-submit", [result]):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
            if event.event_type == RuntimeEventType.OUTPUT_DELTA:
                text = str(event.payload.get("text", ""))
        return types, text

    event_types, delta_text = asyncio.run(_collect())
    assert event_types == ["output_delta", "run_complete"]
    assert delta_text == "final after tools"


def test_submit_tool_results_without_api_key_returns_summary() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-no-key")
    result = ToolResult(
        schema_version="1.0",
        call_id="tc2",
        tool_name="demo",
        status=ToolStatus.BLOCKED,
        error=NormalizedError(code="POLICY_BLOCKED", category="policy", message="denied"),
    )

    async def _collect() -> tuple[list[str], str]:
        await adapter.start_session("sess-no-key")
        types: list[str] = []
        text = ""
        async for event in adapter.submit_tool_results("sess-no-key", "run-nk", [result]):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
            if event.event_type == RuntimeEventType.OUTPUT_DELTA:
                text = str(event.payload.get("text", ""))
        return types, text

    event_types, summary = asyncio.run(_collect())
    assert event_types == ["output_delta", "run_complete"]
    assert "demo" in summary
    assert "denied" in summary
