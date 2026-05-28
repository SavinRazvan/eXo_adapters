"""
File: test_core_contracts_imports.py
Path: tests/test_core_contracts_imports.py
Role: Verify core contracts package exports load from installed distribution.
Used By:
 - pytest (adapter ecosystem repo)
Depends On:
 - exo-brain-core-contracts (editable install via requirements-ci.txt)
Notes:
 - Requires `pip install -r requirements-ci.txt` before pytest.
"""

from __future__ import annotations

import exo_brain_core_contracts as contracts


def test_core_contracts_exports_load() -> None:
    assert contracts.RuntimeAdapter is not None
    assert contracts.ToolCallContext is not None
    assert contracts.RuntimeEvent is not None
    assert callable(contracts.RuntimeEvent.tool_intent)
    assert callable(contracts.blocked_result)
