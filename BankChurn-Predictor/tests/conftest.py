from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from common_utils.seed import set_seed


@pytest.fixture(autouse=True)
def deterministic_seed() -> Generator[None, None, None]:
    """Set a deterministic global seed for every test.

    Resolution order:
    1. TEST_SEED env var if defined.
    2. SEED env var if defined.
    3. Fallback to 42.
    """

    seed = int(os.getenv("TEST_SEED", os.getenv("SEED", "42")))
    set_seed(seed)
    yield
