"""
File: test_sdk_conformance.py
Path: tests/test_sdk_conformance.py
Role: Negative-path tests for adapter SDK conformance assertions.
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-brain-adapter-sdk
"""

from __future__ import annotations

import pytest

from exo_brain_adapter_sdk import assert_runtime_adapter_contract


class _MissingMethods:
    pass


class _SyncOnlyAdapter:
    async def start_session(self, session_id: str, metadata=None):  # noqa: ANN001, ARG002
        return None

    def run_turn(self, session_id: str, user_input: str, context: dict):  # noqa: ANN001, ARG002
        yield None

    async def submit_tool_results(self, session_id: str, run_id: str, tool_results: list):  # noqa: ANN001
        yield None

    async def healthcheck(self):
        return None


class _NoCapabilities:
    async def start_session(self, session_id: str, metadata=None):  # noqa: ANN001, ARG002
        return None

    async def run_turn(self, session_id: str, user_input: str, context: dict):  # noqa: ANN001, ARG002
        if False:
            yield None

    async def submit_tool_results(self, session_id: str, run_id: str, tool_results: list):  # noqa: ANN001
        if False:
            yield None

    async def healthcheck(self):
        return None


def test_conformance_raises_when_method_missing() -> None:
    with pytest.raises(AssertionError, match="Missing required runtime adapter method: start_session"):
        assert_runtime_adapter_contract(_MissingMethods())


def test_conformance_raises_when_method_not_async() -> None:
    with pytest.raises(AssertionError, match="Method must be async: run_turn"):
        assert_runtime_adapter_contract(_SyncOnlyAdapter())


def test_conformance_raises_when_get_capabilities_missing() -> None:
    with pytest.raises(AssertionError, match="get_capabilities"):
        assert_runtime_adapter_contract(_NoCapabilities())
