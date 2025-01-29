"""Simple test of new API Changes."""
import asyncio
import json
import pprint
from datetime import date, timedelta

from mytoyota.client import MyT
from mytoyota.models.summary import SummaryType

pp = pprint.PrettyPrinter(indent=4)
CREDENTIALS_FILE_NAME = "credentials.json"


def load_credentials():
    """Load credentials from 'CREDENTIAL_FILE_NAME'."""
    try:
        with open(CREDENTIALS_FILE_NAME, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError, ValueError) as exc:
        raise ValueError(
            "Did you forget to set your username and password? Or supply the credentials file?"
            f"Please set your username and password in a file on top level called '{CREDENTIALS_FILE_NAME}' in the format:"  # noqa: E501
            "{'username': '<username>', 'password': '<password>'}"
        ) from exc


credentials = load_credentials()
client = MyT(username=credentials["username"], password=credentials["password"])


async def get_information():
    """Test login and output from endpoints."""
    print("Logging in...")
    await client.login()

    print("Retrieving cars...")
    cars = await client.get_vehicles(metric=True) or []
    for car in cars:
        await car.update()
        # Dashboard Information
        pp.pprint(f"Dashboard: {car.dashboard}")
        # Electric Status Information
        pp.pprint(f"Electric Status: {car.electric_status}")
        # Location Information
        pp.pprint(f"Location: {car.location}")
        # Lock Status
        pp.pprint(f"Lock Status: {car.lock_status}")
        # Notifications
        pp.pprint(f"Notifications: {[[x] for x in car.notifications or []]}")
        # Service history
        pp.pprint(f"Latest service: {car.get_latest_service_history()}")
        # Summary
        pp.pprint(
            f"Summary: {[[x] for x in await car.get_summary(date.today() - timedelta(days=6 * 30), date.today(), summary_type=SummaryType.MONTHLY)]}"  # noqa: E501
        )


loop = asyncio.get_event_loop()
loop.run_until_complete(get_information())
loop.close()
