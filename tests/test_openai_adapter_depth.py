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
from unittest.mock import MagicMock

from exo_adapter_openai import OpenAIAgentsRuntimeAdapter, load_adapter
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


def test_openai_run_turn_non_dict_context_uses_echo_path() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-ctx")

    async def _collect() -> list[str]:
        await adapter.start_session("sess-ctx")
        types: list[str] = []
        async for event in adapter.run_turn(
            session_id="sess-ctx",
            user_input="hello",
            context="bad-context",  # type: ignore[arg-type]
        ):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
        return types

    assert asyncio.run(_collect()) == ["output_delta", "run_complete"]


def test_openai_run_turn_echo_path_without_api_key() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-fallback")

    async def _collect() -> list[str]:
        await adapter.start_session("sess-fallback")
        types: list[str] = []
        async for event in adapter.run_turn(
            session_id="sess-fallback",
            user_input="ping",
            context={"run_id": "run-fb"},
        ):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
        return types

    event_types = asyncio.run(_collect())
    assert event_types == ["output_delta", "run_complete"]


def test_planned_tool_call_validation_errors() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-planned-err")

    async def _run(context: dict[str, Any]) -> str:
        await adapter.start_session("sess-pe")
        code = ""
        async for event in adapter.run_turn("sess-pe", "x", context):
            if event.event_type == RuntimeEventType.ERROR:
                code = str(event.payload.get("code", ""))
        return code

    assert asyncio.run(_run({"planned_tool_call": "bad"})) == "RUNTIME_TURN_ERROR"
    assert asyncio.run(_run({"planned_tool_call": {"tool_name": ""}})) == "RUNTIME_TURN_ERROR"


def test_planned_tool_call_accepts_risk_tier_enum() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-tier-enum")

    async def _intent_tier() -> str:
        await adapter.start_session("sess-tier-enum")
        async for event in adapter.run_turn(
            "sess-tier-enum",
            "tool",
            {
                "run_id": "run-tier-enum",
                "planned_tool_call": {
                    "tool_name": "demo_tool",
                    "arguments": {},
                    "risk_tier": RiskTier.CRITICAL,
                },
            },
        ):
            if event.tool_call is not None:
                return str(event.tool_call.risk_tier.value)
        return ""

    assert asyncio.run(_intent_tier()) == "critical"


def test_planned_tool_call_coerces_unknown_risk_tier_to_low() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-tier")

    async def _intent_tier() -> str:
        await adapter.start_session("sess-tier")
        async for event in adapter.run_turn(
            "sess-tier",
            "tool",
            {
                "run_id": "run-tier",
                "planned_tool_call": {
                    "tool_name": "demo_tool",
                    "arguments": {},
                    "risk_tier": "not-a-real-tier",
                },
            },
        ):
            if event.tool_call is not None:
                return str(event.tool_call.risk_tier.value)
        return ""

    assert asyncio.run(_intent_tier()) == "low"


def test_submit_tool_results_invalid_list_yields_error() -> None:
    adapter = OpenAIAgentsRuntimeAdapter(provider_id="openai-tr-err")

    async def _collect() -> str:
        await adapter.start_session("sess-tr")
        code = ""
        async for event in adapter.submit_tool_results("sess-tr", "run-tr", object()):  # type: ignore[arg-type]
            if event.event_type == RuntimeEventType.ERROR:
                code = str(event.payload.get("code", ""))
        return code

    assert asyncio.run(_collect()) == "RUNTIME_TOOL_RESULT_ERROR"


def test_build_agent_tools_json_error_and_execution_failure() -> None:
    registry = _Registry([_Descriptor(name="beta")])
    executor = _Executor()

    async def _bad_json() -> str:
        tools = build_agent_tools(tool_registry=registry, tool_executor=executor)
        return await tools[0].on_invoke_tool(None, "not-json{")

    assert "TOOL_INPUT_ERROR" in asyncio.run(_bad_json())

    class _FailExecutor:
        def execute(self, call: ToolCallContext) -> _ExecResult:
            return _ExecResult(
                status=ToolStatus.ERROR,
                error=NormalizedError(code="EXEC_FAIL", category="runtime", message="boom"),
            )

    async def _fail_exec() -> str:
        tools = build_agent_tools(tool_registry=registry, tool_executor=_FailExecutor())
        return await tools[0].on_invoke_tool(None, "{}")

    assert "TOOL_EXECUTION_ERROR: boom" == asyncio.run(_fail_exec())


def test_build_agent_tools_success_scalar_and_risk_tier_string() -> None:
    registry = _Registry(
        [
            _Descriptor(
                name="gamma",
                risk_tier="high",  # type: ignore[arg-type]
                parameters_schema={"type": "object", "properties": {}},
            )
        ]
    )

    class _ScalarExecutor:
        def execute(self, call: ToolCallContext) -> _ExecResult:
            return _ExecResult(status=ToolStatus.SUCCESS, result={"value": None})

    tools = build_agent_tools(tool_registry=registry, tool_executor=_ScalarExecutor())

    async def _invoke() -> str:
        return await tools[0].on_invoke_tool(None, "{}")

    assert asyncio.run(_invoke()) == ""
    assert tools[0].name == "gamma"


def test_build_agent_tools_status_string_success_and_unknown_error() -> None:
    registry = _Registry([_Descriptor(name="epsilon")])

    class _StringStatusResult:
        status = "success"
        result = {"value": "plain"}

    class _StringExecutor:
        def execute(self, call: ToolCallContext) -> _StringStatusResult:
            return _StringStatusResult()

    tools = build_agent_tools(tool_registry=registry, tool_executor=_StringExecutor())

    async def _ok() -> str:
        return await tools[0].on_invoke_tool(None, "{}")

    assert asyncio.run(_ok()) == "plain"

    class _WeirdError:
        def __str__(self) -> str:
            return "weird-failure"

    class _WeirdExecutor:
        def execute(self, call: ToolCallContext) -> _ExecResult:
            return _ExecResult(status=ToolStatus.ERROR, error=_WeirdError())

    tools2 = build_agent_tools(tool_registry=registry, tool_executor=_WeirdExecutor())

    async def _weird() -> str:
        return await tools2[0].on_invoke_tool(None, "{}")

    assert asyncio.run(_weird()) == "TOOL_EXECUTION_ERROR: weird-failure"


def test_build_agent_tools_error_fallback_to_code_only() -> None:
    registry = _Registry([_Descriptor(name="delta")])

    class _CodeOnlyError:
        code = "ONLY_CODE"
        message = ""

    class _CodeExecutor:
        def execute(self, call: ToolCallContext) -> _ExecResult:
            return _ExecResult(status=ToolStatus.ERROR, error=_CodeOnlyError())

    tools = build_agent_tools(tool_registry=registry, tool_executor=_CodeExecutor())

    async def _invoke() -> str:
        return await tools[0].on_invoke_tool(None, "{}")

    assert asyncio.run(_invoke()) == "TOOL_EXECUTION_ERROR: ONLY_CODE"


def test_build_agent_tools_coerces_enum_risk_tier_and_none_error() -> None:
    registry = _Registry(
        [
            _Descriptor(
                name="zeta",
                risk_tier=RiskTier.MEDIUM,
                parameters_schema={"type": "object", "properties": {}},
            )
        ]
    )

    class _NoneErrorExecutor:
        def execute(self, call: ToolCallContext) -> _ExecResult:
            return _ExecResult(status=ToolStatus.ERROR, error=None)

    tools = build_agent_tools(tool_registry=registry, tool_executor=_NoneErrorExecutor())

    async def _fail() -> str:
        return await tools[0].on_invoke_tool(None, "{}")

    assert asyncio.run(_fail()) == "TOOL_EXECUTION_ERROR: unknown error"

    registry_bad = _Registry(
        [
            _Descriptor(
                name="eta",
                risk_tier="not-a-valid-tier",  # type: ignore[arg-type]
                parameters_schema={"type": "object", "properties": {}},
            )
        ]
    )
    captured: list[ToolCallContext] = []

    class _CaptureExecutor:
        def execute(self, call: ToolCallContext) -> _ExecResult:
            captured.append(call)
            return _ExecResult(status=ToolStatus.SUCCESS, result={"value": "ok"})

    tools2 = build_agent_tools(tool_registry=registry_bad, tool_executor=_CaptureExecutor())

    async def _ok() -> str:
        return await tools2[0].on_invoke_tool(None, "{}")

    assert asyncio.run(_ok()) == "ok"
    assert captured[0].risk_tier == RiskTier.LOW


def test_run_turn_streaming_output_delta_when_delegating(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from agents.items import (
        ItemHelpers,
        MessageOutputItem,
        ToolCallItem,
        ToolCallOutputItem,
    )
    from agents.stream_events import RunItemStreamEvent

    message_item = MagicMock(spec=MessageOutputItem)
    tool_call_item = MagicMock(spec=ToolCallItem)
    tool_output_item = MagicMock(spec=ToolCallOutputItem)

    class _Streamed:
        final_output = "stream-final"

        async def stream_events(self):
            yield object()  # ignored: not a RunItemStreamEvent
            yield RunItemStreamEvent(name="message_output_created", item=message_item)
            yield RunItemStreamEvent(name="tool_called", item=tool_call_item)
            yield RunItemStreamEvent(name="tool_output", item=tool_output_item)

    def _fake_run_streamed(agent, user_input):  # noqa: ARG001
        return _Streamed()

    monkeypatch.setattr("agents.Runner.run_streamed", _fake_run_streamed)
    monkeypatch.setattr(ItemHelpers, "text_message_output", lambda _item: "stream-chunk")

    registry = _Registry([_Descriptor(name="stream-tool")])
    executor = _Executor()
    adapter = OpenAIAgentsRuntimeAdapter(
        provider_id="openai-stream",
        tool_registry=registry,
        tool_executor=executor,
    )

    async def _collect() -> tuple[list[str], str | None]:
        await adapter.start_session(
            "sess-stream",
            metadata={"agent_id": "a1", "model": "gpt-4o-mini", "instructions": "hi"},
        )
        types: list[str] = []
        text: str | None = None
        async for event in adapter.run_turn("sess-stream", "stream me", {"run_id": "run-stream"}):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
            if event.event_type == RuntimeEventType.OUTPUT_DELTA:
                text = str(event.payload.get("text", ""))
        return types, text

    event_types, delta = asyncio.run(_collect())
    assert "output_delta" in event_types
    assert "run_complete" in event_types
    assert "tool_intent" not in event_types
    assert delta == "stream-chunk"


def test_run_turn_streaming_unexpected_error_yields_error_event(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def _boom(agent, user_input):  # noqa: ARG001
        raise RuntimeError("stream exploded")

    monkeypatch.setattr("agents.Runner.run_streamed", _boom)
    registry = _Registry([_Descriptor(name="tool-a")])
    adapter = OpenAIAgentsRuntimeAdapter(
        provider_id="openai-stream-err",
        tool_registry=registry,
        tool_executor=_Executor(),
    )

    async def _collect() -> dict[str, str]:
        await adapter.start_session("sess-se", metadata={"agent_id": "a1"})
        payload: dict[str, str] = {}
        async for event in adapter.run_turn("sess-se", "go", {"run_id": "run-se"}):
            if event.event_type == RuntimeEventType.ERROR:
                payload = {k: str(v) for k, v in event.payload.items()}
        return payload

    payload = asyncio.run(_collect())
    assert payload.get("code") == "RUNTIME_TURN_ERROR"
    assert "stream exploded" in payload.get("message", "")


def test_submit_tool_results_runner_failure_yields_error_event(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    async def _fail_run(agent, prompt):  # noqa: ARG001
        raise RuntimeError("continuation exploded")

    monkeypatch.setattr("agents.Runner.run", _fail_run)
    registry = _Registry([_Descriptor(name="tool-b")])
    adapter = OpenAIAgentsRuntimeAdapter(
        provider_id="openai-submit-err",
        tool_registry=registry,
        tool_executor=_Executor(),
    )
    result = ToolResult(
        schema_version="1.0",
        call_id="tc-err",
        tool_name="tool-b",
        status=ToolStatus.SUCCESS,
        result={"value": "ok"},
    )

    async def _collect() -> dict[str, str]:
        await adapter.start_session("sess-sbe", metadata={"agent_id": "a1"})
        payload: dict[str, str] = {}
        async for event in adapter.submit_tool_results("sess-sbe", "run-sbe", [result]):
            if event.event_type == RuntimeEventType.ERROR:
                payload = {k: str(v) for k, v in event.payload.items()}
        return payload

    payload = asyncio.run(_collect())
    assert payload.get("code") == "RUNTIME_TOOL_RESULT_ERROR"
    assert "continuation exploded" in payload.get("message", "")


def test_openai_capabilities_healthcheck_load_adapter() -> None:
    adapter = load_adapter(provider_id="openai-loaded")
    caps = adapter.get_capabilities()
    assert caps.provider_id == "openai-loaded"
    assert caps.supports_agents_sdk_native is True
    assert caps.should_force_deterministic() is False

    health = asyncio.run(adapter.healthcheck())
    assert str(getattr(health.state, "value", health.state)) == "healthy"
