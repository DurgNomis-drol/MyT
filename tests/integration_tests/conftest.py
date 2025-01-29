"""Need for pytest or else it will cause an import error in pytest."""

import json
from pathlib import Path
from typing import List

import pytest
from pytest_httpx import HTTPXMock

TEST_USER_NAME = "user@email.info"
TEST_USER_PASSWORD = "password"


@pytest.fixture(scope="module")
def data_folder(request) -> str:
    """Return the folder containing test files."""
    return str(Path(request.module.__file__).parent / "data")


def build_routes(httpx_mock: HTTPXMock, filenames: List[str]) -> None:  # noqa: D103
    for filename in filenames:
        path: str = f"{Path(__file__).parent}/data/"

        with open(
            f"{path}/{filename}", encoding="utf-8"
        ) as f:  # I cant see a problem for the tests
            routes = json.load(f)
            print("test routes", routes)

        for route in routes:
            httpx_mock.add_response(
                method=route["request"]["method"],
                url=route["request"]["url"],
                status_code=route["response"]["status"],
                content=route["response"]["content"]
                if isinstance(route["response"]["content"], str)
                else json.dumps(route["response"]["content"]),
                headers=route["response"]["headers"],
            )
