"""Client for connecting to Toyota Connected Services.

A client for connecting to MyT (Toyota Connected Services) and retrieving vehicle
information, sensor data, fuel level, driving statistics and more.

  Typical usage example:

  client = MyT()
  vehicles = await client.get_vehicles()
"""
import logging
from typing import List, Optional

import mytoyota.utils.logging.logging_config  # noqa # pylint: disable=unused-import
from mytoyota.api import Api
from mytoyota.models.vehicle import Vehicle

from .controller import Controller
from .exceptions import ToyotaInvalidUsernameError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MyT:
    """Connected Services client.

    Connected services client class.

    NOTE: Only tested with Toyota endpoints to this point.
        Do you have a Lexus/Subaru and are willing to help?
    """

    def __init__(
        self,
        username: str,
        password: str,
        controller_class=Controller,
    ) -> None:
        """Initialise Connected Services client."""
        if username is None or "@" not in username:
            raise ToyotaInvalidUsernameError

        self._api = Api(
            controller_class(
                username=username,
                password=password,
            ),
        )

    async def login(self) -> None:
        """Perform first login.

        Performs first login to Toyota's servers. Should be ideally be used
        the very first time you login in. Fetches a token and stores it in
        the controller object for future use.

        """
        _LOGGER.debug("Performing first login")
        await self._api.controller.login()

    async def get_vehicles(self, metric: bool = True, brand: str = "T") -> Optional[List[Vehicle]]:
        """Return a list of vehicles."""
        _LOGGER.debug("Getting list of vehicles associated with the account")
        vehicles = await self._api.get_vehicles_endpoint(brand)
        if vehicles.payload is not None:
            return [Vehicle(self._api, v, metric) for v in vehicles.payload]

        return []
