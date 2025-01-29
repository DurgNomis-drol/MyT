"""pytest tests for mytoyota using httpx mocking."""
import json
from datetime import datetime, timedelta

import pytest
from pytest_httpx import HTTPXMock

from mytoyota import MyT
from mytoyota.exceptions import ToyotaInvalidUsernameError, ToyotaLoginError

from .conftest import TEST_USER_NAME, TEST_USER_PASSWORD, build_routes

# Global in-memory cache for testing
cache = {}


@pytest.mark.asyncio
async def test_authenticate(httpx_mock):  # noqa: D103
    build_routes(httpx_mock, filenames=["authenticate_working.json"])

    client = MyT(TEST_USER_NAME, TEST_USER_PASSWORD)
    # Nothing validates this is correct, just replays a "correct" authentication sequence
    await client.login()


@pytest.mark.asyncio
async def test_authenticate_invalid_username(httpx_mock: HTTPXMock):  # noqa: D103
    build_routes(httpx_mock, filenames=["authenticate_invalid_username.json"])

    client = MyT("invalid.user@email.com", TEST_USER_PASSWORD)
    # Nothing validates this is correct, just replays an invalid username authentication sequence
    with pytest.raises(ToyotaInvalidUsernameError):
        await client.login()


@pytest.mark.asyncio
async def test_authenticate_invalid_password(httpx_mock: HTTPXMock):  # noqa: D103
    build_routes(httpx_mock, filenames=["authenticate_invalid_password.json"])

    client = MyT(TEST_USER_NAME, "invalid_password")
    # Nothing validates this is correct, just replays an invalid username authentication sequence
    with pytest.raises(ToyotaLoginError):
        await client.login()


@pytest.mark.asyncio
async def test_authenticate_refresh_token(data_folder, httpx_mock: HTTPXMock):  # noqa: D103
    # Load the cached token and set it to expire soon
    with open(f"{data_folder}/cached_token.json", encoding="utf-8") as f:  # noqa: ASYNC101. I dont see this as a problem in test code
        valid_token = json.load(f)
        valid_token["expiration"] = (
            datetime.now() - timedelta(hours=1)
        ).isoformat()  # expired token

        # Initialize the in-memory cache with the expired token
        cache[TEST_USER_NAME] = {
            "access_token": valid_token["access_token"],
            "refresh_token": valid_token["refresh_token"],
            "uuid": valid_token["uuid"],
            "expiration": valid_token["expiration"],
        }

    build_routes(httpx_mock, filenames=["authenticate_working.json"])

    client = MyT(TEST_USER_NAME, TEST_USER_PASSWORD)
    # This should trigger a refresh token sequence
    await client.login()


@pytest.mark.asyncio
async def test_get_static_data(data_folder, httpx_mock: HTTPXMock):  # noqa: D103
    # Create valid token => Means no authentication requests
    with open(f"{data_folder}/cached_token.json", encoding="utf-8") as f:  # noqa: ASYNC101. I dont see this as a problem in test code
        valid_token = json.load(f)
        valid_token["expiration"] = (datetime.now() + timedelta(hours=4)).isoformat()

        # Initialize the in-memory cache with the valid token
        cache[TEST_USER_NAME] = {
            "access_token": valid_token["access_token"],
            "refresh_token": valid_token["refresh_token"],
            "uuid": valid_token["uuid"],
            "expiration": valid_token["expiration"],
        }

    build_routes(httpx_mock, filenames=["authenticate_working.json", "get_static_data.json"])

    client = MyT(TEST_USER_NAME, TEST_USER_PASSWORD)
    await client.login()
    cars = await client.get_vehicles(metric=True)
    car = cars[0]
    await car.update()

    # Check VIN
    assert car.vin == "12345678912345678"

    # Check alias
    assert car.alias == "RAV4"

    # Check Dashboard
    assert car.dashboard.odometer == 9999.975
    assert car.dashboard.fuel_level == 10
    assert car.dashboard.battery_level == 22
    assert car.dashboard.fuel_range == 112.654
    assert car.dashboard.battery_range == 33.0
    assert car.dashboard.battery_range_with_ac == 30
    assert car.dashboard.range == 100
    assert len(car.dashboard.warning_lights) == 0

    # Check location
    assert car.location.latitude == 50.0
    assert car.location.longitude == 0.0

    # Check Notifications
    assert len(car.notifications) == 3
    assert (
        car.notifications[0].message
        == "2020 RAV4 PHEV: Climate control was interrupted (Door open) [1]"
    )
    assert car.notifications[0].type == "alert"
    assert car.notifications[0].category == "RemoteCommand"
    assert (
        car.notifications[1].message
        == "2020 RAV4 PHEV: Climate was started and will automatically shut off."
    )
    assert car.notifications[2].message == "2020 RAV4 PHEV: Charging Interrupted [4]."
