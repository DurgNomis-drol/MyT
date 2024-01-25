"""Toyota Connected Services API."""

import logging
from datetime import date, datetime, timezone
from uuid import uuid4

import mytoyota.utils.logging.logging_config  # noqa # pylint: disable=unused-import
from mytoyota.const import (
    VEHICLE_ASSOCIATION_ENDPOINT,
    VEHICLE_GLOBAL_REMOTE_ELECTRIC_STATUS_ENDPOINT,
    VEHICLE_GLOBAL_REMOTE_STATUS_ENDPOINT,
    VEHICLE_GUID_ENDPOINT,
    VEHICLE_HEALTH_STATUS_ENDPOINT,
    VEHICLE_LOCATION_ENDPOINT,
    VEHICLE_NOTIFICATION_HISTORY_ENDPOINT,
    VEHICLE_SERVICE_HISTORY_ENDPONT,
    VEHICLE_TELEMETRY_ENDPOINT,
    VEHICLE_TRIPS_ENDPOINT,
)
from mytoyota.controller import Controller
from mytoyota.models.endpoints.electric import ElectricResponseModel
from mytoyota.models.endpoints.location import LocationResponseModel
from mytoyota.models.endpoints.notifications import NotificationResponseModel
from mytoyota.models.endpoints.service_history import ServiceHistoryResponseModel
from mytoyota.models.endpoints.status import RemoteStatusResponseModel
from mytoyota.models.endpoints.telemetry import TelemetryResponseModel
from mytoyota.models.endpoints.trips import TripsResponseModel
from mytoyota.models.endpoints.vehicle_guid import VehiclesResponseModel
from mytoyota.models.endpoints.vehicle_health import VehicleHealthResponseModel

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Api:
    """API Class. Allows access to available endpoints to retrieve the raw data."""

    def __init__(self, controller: Controller) -> None:
        """Initialise the API.

        Initialise the API and set the Controller

        Args:
        ----
            controller: Controller: A controller class to managing communication

        Returns:
        -------
            None
        """
        self.controller = controller

    async def _request_and_parse(self, model, method: str, endpoint: str, brand: str, **kwargs):
        """Parse requests and responses."""
        response = await self.controller.request_json(
            method=method, endpoint=endpoint, brand=brand, **kwargs
        )
        return model(**response)

    async def set_vehicle_alias_endpoint(self, alias: str, guid: str, vin: str, brand: str):
        """Set the alias for a vehicle."""
        return await self.controller.request_raw(
            method="PUT",
            endpoint=VEHICLE_ASSOCIATION_ENDPOINT,
            vin=vin,
            brand=brand,
            headers={
                "datetime": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
                "x-correlationid": str(uuid4()),
                "Content-Type": "application/json",
            },
            body={"guid": guid, "vin": vin, "nickName": alias},
        )

    #    TODO: Remove for now as it seems to have no effect.
    #    The App is sending it!
    #    async def post_wake_endpoint(self) -> None:
    #        """Send a wake request to the vehicle."""
    #        await self.controller.request_raw(
    #            method="POST", endpoint="/v2/global/remote/wake"
    #        )

    async def get_vehicles_endpoint(self, brand: str = "T") -> VehiclesResponseModel:
        """Return list of vehicles registered with provider."""
        parsed_response = await self._request_and_parse(
            VehiclesResponseModel, "GET", VEHICLE_GUID_ENDPOINT, brand
        )
        _LOGGER.debug(msg=f"Parsed 'VehiclesResponseModel': {parsed_response}")
        return parsed_response

    async def get_location_endpoint(self, vin: str, brand: str) -> LocationResponseModel:
        """Get the last known location of your car. Only updates when car is parked.

        Response includes Lat, Lon position. * If supported.

        Args:
        ----
            vin: (str): The vehicles VIN
            brand (str): The car brand used for the request.

        Returns:
        -------
            LocationResponseModel: A pydantic model for the location response
        """
        parsed_response = await self._request_and_parse(
            LocationResponseModel, "GET", VEHICLE_LOCATION_ENDPOINT, vin=vin, brand=brand
        )
        _LOGGER.debug(msg=f"Parsed 'LocationResponseModel': {parsed_response}")
        return parsed_response

    async def get_vehicle_health_status_endpoint(
        self, vin: str, brand: str
    ) -> VehicleHealthResponseModel:
        r"""Get the latest health status.

        Response includes the quantity of engine oil and any dashboard warning lights. \n
        * If supported.

        Args:
        ----
            vin: (str): The vehicles VIN
            brand (str): The car brand used for the request.

        Returns:
        -------
            VehicleHealthResponseModel: A pydantic model for the vehicle health response
        """
        parsed_response = await self._request_and_parse(
            VehicleHealthResponseModel, "GET", VEHICLE_HEALTH_STATUS_ENDPOINT, vin=vin, brand=brand
        )
        _LOGGER.debug(msg=f"Parsed 'VehicleHealthResponseModel': {parsed_response}")
        return parsed_response

    async def get_remote_status_endpoint(self, vin: str, brand: str) -> RemoteStatusResponseModel:
        """Get information about the vehicle."""
        parsed_response = await self._request_and_parse(
            RemoteStatusResponseModel,
            "GET",
            VEHICLE_GLOBAL_REMOTE_STATUS_ENDPOINT,
            vin=vin,
            brand=brand,
        )
        _LOGGER.debug(msg=f"Parsed 'RemoteStatusResponseModel': {parsed_response}")
        return parsed_response

    async def get_vehicle_electric_status_endpoint(
        self, vin: str, brand: str
    ) -> ElectricResponseModel:
        r"""Get the latest electric status.

        Response includes current battery level, EV Range, EV Range with AC, \n
        fuel level, fuel range and current charging status

        Args:
        ----
            vin: (str): The vehicles VIN
            brand (str): The car brand used for the request.

        Returns:
        -------
            ElectricResponseModel: A pydantic model for the electric response
        """
        parsed_response = await self._request_and_parse(
            ElectricResponseModel,
            "GET",
            VEHICLE_GLOBAL_REMOTE_ELECTRIC_STATUS_ENDPOINT,
            vin=vin,
            brand=brand,
        )
        _LOGGER.debug(msg=f"Parsed 'ElectricResponseModel': {parsed_response}")
        return parsed_response

    async def get_telemetry_endpoint(self, vin: str, brand: str) -> TelemetryResponseModel:
        """Get the latest telemetry status.

        Response includes current fuel level, distance to empty and odometer

        Args:
        ----
            vin: (str): The vehicles VIN
            brand (str): The car brand used for the request.

        Returns:
        -------
            TelemetryResponseModel: A pydantic model for the telemetry response
        """
        parsed_response = await self._request_and_parse(
            TelemetryResponseModel, "GET", VEHICLE_TELEMETRY_ENDPOINT, vin=vin, brand=brand
        )
        _LOGGER.debug(msg=f"Parsed 'TelemetryResponseModel': {parsed_response}")
        return parsed_response

    async def get_notification_endpoint(self, vin: str, brand: str) -> NotificationResponseModel:
        """Get all available notifications for the vehicle.

        A notification includes a message, notification date, read flag, date read.

        NOTE: Currently no way to mark notification as read or limit the response.

        Args:
        ----
            vin: (str): The vehicles VIN
            brand (str): The car brand used for the request.

        Returns:
        -------
            NotificationResponseModel: A pydantic model for the notification response
        """
        parsed_response = await self._request_and_parse(
            NotificationResponseModel,
            "GET",
            VEHICLE_NOTIFICATION_HISTORY_ENDPOINT,
            vin=vin,
            brand=brand,
        )
        _LOGGER.debug(msg=f"Parsed 'NotificationResponseModel': {parsed_response}")
        return parsed_response

    async def get_trips_endpoint(  # noqa: PLR0913
        self,
        vin: str,
        brand: str,
        from_date: date,
        to_date: date,
        route: bool = False,
        summary: bool = True,
        limit: int = 5,
        offset: int = 0,
    ) -> TripsResponseModel:
        r"""Get list of trips.

        Retrieves a list of all trips between the given dates. \n
        The default data(route = False, summary = False) provides
        a basic summary of each trip and includes Coaching message and electrical use.

        Args:
        ----
            vin: str:        The vehicles VIN
            brand: str:      The car brand used for the request.
            from_date: date: From date to include trips, inclusive. Cant be in the future.
            to_date: date:   To date to include trips, inclusive. Cant be in the future.
            route: bool:     If true returns the route of each trip as a list of coordinates.
                             Suitable for drawing on a map.
            summary: bool:   If true returns a summary of each month and day in the date range
            limit: int:      Limit of number of trips to return in one request. Max 50.
            offset: int:     Offset into trips to start the request.

        Returns:
        -------
            TripsResponseModel: A pydantic model for the trips response
        """
        endpoint = VEHICLE_TRIPS_ENDPOINT.format(
            from_date=from_date,
            to_date=to_date,
            route=route,
            summary=summary,
            limit=limit,
            offset=offset,
        )
        parsed_response = await self._request_and_parse(
            TripsResponseModel, "GET", endpoint, vin=vin, brand=brand
        )
        _LOGGER.debug(msg=f"Parsed 'TripsResponseModel': {parsed_response}")
        return parsed_response

    async def get_service_history_endpoint(
        self, vin: str, brand: str
    ) -> ServiceHistoryResponseModel:
        """Get the current servic history.

        Response includes service category, date and dealer.

        Args:
        ----
            vin: (str): The vehicles VIN
            brand (str): The car brand used for the request.

        Returns:
        -------
            ServicHistoryResponseModel: A pydantic model for the service history response
        """
        parsed_response = await self._request_and_parse(
            ServiceHistoryResponseModel,
            "GET",
            VEHICLE_SERVICE_HISTORY_ENDPONT,
            vin=vin,
            brand=brand,
        )
        _LOGGER.debug(msg=f"Parsed 'ServiceHistoryResponseModel': {parsed_response}")
        return parsed_response
