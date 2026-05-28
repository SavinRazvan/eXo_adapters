"""
File: test_echo_adapter_depth.py
Path: tests/test_echo_adapter_depth.py
Role: Additional echo adapter tests (errors, tool results, capabilities, factory).
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-adapter-echo, exo-brain-core-contracts
"""

from __future__ import annotations

import asyncio

from exo_adapter_echo import EchoRuntimeAdapter, load_adapter
from exo_brain_core_contracts import (
    HealthState,
    RuntimeEventType,
    SecurityTier,
    ToolResult,
    ToolStatus,
)


def test_echo_run_turn_invalid_user_input_yields_error() -> None:
    adapter = EchoRuntimeAdapter(provider_id="echo-err")

    async def _collect() -> dict[str, str]:
        await adapter.start_session("sess-echo-err")
        payload: dict[str, str] = {}
        async for event in adapter.run_turn(
            session_id="sess-echo-err",
            user_input=99,  # type: ignore[arg-type]
            context={"run_id": "run-err"},
        ):
            if event.event_type == RuntimeEventType.ERROR:
                payload = {k: str(v) for k, v in event.payload.items()}
        return payload

    payload = asyncio.run(_collect())
    assert payload.get("code") == "RUNTIME_TURN_ERROR"


def test_echo_submit_tool_results_happy_path_and_invalid_list() -> None:
    adapter = EchoRuntimeAdapter(provider_id="echo-tools")
    result = ToolResult(
        schema_version="1.0",
        call_id="tc1",
        tool_name="demo",
        status=ToolStatus.SUCCESS,
        result={"value": 1},
    )

    async def _ok() -> dict[str, object]:
        await adapter.start_session("sess-tools")
        payload: dict[str, object] = {}
        async for event in adapter.submit_tool_results("sess-tools", "run-t", [result]):
            if event.event_type == RuntimeEventType.RUN_COMPLETE:
                payload = dict(event.payload)
        return payload

    complete_payload = asyncio.run(_ok())
    assert complete_payload.get("tool_results_count") == 1

    async def _bad() -> str:
        code = ""
        async for event in adapter.submit_tool_results("sess-tools", "run-t", "nope"):  # type: ignore[arg-type]
            if event.event_type == RuntimeEventType.ERROR:
                code = str(event.payload.get("code", ""))
        return code

    assert asyncio.run(_bad()) == "RUNTIME_TOOL_RESULT_ERROR"


def test_echo_run_turn_non_dict_context_still_streams() -> None:
    adapter = EchoRuntimeAdapter(provider_id="echo-ctx")

    async def _collect() -> list[str]:
        await adapter.start_session("sess-ctx")
        types: list[str] = []
        async for event in adapter.run_turn(
            session_id="sess-ctx",
            user_input="ping",
            context="not-a-dict",  # type: ignore[arg-type]
        ):
            types.append(str(getattr(event.event_type, "value", event.event_type)))
        return types

    event_types = asyncio.run(_collect())
    assert event_types == ["output_delta", "run_complete"]


def test_echo_capabilities_healthcheck_and_load_adapter() -> None:
    adapter = load_adapter(provider_id="echo-loaded")
    caps = adapter.get_capabilities()
    assert caps.provider_id == "echo-loaded"
    assert caps.security_tier == SecurityTier.SELF_MANAGED
    assert caps.should_force_deterministic() is True

    health = asyncio.run(adapter.healthcheck())
    assert health.state == HealthState.HEALTHY
    assert "echo" in health.reason
