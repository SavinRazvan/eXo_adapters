"""
File: test_echo_adapter_conformance.py
Path: tests/test_echo_adapter_conformance.py
Role: Conformance tests for exo-adapter-echo (second portable adapter).
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-brain-adapter-sdk, exo-adapter-echo, exo-brain-core-contracts
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from exo_adapter_echo import EchoRuntimeAdapter
from exo_brain_adapter_sdk import assert_runtime_adapter_contract


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_echo_adapter_package_conformance() -> None:
    adapter = EchoRuntimeAdapter(provider_id="echo-test")
    assert_runtime_adapter_contract(adapter)


def test_echo_adapter_portability_smoke_run_turn() -> None:
    adapter = EchoRuntimeAdapter(provider_id="echo-test")
    assert adapter.__class__.__module__.startswith("exo_adapter_echo.")

    async def _collect_event_types() -> list[str]:
        await adapter.start_session("sess-echo", metadata={"agent_id": "smoke-agent"})
        event_types: list[str] = []
        async for event in adapter.run_turn(
            session_id="sess-echo",
            user_input="hello",
            context={"run_id": "run-echo"},
        ):
            event_types.append(str(getattr(event.event_type, "value", event.event_type)))
        return event_types

    event_types = asyncio.run(_collect_event_types())
    assert "output_delta" in event_types
    assert "run_complete" in event_types


def test_echo_package_has_no_monorepo_imports() -> None:
    root = _repo_root()
    package_files = [
        root / "packages" / "exo-adapter-echo" / "src" / "exo_adapter_echo" / "__init__.py",
        root / "packages" / "exo-adapter-echo" / "src" / "exo_adapter_echo" / "runtime.py",
    ]
    for file_path in package_files:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            assert not stripped.startswith("from src."), f"Monorepo import found in {file_path}: {stripped}"
            assert not stripped.startswith("import src."), f"Monorepo import found in {file_path}: {stripped}"
