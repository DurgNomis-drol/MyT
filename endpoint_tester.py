import asyncio
import json
import sys
from pprint import PrettyPrinter

from mytoyota import MyT
from mytoyota.models.vehicle import Vehicle


async def test_endpoint(myt: MyT, vehicle: Vehicle, method: str, endpoint: str) -> None:
    print(f"+++++ Endpoint: {endpoint}")
    try:
        response = await myt._api.controller.request_raw(method, endpoint, vin=vehicle.vin)
    except Exception as e:
        print(f"----- EXCEPTION: {e}")
        return
    if response:
        print(f"----- Status:\n({response.status_code},{response.reason_phrase})\n")
        print(f"----- Headers:\n{response.headers}\n")
        print("----- Content:\n")
        try:
            j = json.loads(response.content.decode("utf-8"))
            pp = PrettyPrinter(indent=4)
            pp.pprint(j)
        except Exception:
            print(f"{response.content.decode('utf-8')}")

    else:
        print(f"FAILED: {sys.argv[2]} => {response.reason_phrase}({response.status_code})")


def load_credentials():
    """Load credentials from 'credentials.json'."""
    try:
        with open("credentials.json", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None


async def main():
    print(sys.argv)

    credentials = load_credentials()
    if not credentials:
        raise ValueError(
            "Did you forget to set your username and password? Or supply the credentials file"
        )

    USERNAME = credentials["username"]
    PASSWORD = credentials["password"]

    client = MyT(username=USERNAME, password=PASSWORD)
    vehicles = await client.get_vehicles()
    assert len(vehicles) > 0

    # If an endpoint URL has been provided on the command line then we just test it
    if len(sys.argv) == 3:
        await test_endpoint(client, vehicles[0], sys.argv[1], sys.argv[2])

    elif len(sys.argv) == 2:
        with open(sys.argv[1], "r") as f:
            while True:
                url = f.readline()
                if len(url) == 0:
                    break

                if url[0] != "#":
                    print(f"-> {url.strip()} <-")
                    await test_endpoint(client, vehicles[0], "GET", url.strip())

        pass
    else:
        print('Expects 1 argument to file containing METHOD,"URL" pair on each line')
        print("Expects 2 arguments(METHOD, ENDPOINT to test a single endpoint")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
