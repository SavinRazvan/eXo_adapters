"""
File: test_core_contracts_runtime_adapter.py
Path: tests/test_core_contracts_runtime_adapter.py
Role: Exercise RuntimeAdapter abstract stub bodies for full contract coverage.
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-brain-core-contracts
"""

from __future__ import annotations

import asyncio

import pytest

from exo_brain_core_contracts.runtime_adapter import RuntimeAdapter


class _BareObject:
    """Stand-in instance for calling unbound RuntimeAdapter abstract stubs."""


@pytest.mark.parametrize(
    ("method_name", "args"),
    [
        ("run_turn", ("sess", "hello", {})),
        ("submit_tool_results", ("sess", "run", [])),
        ("get_capabilities", ()),
    ],
)
def test_runtime_adapter_sync_abstract_stubs_raise_not_implemented(
    method_name: str,
    args: tuple[object, ...],
) -> None:
    stub = getattr(RuntimeAdapter, method_name)
    with pytest.raises(NotImplementedError):
        stub(_BareObject(), *args)


def test_runtime_adapter_start_session_stub_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        asyncio.run(RuntimeAdapter.start_session(_BareObject(), "sess", None))


def test_runtime_adapter_healthcheck_stub_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        asyncio.run(RuntimeAdapter.healthcheck(_BareObject()))
