"""Toyota Connected Services API - Vehicle Models."""
from datetime import date
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from mytoyota.models.endpoints.common import StatusModel


class _TranslationModel(BaseModel):
    english: Optional[Any]  # TODO unsure what this returns
    french: Optional[Any]  # TODO unsure what this returns
    spanish: Optional[Any]  # TODO unsure what this returns


class _CapabilitiesModel(BaseModel):
    description: Optional[str]
    display: bool
    display_name: Optional[Any] = Field(alias="displayName")  # TODO unsure what this returns
    name: str
    translation: _TranslationModel


class _ExtendedCapabilitiesModel(BaseModel):
    c_scheduling: bool = Field(alias="acScheduling")
    battery_status: bool = Field(alias="batteryStatus")
    bonnet_status: bool = Field(alias="bonnetStatus")
    bump_collisions: bool = Field(alias="bumpCollisions")
    buzzer_capable: bool = Field(alias="buzzerCapable")
    charge_management: bool = Field(alias="chargeManagement")
    climate_capable: bool = Field(alias="climateCapable")
    climate_temperature_control_full: bool = Field(alias="climateTemperatureControlFull")
    climate_temperature_control_limited: bool = Field(alias="climateTemperatureControlLimited")
    dashboard_warning_lights: bool = Field(alias="dashboardWarningLights")
    door_lock_unlock_capable: bool = Field(alias="doorLockUnlockCapable")
    drive_pulse: bool = Field(alias="drivePulse")
    ecare: bool = Field(alias="ecare")
    econnect_climate_capable: bool = Field(alias="econnectClimateCapable")
    econnect_vehicle_status_capable: bool = Field(alias="econnectVehicleStatusCapable")
    electric_pulse: bool = Field(alias="electricPulse")
    emergency_assist: bool = Field(alias="emergencyAssist")
    enhanced_security_system_capable: bool = Field(alias="enhancedSecuritySystemCapable")
    equipped_with_alarm: bool = Field(alias="equippedWithAlarm")
    ev_battery: bool = Field(alias="evBattery")
    ev_charge_stations_capable: bool = Field(alias="evChargeStationsCapable")
    fcv_stations_capable: bool = Field(alias="fcvStationsCapable")
    front_defogger: bool = Field(alias="frontDefogger")
    front_driver_door_lock_status: bool = Field(alias="frontDriverDoorLockStatus")
    front_driver_door_open_status: bool = Field(alias="frontDriverDoorOpenStatus")
    front_driver_door_window_status: bool = Field(alias="frontDriverDoorWindowStatus")
    front_driver_seat_heater: bool = Field(alias="frontDriverSeatHeater")
    front_driver_seat_ventilation: bool = Field(alias="frontDriverSeatVentilation")
    front_passenger_door_lock_status: bool = Field(alias="frontPassengerDoorLockStatus")
    front_passenger_door_open_status: bool = Field(alias="frontPassengerDoorOpenStatus")
    front_passenger_door_window_status: bool = Field(alias="frontPassengerDoorWindowStatus")
    front_passenger_seat_heater: bool = Field(alias="frontPassengerSeatHeater")
    front_passenger_seat_ventilation: bool = Field(alias="frontPassengerSeatVentilation")
    fuel_level_available: bool = Field(alias="fuelLevelAvailable")
    fuel_range_available: bool = Field(alias="fuelRangeAvailable")
    guest_driver: bool = Field(alias="guestDriver")
    hazard_capable: bool = Field(alias="hazardCapable")
    horn_capable: bool = Field(alias="hornCapable")
    hybrid_pulse: bool = Field(alias="hybridPulse")
    hydrogen_pulse: bool = Field(alias="hydrogenPulse")
    last_parked_capable: bool = Field(alias="lastParkedCapable")
    light_status: bool = Field(alias="lightStatus")
    lights_capable: bool = Field(alias="lightsCapable")
    manual_rear_windows: bool = Field(alias="manualRearWindows")
    mirror_heater: bool = Field(alias="mirrorHeater")
    moonroof: bool = Field(alias="moonroof")
    next_charge: bool = Field(alias="nextCharge")
    power_tailgate_capable: bool = Field(alias="powerTailgateCapable")
    power_windows_capable: bool = Field(alias="powerWindowsCapable")
    rear_defogger: bool = Field(alias="rearDefogger")
    rear_driver_door_lock_status: bool = Field(alias="rearDriverDoorLockStatus")
    rear_driver_door_open_status: bool = Field(alias="rearDriverDoorOpenStatus")
    rear_driver_door_window_status: bool = Field(alias="rearDriverDoorWindowStatus")
    rear_driver_seat_heater: bool = Field(alias="rearDriverSeatHeater")
    rear_driver_seat_ventilation: bool = Field(alias="rearDriverSeatVentilation")
    rear_hatch_rear_window: bool = Field(alias="rearHatchRearWindow")
    rear_passenger_door_lock_status: bool = Field(alias="rearPassengerDoorLockStatus")
    rear_passenger_door_open_status: bool = Field(alias="rearPassengerDoorOpenStatus")
    rear_passenger_door_window_status: bool = Field(alias="rearPassengerDoorWindowStatus")
    rear_passenger_seat_heater: bool = Field(alias="rearPassengerSeatHeater")
    rear_passenger_seat_ventilation: bool = Field(alias="rearPassengerSeatVentilation")
    remote_econnect_capable: bool = Field(alias="remoteEConnectCapable")
    remote_engine_start_stop: bool = Field(alias="remoteEngineStartStop")
    smart_key_status: bool = Field(alias="smartKeyStatus")
    steering_heater: bool = Field(alias="steeringHeater")
    stellantis_climate_capable: bool = Field(alias="stellantisClimateCapable")
    stellantis_vehicle_status_capable: bool = Field(alias="stellantisVehicleStatusCapable")
    sunroof: bool = Field(alias="sunroof")
    telemetry_capable: bool = Field(alias="telemetryCapable")
    trunk_lock_unlock_capable: bool = Field(alias="trunkLockUnlockCapable")
    try_and_play: bool = Field(alias="tryAndPlay")
    vehicle_diagnostic_capable: bool = Field(alias="vehicleDiagnosticCapable")
    vehicle_finder: bool = Field(alias="vehicleFinder")
    vehicle_status: bool = Field(alias="vehicleStatus")
    we_hybrid_capable: bool = Field(alias="weHybridCapable")
    weekly_charge: bool = Field(alias="weeklyCharge")


class _LinksModel(BaseModel):
    body: Optional[str]  # TODO unsure what this returns
    button_text: Optional[str] = Field(alias="buttonText")
    image_url: Optional[str] = Field(alias="imageUrl", default=None)
    link: Optional[str]
    name: Optional[str]


class _DcmModel(BaseModel):  # Data connection model
    country_code: Optional[str] = Field(alias="countryCode", default=None)
    destination: str = Field(alias="dcmDestination")
    grade: str = Field(alias="dcmGrade")
    car_model_year: str = Field(alias="dcmModelYear")
    supplier: str = Field(alias="dcmSupplier")
    supplier_name: str = Field(alias="dcmSupplierName")
    euicc_id: str = Field(alias="euiccid")
    hardware_type: Optional[str] = Field(alias="hardwareType")
    vehicle_unit_terminal_number: Optional[str] = Field(alias="vehicleUnitTerminalNumber")


class _HeadUnitModel(BaseModel):
    description: Optional[Any] = Field(alias="huDescription")  # TODO unsure what this returns
    generation: Optional[Any] = Field(alias="huGeneration")  # TODO unsure what this returns
    version: Optional[Any] = Field(alias="huVersion")  # TODO unsure what this returns
    mobile_platform_code: Optional[Any] = Field(
        alias="mobilePlatformCode"
    )  # TODO unsure what this returns
    multimedia_type: Optional[Any] = Field(alias="multimediaType")  # TODO unsure what this returns


class _SubscriptionsModel(BaseModel):
    auto_renew: bool = Field(alias="autoRenew")
    category: str
    components: Optional[Any]  # TODO unsure what this returns
    consolidated_goodwill_ids: List[Any] = Field(
        alias="consolidatedGoodwillIds"
    )  # TODO unsure what this returns
    consolidated_product_ids: List[Any] = Field(
        alias="consolidatedProductIds"
    )  # TODO unsure what this returns
    display_procuct_name: str = Field(alias="displayProductName")
    display_term: str = Field(alias="displayTerm")
    future_cancel: bool = Field(alias="futureCancel")
    good_will_issued_for: Optional[Any] = Field(
        alias="goodwillIssuedFor"
    )  # TODO unsure what this returns
    product_code: str = Field(alias="productCode")
    product_description: str = Field(alias="productDescription")
    product_line: str = Field(alias="productLine")
    product_name: str = Field(alias="productName")
    procut_type: Optional[Any] = Field(alias="productType")
    renewable: bool
    status: str
    subscription_end_date: date = Field(alias="subscriptionEndDate")
    subscription_id: str = Field(alias="subscriptionID")
    subscription_next_billing_date: Optional[Any] = Field(
        alias="subscriptionNextBillingDate",
    )  # TODO unsure what this returns
    subscription_remaining_days: int = Field(alias="subscriptionRemainingDays")
    subscription_remaining_term: Optional[Any] = Field(
        alias="subscriptionRemainingTerm",
    )  # TODO unsure what this returns
    subscription_start_date: date = Field(alias="subscriptionStartDate")
    subscription_term: str = Field(alias="subscriptionTerm")
    term: int
    term_unit: str = Field(alias="termUnit")
    type: str


class _RemoteServiceCapabilitiesModel(BaseModel):
    acsetting_enabled: bool = Field(alias="acsettingEnabled")
    allow_hvac_override_capable: bool = Field(alias="allowHvacOverrideCapable")
    dlock_unlock_capable: bool = Field(alias="dlockUnlockCapable")
    estart_enabled: bool = Field(alias="estartEnabled")
    estart_stop_capable: bool = Field(alias="estartStopCapable")
    estop_enabled: bool = Field(alias="estopEnabled")
    guest_driver_capable: bool = Field(alias="guestDriverCapable")
    hazard_capable: bool = Field(alias="hazardCapable")
    head_light_capable: bool = Field(alias="headLightCapable")
    moon_roof_capable: bool = Field(alias="moonRoofCapable")
    power_window_capable: bool = Field(alias="powerWindowCapable")
    steering_wheel_heater_capable: bool = Field(alias="steeringWheelHeaterCapable")
    trunk_capable: bool = Field(alias="trunkCapable")
    vehicle_finder_capable: bool = Field(alias="vehicleFinderCapable")
    ventilator_capable: bool = Field(alias="ventilatorCapable")


class _DataConsentModel(BaseModel):
    can_300: bool = Field(alias="can300")
    dealer_contact: bool = Field(alias="dealerContact")
    service_connect: bool = Field(alias="serviceConnect")
    ubi: bool = Field(alias="ubi")


class _FeaturesModel(BaseModel):
    ach_payment: bool = Field(alias="achPayment")
    add_service_record: bool = Field(alias="addServiceRecord")
    auto_drive: bool = Field(alias="autoDrive")
    cerence: bool = Field(alias="cerence")
    charging_station: bool = Field(alias="chargingStation")
    climate_start_engine: bool = Field(alias="climateStartEngine")
    collision_assistance: bool = Field(alias="collisionAssistance")
    connected_card: bool = Field(alias="connectedCard")
    connected_insurance: bool = Field(alias="connectedInsurance")
    connected_support: bool = Field(alias="connectedSupport")
    crash_notification: bool = Field(alias="crashNotification")
    critical_alert: bool = Field(alias="criticalAlert")
    dashboard_lights: bool = Field(alias="dashboardLights")
    dealer_appointment: bool = Field(alias="dealerAppointment")
    digital_key: bool = Field(alias="digitalKey")
    door_lock_capable: bool = Field(alias="doorLockCapable")
    drive_pulse: bool = Field(alias="drivePulse")
    driver_companion: bool = Field(alias="driverCompanion")
    driver_score: bool = Field(alias="driverScore")
    dtc_access: bool = Field(alias="dtcAccess")
    dynamic_navi: bool = Field(alias="dynamicNavi")
    eco_history: bool = Field(alias="ecoHistory")
    eco_ranking: bool = Field(alias="ecoRanking")
    electric_pulse: bool = Field(alias="electricPulse")
    emergency_assist: bool = Field(alias="emergencyAssist")
    enhanced_security_system: bool = Field(alias="enhancedSecuritySystem")
    ev_charge_station: bool = Field(alias="evChargeStation")
    ev_remote_services: bool = Field(alias="evRemoteServices")
    ev_vehicle_status: bool = Field(alias="evVehicleStatus")
    financial_services: bool = Field(alias="financialServices")
    flex_rental: bool = Field(alias="flexRental")
    h2_fuel_station: bool = Field(alias="h2FuelStation")
    home_charge: bool = Field(alias="homeCharge")
    how_to_videos: bool = Field(alias="howToVideos")
    hybrid_pulse: bool = Field(alias="hybridPulse")
    hydrogen_pulse: bool = Field(alias="hydrogenPulse")
    important_message: bool = Field(alias="importantMessage")
    insurance: bool = Field(alias="insurance")
    last_parked: bool = Field(alias="lastParked")
    lcfs: bool = Field(alias="lcfs")
    linked_accounts: bool = Field(alias="linkedAccounts")
    maintenance_timeline: bool = Field(alias="maintenanceTimeline")
    marketing_card: bool = Field(alias="marketingCard")
    marketing_consent: bool = Field(alias="marketingConsent")
    master_consent_editable: bool = Field(alias="masterConsentEditable")
    my_destination: bool = Field(alias="myDestination")
    owners_manual: bool = Field(alias="ownersManual")
    paid_product: bool = Field(alias="paidProduct")
    parked_vehicle_locator: bool = Field(alias="parkedVehicleLocator")
    parking: bool = Field(alias="parking")
    parking_notes: bool = Field(alias="parkingNotes")
    personalized_settings: bool = Field(alias="personalizedSettings")
    privacy: bool = Field(alias="privacy")
    recent_trip: bool = Field(alias="recentTrip")
    remote_dtc: bool = Field(alias="remoteDtc")
    remote_parking: bool = Field(alias="remoteParking")
    remote_service: bool = Field(alias="remoteService")
    roadside_assistance: bool = Field(alias="roadsideAssistance")
    safety_recall: bool = Field(alias="safetyRecall")
    schedule_maintenance: bool = Field(alias="scheduleMaintenance")
    service_history: bool = Field(alias="serviceHistory")
    shop_genuine_parts: bool = Field(alias="shopGenuineParts")
    smart_charging: bool = Field(alias="smartCharging")
    ssa_download: bool = Field(alias="ssaDownload")
    sxm_radio: bool = Field(alias="sxmRadio")
    telemetry: bool = Field(alias="telemetry")
    tff: bool = Field(alias="tff")
    tire_pressure: bool = Field(alias="tirePressure")
    v1g: bool = Field(alias="v1g")
    va_setting: bool = Field(alias="vaSetting")
    vehicle_diagnostic: bool = Field(alias="vehicleDiagnostic")
    vehicle_health_report: bool = Field(alias="vehicleHealthReport")
    vehicle_specifications: bool = Field(alias="vehicleSpecifications")
    vehicle_status: bool = Field(alias="vehicleStatus")
    we_hybrid: bool = Field(alias="weHybrid")
    wifi: bool = Field(alias="wifi")
    xcapp: bool = Field(alias="xcapp")


class VehicleGuidModel(BaseModel):
    """Model representing a vehicle with its associated information.

    Attributes
    ----------
        alerts (List[Any]): The alerts associated with the vehicle.
        asiCode (str): The ASI code of the vehicle.
        brand (str): The brand of the vehicle.
        capabilities (List[_CapabilitiesModel]): The capabilities of the vehicle.
        car_line_name (str): The name of the car line.
        color (str): The color of the vehicle.
        commercial_rental (bool): Indicates if the vehicle is used for commercial rental.
        contract_id (str): The contract ID of the vehicle.
        cts_links (_LinksModel): The CTS (Connected Technologies Services) links of the vehicle.
        data_consent (_DataConsentModel): The data consent information of the vehicle.
        date_of_first_use (Optional[date]): The date of first use of the vehicle.
        dcm (_DcmModel): The DCM (Data Communication Module) information of the vehicle.
        dcm_active (bool): Indicates if the DCM is active for the vehicle.
        dcms (Optional[Any]): The DCMS (Data Communication Module Status) information
            of the vehicle.
        display_model_description (str): The description of the displayed model.
        display_subscriptions (List[Dict[str, str]]): The displayed subscriptions of the vehicle.
        electrical_platform_code (str): The electrical platform code of the vehicle.
        emergency_contact (Optional[Any]): The emergency contact information of the vehicle.
        ev_vehicle (bool): Indicates if the vehicle is an electric vehicle.
        extended_capabilities (_ExtendedCapabilitiesModel): The extended capabilities
            of the vehicle.
        external_subscriptions (Optional[Any]): The external subscriptions of the vehicle.
        family_sharing (bool): Indicates if the vehicle is part of a family sharing plan.
        faq_url (str): The URL of the FAQ (Frequently Asked Questions) for the vehicle.
        features (_FeaturesModel): The features of the vehicle.
        fleet_ind (Optional[Any]): The fleet indicator of the vehicle.
        generation (str): The generation of the vehicle.
        head_unit (_HeadUnitModel): The head unit information of the vehicle.
        hw_type (Optional[Any]): The hardware type of the vehicle.
        image (str): The image URL of the vehicle.
        imei (str): The IMEI (International Mobile Equipment Identity) of the vehicle.
        katashiki_code (str): The katashiki code of the vehicle.
        manufactured_date (date): The manufactured date of the vehicle.
        manufactured_code (str): The manufacturer code of the vehicle.
        car_model_code (str): The model code of the vehicle.
        car_model_description (str): The description of the model of the vehicle.
        car_model_name (str): The name of the model of the vehicle.
        car_model_year (str): The model year of the vehicle.
        nickname (Optional[str]): The nickname of the vehicle.
        non_cvt_vehicle (bool): Indicates if the vehicle is a non-CVT
            (Continuously Variable Transmission) vehicle.
        old_imei (Optional[Any]): The old IMEI of the vehicle.
        owner (bool): Indicates if the user is the owner of the vehicle.
        personalized_settings (_LinksModel): The personalized settings of the vehicle.
        preferred (Optional[bool]): Indicates if the vehicle is the preferred vehicle.
        primary_subscriber (bool): Indicates if the user is the primary subscriber of the vehicle.
        region (str): The region of the vehicle.
        registration_number (Optional[str]): The registration number of the vehicle.
        remote_display (Optional[Any]): The remote display information of the vehicle.
        remote_service_capabilities (_RemoteServiceCapabilitiesModel): The remote
            service capabilities of the vehicle.
        remote_service_exceptions (List[Any]): The remote service exceptions of the vehicle.
        remote_subscription_exists (bool): Indicates if a remote subscription
            exists for the vehicle.
        remote_subscription_status (str): The remote subscription status of the vehicle.
        remote_user (bool): Indicates if the user is a remote user of the vehicle.
        remote_user_guid (Optional[Union[UUID, str]]): The remote user GUID
            (Globally Unique Identifier) of the vehicle.
        service_connect_status (Optional[Any]): The service connect status of the vehicle.
        services (List[Any]): The services associated with the vehicle.
        shop_genuine_parts_url (str): The URL for shopping genuine parts for the vehicle.
        status (str): The status of the vehicle.
        stock_pic_reference (str): The stock picture reference of the vehicle.
        subscriber_guid (UUID): The subscriber GUID of the vehicle.
        subscription_expiration_status (bool): Indicates if the subscription
            is expired for the vehicle.
        subscription_status (str): The subscription status of the vehicle.
        subscriptions (List[_SubscriptionsModel]): The subscriptions associated with the vehicle.
        suffix_code (Optional[Any]): The suffix code of the vehicle.
        svl_satus (bool): Indicates the SVL (Smart Vehicle Link) status of the vehicle.
        tff_links (_LinksModel): The TFF (Toyota Friend Finder) links of the vehicle.
        transmission_type (str): The transmission type of the vehicle.
        vehicle_capabilities (List[Any]): The capabilities of the vehicle.
        vehicle_data_consents (Optional[Any]): The vehicle data consents of the vehicle.
        vin (str): The VIN (Vehicle Identification Number) of the vehicle.
    """

    alerts: List[Any]  # TODO unsure what this returns
    asi_code: str = Field(alias="asiCode")
    brand: str
    capabilities: List[_CapabilitiesModel]
    car_line_name: str = Field(alias="carlineName")
    color: str
    commercial_rental: bool = Field(alias="commercialRental")
    contract_id: str = Field(alias="contractId")
    cts_links: _LinksModel = Field(alias="ctsLinks")
    data_consent: _DataConsentModel = Field(alias="dataConsent")
    date_of_first_use: Optional[date] = Field(alias="dateOfFirstUse")
    dcm: Optional[_DcmModel] = None
    dcm_active: bool = Field(alias="dcmActive")
    dcms: Optional[Any]  # TODO unsure what this returns
    display_model_description: str = Field(alias="displayModelDescription")
    display_subscriptions: List[Dict[str, str]] = Field(alias="displaySubscriptions")
    electrical_platform_code: Optional[str] = Field(alias="electricalPlatformCode", default=None)
    emergency_contact: Optional[Any] = Field(
        alias="emergencyContact"
    )  # TODO unsure what this returns
    ev_vehicle: bool = Field(alias="evVehicle")
    extended_capabilities: _ExtendedCapabilitiesModel = Field(alias="extendedCapabilities")
    external_subscriptions: Optional[Any] = Field(alias="externalSubscriptions")
    family_sharing: bool = Field(alias="familySharing")
    faq_url: str = Field(alias="faqUrl")
    features: _FeaturesModel
    fleet_ind: Optional[Any] = Field(alias="fleetInd")  # TODO unsure what this returns
    fuel_type: Optional[str] = Field(alias="fuelType", default=None)
    generation: str
    head_unit: _HeadUnitModel = Field(alias="headUnit")
    hw_type: Optional[Any] = Field(alias="hwType")  # TODO unsure what this returns
    image: str
    imei: Optional[str] = None
    katashiki_code: str = Field(alias="katashikiCode")
    manufactured_date: date = Field(alias="manufacturedDate")
    manufactured_code: str = Field(alias="manufacturerCode")
    car_model_code: str = Field(alias="modelCode")
    car_model_description: str = Field(alias="modelDescription")
    car_model_name: str = Field(alias="modelName")
    car_model_year: str = Field(alias="modelYear")
    nickname: Optional[str] = Field(alias="nickName", default=None)
    non_cvt_vehicle: bool = Field(alias="nonCvtVehicle")
    old_imei: Optional[Any] = Field(alias="oldImei")  # TODO unsure what this returns
    owner: bool
    personalized_settings: _LinksModel = Field(
        alias="personalizedSettings"
    )  # TODO unsure what this returns
    preferred: Optional[bool] = None
    primary_subscriber: bool = Field(alias="primarySubscriber")
    region: str
    registration_number: Optional[str] = Field(alias="registrationNumber")
    remote_display: Optional[Any] = Field(alias="remoteDisplay")  # TODO unsure what this returns
    remote_service_capabilities: _RemoteServiceCapabilitiesModel = Field(
        alias="remoteServiceCapabilities"
    )
    remote_service_exceptions: List[Any] = Field(
        alias="remoteServicesExceptions"
    )  # TODO unsure what this returns
    remote_subscription_exists: bool = Field(alias="remoteSubscriptionExists")
    remote_subscription_status: str = Field(alias="remoteSubscriptionStatus")
    remote_user: bool = Field(alias="remoteUser")
    remote_user_guid: Optional[Union[UUID, str]] = Field(alias="remoteUserGuid", default=None)
    service_connect_status: Optional[Any] = Field(
        alias="serviceConnectStatus"
    )  # TODO unsure what this returns
    services: List[Any]  # TODO unsure what this returns
    shop_genuine_parts_url: str = Field(alias="shopGenuinePartsUrl")
    status: str
    stock_pic_reference: str = Field(alias="stockPicReference")
    subscriber_guid: UUID = Field(alias="subscriberGuid")
    subscription_expiration_status: bool = Field(alias="subscriptionExpirationStatus")
    subscription_status: str = Field(alias="subscriptionStatus")
    subscriptions: List[_SubscriptionsModel]
    suffix_code: Optional[Any] = Field(alias="suffixCode")
    svl_satus: bool = Field(alias="svlStatus")
    tff_links: _LinksModel = Field(alias="tffLinks")
    transmission_type: str = Field(alias="transmissionType")
    vehicle_capabilities: List[Any] = Field(alias="vehicleCapabilities")
    vehicle_data_consents: Optional[Any] = Field(alias="vehicleDataConsents")
    vin: str


class VehiclesResponseModel(StatusModel):
    r"""Model representing a vehicles response.

    Inherits from StatusModel.

    Attributes
    ----------
        payload (Optional[List[VehicleGuidModel]], optional): The vehicles payload. \n
            Defaults to None.

    """

    payload: Optional[List[VehicleGuidModel]] = None
