"""Need for pytest or else it will cause an import error in pytest."""

from pathlib import Path

import pytest

from mytoyota.controller import CACHE_FILENAME


@pytest.fixture
def data_folder(request) -> str:
    """Return the folder containing test files."""
    return f"{Path(request.module.__file__).parent}/data"


@pytest.fixture
def remove_cache() -> None:
    """Remove the credentials cache file if it exists."""
    # Remove cache file if exists
    Path.unlink(CACHE_FILENAME, missing_ok=True)
