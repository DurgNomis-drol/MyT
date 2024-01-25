"""Vehicle model."""
import asyncio
import copy
import json
import logging
from datetime import date
from functools import partial
from itertools import groupby
from operator import attrgetter
from typing import Any, Dict, List, Optional, Tuple

from arrow import Arrow

import mytoyota.utils.logging.logging_config  # noqa # pylint: disable=unused-import
from mytoyota.api import Api
from mytoyota.models.dashboard import Dashboard
from mytoyota.models.endpoints.vehicle_guid import VehicleGuidModel
from mytoyota.models.location import Location
from mytoyota.models.lock_status import LockStatus
from mytoyota.models.nofication import Notification
from mytoyota.models.service_history import ServiceHistory
from mytoyota.models.summary import Summary, SummaryType
from mytoyota.models.trips import Trip
from mytoyota.utils.helpers import add_with_none
from mytoyota.utils.logging.log_utils import censor_all

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Vehicle:
    """Vehicle data representation."""

    def __init__(self, api: Api, vehicle_info: VehicleGuidModel, metric: bool = True) -> None:
        """Initialise the Vehicle data representation."""
        self._vehicle_info = vehicle_info
        self._api = api
        self._endpoint_data: Dict[str, Any] = {}
        self._metric = metric

        # Endpoint Name, Function to check if car supports the endpoint, endpoint to call to update
        api_endpoints = [
            {
                "name": "location",
                "capable": vehicle_info.extended_capabilities.last_parked_capable
                or vehicle_info.features.last_parked,
                "function": partial(
                    self._api.get_location_endpoint, vin=vehicle_info.vin, brand=vehicle_info.brand
                ),
            },
            {
                "name": "health_status",
                "capable": True,  # TODO Unsure of the required capability
                "function": partial(
                    self._api.get_vehicle_health_status_endpoint,
                    vin=vehicle_info.vin,
                    brand=vehicle_info.brand,
                ),
            },
            {
                "name": "electric_status",
                "capable": vehicle_info.extended_capabilities.econnect_vehicle_status_capable,
                "function": partial(
                    self._api.get_vehicle_electric_status_endpoint,
                    vin=vehicle_info.vin,
                    brand=vehicle_info.brand,
                ),
            },
            {
                "name": "telemetry",
                "capable": vehicle_info.extended_capabilities.telemetry_capable,
                "function": partial(
                    self._api.get_telemetry_endpoint,
                    vin=vehicle_info.vin,
                    brand=vehicle_info.brand,
                ),
            },
            {
                "name": "notifications",
                "capable": True,  # TODO Unsure of the required capability
                "function": partial(
                    self._api.get_notification_endpoint,
                    vin=vehicle_info.vin,
                    brand=vehicle_info.brand,
                ),
            },
            {
                "name": "status",
                "capable": vehicle_info.extended_capabilities.vehicle_status,
                "function": partial(
                    self._api.get_remote_status_endpoint,
                    vin=vehicle_info.vin,
                    brand=vehicle_info.brand,
                ),
            },
            {
                "name": "service_history",
                "capable": vehicle_info.features.service_history,
                "function": partial(
                    self._api.get_service_history_endpoint,
                    vin=vehicle_info.vin,
                    brand=vehicle_info.brand,
                ),
            },
        ]
        self._endpoint_collect = [
            (endpoint["name"], endpoint["function"])
            for endpoint in api_endpoints
            if endpoint["capable"]
        ]

    async def update(self) -> None:
        """Update the data for the vehicle.

        This method asynchronously updates the data for the vehicle by
        calling the endpoint functions in parallel.

        Returns
        -------
            None

        """

        async def parallel_wrapper(name: str, function: partial) -> Tuple[str, Dict[str, Any]]:
            r = await function()
            return name, r

        responses = asyncio.gather(
            *[parallel_wrapper(name, function) for name, function in self._endpoint_collect]
        )
        for name, data in await responses:
            self._endpoint_data[name] = data

    @property
    def vin(self) -> Optional[str]:
        """Return the vehicles VIN number.

        Returns
        -------
            The vehicles VIN number

        """
        return self._vehicle_info.vin

    @property
    def alias(self) -> Optional[str]:
        """Vehicle's alias.

        Returns
        -------
            Nickname of vehicle

        """
        return self._vehicle_info.nickname

    @property
    def type(self) -> Optional[str]:
        """Returns the "type" of vehicle.

        Returns
        -------
            "fuel" if only fuel based
            "mildhybrid" if hybrid
            "phev" if plugin hybrid
            "ev" if full electric vehicle
        """
        # TODO enum
        # TODO currently guessing until we see a mild hybrid and full EV
        # TODO should probably use electricalPlatformCode but values currently unknown
        # TODO list of fuel types. ?: G=Petrol Only, I=Hybrid
        return "phev" if self._vehicle_info.ev_vehicle and self._vehicle_info.fuel_type else "ev"

    @property
    def dashboard(self) -> Optional[Dashboard]:
        """Returns the Vehicle dashboard.

        The dashboard consists of items of information you would expect to
        find on the dashboard. i.e. Fuel Levels.

        Returns
        -------
            A dashboard
        """
        # Always returns a Dashboard object as we can always get the odometer value
        return Dashboard(
            self._endpoint_data["telemetry"] if "telemetry" in self._endpoint_data else None,
            self._endpoint_data["electric_status"]
            if "electric_status" in self._endpoint_data
            else None,
            self._endpoint_data["health_status"]
            if "health_status" in self._endpoint_data
            else None,
            self._metric,
        )

    @property
    def location(self) -> Optional[Location]:
        """Return the vehicles latest reported Location.

        Returns
        -------
          The latest location or None. If None vehicle car does not support
          providing location information.
          _Note_ an empty location object can be returned when the Vehicle
          supports location but none is currently available.
        """
        return (
            Location(self._endpoint_data["location"])
            if "location" in self._endpoint_data
            else None
        )

    @property  # TODO: Cant have a property with parameters! Split into two methods?
    def notifications(self) -> Optional[List[Notification]]:
        r"""Returns a list of notifications for the vehicle.

        Args:
        ----
            include_read (bool, optional): Indicates whether to include read notifications. \n
            Defaults to False.

        Returns:
        -------
            Optional[List[Notification]]: A list of notifications for the vehicle,
            or None if not supported.

        """
        if "notifications" in self._endpoint_data:
            ret: List[Notification] = []
            for p in self._endpoint_data["notifications"].payload:
                ret.extend(Notification(n) for n in p.notifications)
            return ret

        return None

    @property
    def service_history(self) -> Optional[List[ServiceHistory]]:
        r"""Returns a list of service history entries for the vehicle.

        Returns
        -------
            Optional[List[ServiceHistory]]: A list of service history entries for the vehicle,
            or None if not supported.

        """
        if "service_history" in self._endpoint_data:
            ret: List[ServiceHistory] = []
            payload = self._endpoint_data["service_history"].payload
            ret.extend(
                ServiceHistory(service_history) for service_history in payload.service_histories
            )
            return ret

        return None

    def get_latest_service_history(self) -> Optional[ServiceHistory]:
        r"""Return the latest service history entry for the vehicle.

        Returns
        -------
            Optional[ServiceHistory]: A service history entry for the vehicle,
            ordered by date and service_category. None if not supported or unknown.

        """
        if self.service_history is not None:
            return max(self.service_history, key=lambda x: (x.service_date, x.service_category))
        return None

    @property
    def lock_status(self) -> Optional[LockStatus]:
        """Returns the latest lock status of Doors & Windows.

        Returns
        -------
            Optional[LockStatus]: The latest lock status of Doors & Windows,
            or None if not supported.
        """
        return LockStatus(
            self._endpoint_data["status"] if "status" in self._endpoint_data else None
        )

    async def get_summary(
        self,
        from_date: date,
        to_date: date,
        summary_type: SummaryType = SummaryType.MONTHLY,
    ) -> List[Summary]:
        """Return a Daily, Weekly, Monthly or Yearly summary between the provided dates.

        All but Daily can return a partial time range. For example if the summary_type is weekly
        and the date ranges selected include partial weeks these partial weeks will be returned.
        The dates contained in the summary will indicate the range of dates that made up the
        partial week.

        Note: Weekly and yearly summaries lose a small amount of accuracy due to rounding issues

        Args:
        ----
            from_date (date, required): The inclusive from date to report summaries.
            to_date (date, required): The inclusive to date to report summaries.
            summary_type (SummaryType, optional): Daily, Monthly or Yearly summary.
                                                  Monthly by default.

        Returns:
        -------
            List[Summary]: A list of summaries or empty list if not supported.
        """
        if to_date > date.today():  # Future dates not allowed
            to_date = date.today()

        # Summary information is always returned in the first response.
        # No need to check all the following pages
        resp = await self._api.get_trips_endpoint(
            self.vin, from_date, to_date, summary=True, limit=1, offset=0
        )
        if resp.payload is None or len(resp.payload.summary) == 0:
            return []

        # Convert to response
        if summary_type == SummaryType.DAILY:
            return self._generate_daily_summaries(resp.payload.summary)
        elif summary_type == SummaryType.WEEKLY:
            return self._generate_weekly_summaries(resp.payload.summary)
        elif summary_type == SummaryType.MONTHLY:
            return self._generate_monthly_summaries(resp.payload.summary, from_date, to_date)
        elif summary_type == SummaryType.YEARLY:
            return self._generate_yearly_summaries(resp.payload.summary, to_date)
        else:
            raise AssertionError("No such SummaryType")

    async def get_current_day_summary(self) -> Optional[Summary]:
        """Return a summary for the current day.

        Returns
        -------
            Optional[Summary]: A summary or None if not supported.
        """
        summary = await self.get_summary(
            from_date=Arrow.now().date(),
            to_date=Arrow.now().date(),
            summary_type=SummaryType.DAILY,
        )
        assert len(summary) < 2
        return summary[0] if len(summary) > 0 else None

    async def get_current_week_summary(self) -> Optional[Summary]:
        """Return a summary for the current week.

        Returns
        -------
            Optional[Summary]: A summary or None if not supported.
        """
        summary = await self.get_summary(
            from_date=Arrow.now().floor("week").date(),
            to_date=Arrow.now().date(),
            summary_type=SummaryType.WEEKLY,
        )
        assert len(summary) < 2
        return summary[0] if len(summary) > 0 else None

    async def get_current_month_summary(self) -> Optional[Summary]:
        """Return a summary for the current month.

        Returns
        -------
            Optional[Summary]: A summary or None if not supported.
        """
        summary = await self.get_summary(
            from_date=Arrow.now().floor("month").date(),
            to_date=Arrow.now().date(),
            summary_type=SummaryType.MONTHLY,
        )
        assert len(summary) < 2
        return summary[0] if len(summary) > 0 else None

    async def get_current_year_summary(self) -> Optional[Summary]:
        """Return a summary for the current year.

        Returns
        -------
            Optional[Summary]: A summary or None if not supported.
        """
        summary = await self.get_summary(
            from_date=Arrow.now().floor("year").date(),
            to_date=Arrow.now().date(),
            summary_type=SummaryType.YEARLY,
        )
        assert len(summary) < 2
        return summary[0] if len(summary) > 0 else None

    async def get_trips(
        self, from_date: date, to_date: date, full_route: bool = False
    ) -> Optional[List[Trip]]:
        """Return information on all trips made between the provided dates.

        Args:
        ----
            from_date (date, required): The inclusive from date
            to_date (date, required): The inclusive to date
            full_route (bool, optional): Provide the full route information for each trip

        Returns:
        -------
            Optional[List[Something]]: A list of all trips or None if not supported.
        """
        ret: List[Trip] = []
        offset = 0
        while True:
            resp = await self._api.get_trips_endpoint(
                self.vin,
                from_date,
                to_date,
                summary=False,
                limit=5,
                offset=offset,
                route=full_route,
            )
            if resp.payload is None:
                break

            # Convert to response
            for t in resp.payload.trips:
                ret.append(Trip(t, self._metric))

            offset = resp.payload.metadata.pagination.next_offset
            if offset is None:
                break

        return ret

    #
    # More get functionality depending on what we find
    #

    async def set_alias(self, value) -> bool:
        """Set the alias for the vehicle.

        Args:
        ----
            value: The alias value to set for the vehicle.

        Returns:
        -------
            bool
        """
        return value

    #
    # More set functionality depending on what we find
    #

    def _dump_all(self) -> Dict[str, Any]:
        """Dump data from all endpoints for debugging and further work."""
        dump: [str, Any] = {"vehicle_info": json.loads(self._vehicle_info.model_dump_json())}
        for name, data in self._endpoint_data.items():
            dump[name] = json.loads(data.model_dump_json())

        return censor_all(copy.deepcopy(dump))

    def _generate_daily_summaries(self, summary) -> List[Summary]:
        summary.sort(key=attrgetter("year", "month"))
        return [
            Summary(
                histogram.summary,
                self._metric,
                Arrow(histogram.year, histogram.month, histogram.day).date(),
                Arrow(histogram.year, histogram.month, histogram.day).date(),
                histogram.hdc,
            )
            for month in summary
            for histogram in sorted(month.histograms, key=attrgetter("day"))
        ]

    def _generate_weekly_summaries(self, summary) -> List[Summary]:
        ret: List[Summary] = []
        summary.sort(key=attrgetter("year", "month"))

        # Flatten the list of histograms
        histograms = [histogram for month in summary for histogram in month.histograms]
        histograms.sort(key=lambda h: date(day=h.day, month=h.month, year=h.year))

        # Group histograms by week
        for _, week_histograms_iter in groupby(
            histograms, key=lambda h: Arrow(h.year, h.month, h.day).span("week")[0]
        ):
            week_histograms = list(week_histograms_iter)
            build_hdc = copy.copy(week_histograms[0].hdc)
            build_summary = copy.copy(week_histograms[0].summary)
            start_date = Arrow(
                week_histograms[0].year,
                week_histograms[0].month,
                week_histograms[0].day,
            )

            for histogram in week_histograms[1:]:
                add_with_none(build_hdc, histogram.hdc)
                build_summary += histogram.summary

            end_date = Arrow(
                week_histograms[-1].year,
                week_histograms[-1].month,
                week_histograms[-1].day,
            )
            ret.append(
                Summary(
                    build_summary,
                    self._metric,
                    start_date.date(),
                    end_date.date(),
                    build_hdc,
                )
            )

        return ret

    def _generate_monthly_summaries(
        self, summary, from_date: date, to_date: date
    ) -> List[Summary]:
        # Convert all the monthly responses from the payload to a summary response
        ret: List[Summary] = []
        summary.sort(key=attrgetter("year", "month"))
        for month in summary:
            month_start = Arrow(month.year, month.month, 1).date()
            month_end = Arrow(month.year, month.month, 1).shift(months=1).shift(days=-1).date()

            ret.append(
                Summary(
                    month.summary,
                    self._metric,
                    # The data might not include an entire month so update start and end dates
                    max(month_start, from_date),
                    min(month_end, to_date),
                    month.hdc,
                )
            )

        return ret

    def _generate_yearly_summaries(self, summary, to_date: date) -> List[Summary]:
        summary.sort(key=attrgetter("year", "month"))
        ret: List[Summary] = []
        build_hdc = copy.copy(summary[0].hdc)
        build_summary = copy.copy(summary[0].summary)
        start_date = date(day=1, month=summary[0].month, year=summary[0].year)

        if len(summary) == 1:
            ret.append(Summary(build_summary, self._metric, start_date, to_date, build_hdc))
        else:
            for month, next_month in zip(summary[1:], summary[2:] + [None]):
                summary_month = date(day=1, month=month.month, year=month.year)
                add_with_none(build_hdc, month.hdc)
                build_summary += month.summary

                if next_month is None or next_month.year != month.year:
                    end_date = min(to_date, date(day=31, month=12, year=summary_month.year))
                    ret.append(
                        Summary(build_summary, self._metric, start_date, end_date, build_hdc)
                    )
                    if next_month:
                        start_date = date(day=1, month=next_month.month, year=next_month.year)
                        build_hdc = copy.copy(next_month.hdc)
                        build_summary = copy.copy(next_month.summary)

        return ret
