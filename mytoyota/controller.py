"""Toyota Connected Services Controller."""

import contextlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict, Optional
from urllib import parse

import hishel
import httpx
import jwt

from mytoyota.const import (
    ACCESS_TOKEN_URL,
    API_BASE_URL,
    AUTHENTICATE_URL,
    AUTHORIZE_URL,
)
from mytoyota.exceptions import (
    ToyotaApiError,
    ToyotaInternalError,
    ToyotaInvalidUsernameError,
    ToyotaLoginError,
)
from mytoyota.utils.log_utils import format_httpx_response

_LOGGER: logging.Logger = logging.getLogger(__name__)


class TokenStorage(ABC):
    """Abstract base class for token storage implementations."""

    @abstractmethod
    async def load_tokens(self, username: str) -> Dict[str, Any]:
        """Load tokens for given username."""
        pass

    @abstractmethod
    async def save_tokens(self, username: str, token_data: Dict[str, Any]) -> None:
        """Save tokens for given username."""
        pass


class MemoryTokenStorage(TokenStorage):
    """In-memory implementation of token storage.

    This class provides a simple in-memory storage solution for managing
    user tokens. It allows for loading and saving tokens associated
    with a specific username.
    """

    def __init__(self):
        """Initialize the MemoryTokenStorage instance.

        This constructor initializes an empty dictionary to store token
        data, where the keys are usernames and the values are dictionaries
        containing token information.
        """
        self._storage: Dict[str, Dict[str, Any]] = {}

    async def load_tokens(self, username: str) -> Dict[str, Any]:
        """Load tokens for a specified username.

        Args:
        ----
            username (str): The username for which to load token data.

        Returns:
        -------
            Dict[str, Any]: A dictionary containing the token data for
            the specified username. If no tokens are found, an empty
            dictionary is returned.

        """
        return self._storage.get(username, {})

    async def save_tokens(self, username: str, token_data: Dict[str, Any]) -> None:
        """Save token data for a specified username.

        Args:
        ----
            username (str): The username for which to save token data.
            token_data (Dict[str, Any]): A dictionary containing the token
            data to be stored for the specified username.

        Returns:
        -------
            None: This method does not return any value.

        """
        self._storage[username] = token_data


class Controller:
    """Controller class."""

    def __init__(  # noqa: PLR0913
        self,
        username: str,
        password: str,
        token_storage: Optional[TokenStorage] = None,
        timeout: int = 60,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Initialise Controller class."""
        self._username: str = username
        self._password: str = password
        self._token: Optional[str] = None
        self._token_expiration: Optional[datetime] = None
        self._refresh_token: Optional[str] = None
        self._uuid: Optional[str] = None
        self._timeout = timeout
        self._token_storage = token_storage or MemoryTokenStorage()
        self._client = client or httpx.AsyncClient(timeout=timeout)

        # Base URLs
        self._api_base_url = httpx.URL(API_BASE_URL)
        self._access_token_url = httpx.URL(ACCESS_TOKEN_URL)
        self._authenticate_url = httpx.URL(AUTHENTICATE_URL)
        self._authorize_url = httpx.URL(AUTHORIZE_URL)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()

    async def _load_cached_tokens(self) -> None:
        """Load cached tokens if available."""
        cached_data = await self._token_storage.load_tokens(self._username)
        if cached_data:
            self._token = cached_data.get("access_token")
            self._refresh_token = cached_data.get("refresh_token")
            self._uuid = cached_data.get("uuid")
            if expiration := cached_data.get("expiration"):
                self._token_expiration = datetime.fromisoformat(expiration)

    async def login(self) -> None:
        """Perform first login."""
        await self._load_cached_tokens()
        if not self._is_token_valid():
            await self._update_token()

    async def _update_token(self) -> None:
        """Login to toyota servers and retrieve token and uuid for the account."""
        if not self._is_token_valid():
            if self._refresh_token:
                with contextlib.suppress(ToyotaLoginError):
                    await self._refresh_tokens()
                    return
            await self._authenticate()

    async def _authenticate(self):
        """Authenticate with username and password."""
        _LOGGER.debug("Authenticating")

        data: Dict[str, Any] = {}
        token_id: Optional[str] = None

        async with hishel.AsyncCacheClient() as auth_client:
            for _ in range(10):
                if "callbacks" in data:
                    self._handle_callbacks(data["callbacks"])

                resp = await auth_client.post(self._authenticate_url, json=data)
                _LOGGER.debug(format_httpx_response(resp))

                if resp.status_code != HTTPStatus.OK:
                    raise ToyotaLoginError(
                        f"Authentication Failed. {resp.status_code}, {resp.text}."
                    )

                data = resp.json()
                if "tokenId" in data:
                    token_id = data["tokenId"]
                    break

            if not token_id:
                raise ToyotaLoginError("Authentication Failed. Unknown method.")

            # Authorization step
            auth_code = await self._get_authorization_code(auth_client, token_id)

            # Token retrieval
            tokens = await self._retrieve_tokens(auth_client, auth_code)
            await self._update_tokens(tokens)

    def _handle_callbacks(self, callbacks: list) -> None:
        """Handle authentication callbacks."""
        for cb in callbacks:
            if cb["type"] == "NameCallback" and cb["output"][0]["value"] == "User Name":
                cb["input"][0]["value"] = self._username
            elif cb["type"] == "PasswordCallback":
                cb["input"][0]["value"] = self._password
            elif (
                cb["type"] == "TextOutputCallback" and cb["output"][0]["value"] == "User Not Found"
            ):
                raise ToyotaInvalidUsernameError("Authentication Failed. User Not Found.")

    async def _get_authorization_code(self, client: hishel.AsyncCacheClient, token_id: str) -> str:
        """Get authorization code."""
        resp = await client.get(
            self._authorize_url,
            headers={"cookie": f"iPlanetDirectoryPro={token_id}"},
        )
        _LOGGER.debug(format_httpx_response(resp))

        if resp.status_code != HTTPStatus.FOUND:
            raise ToyotaLoginError(f"Authorization failed. {resp.status_code}, {resp.text}.")

        return parse.parse_qs(httpx.URL(resp.headers.get("location")).query.decode())["code"]

    async def _retrieve_tokens(
        self, client: hishel.AsyncCacheClient, auth_code: str
    ) -> Dict[str, Any]:
        """Retrieve access and refresh tokens."""
        resp = await client.post(
            self._access_token_url,
            headers={"authorization": "basic b25lYXBwOm9uZWFwcA=="},
            data={
                "client_id": "oneapp",
                "code": auth_code,
                "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
                "grant_type": "authorization_code",
                "code_verifier": "plain",
            },
        )
        _LOGGER.debug(format_httpx_response(resp))

        if resp.status_code != HTTPStatus.OK:
            raise ToyotaLoginError(f"Token retrieval failed. {resp.status_code}, {resp.text}.")

        return resp.json()

    async def _update_tokens(self, tokens: Dict[str, Any]) -> None:
        """Update tokens and store them."""
        if not all(
            key in tokens for key in ["access_token", "id_token", "refresh_token", "expires_in"]
        ):
            raise ToyotaLoginError("Token retrieval failed. Missing Tokens.")

        self._token = tokens["access_token"]
        self._refresh_token = tokens["refresh_token"]
        self._uuid = jwt.decode(
            tokens["id_token"],
            algorithms=["RS256"],
            options={"verify_signature": False},
            audience="oneappsdkclient",
        )["uuid"]
        self._token_expiration = datetime.now() + timedelta(seconds=tokens["expires_in"])

        # Store tokens
        await self._token_storage.save_tokens(
            self._username,
            {
                "access_token": self._token,
                "refresh_token": self._refresh_token,
                "uuid": self._uuid,
                "expiration": str(self._token_expiration),
            },
        )

    def _is_token_valid(self) -> bool:
        """Check if token is valid."""
        if self._token is None or self._token_expiration is None:
            return False

        return self._token_expiration > datetime.now()

    async def _refresh_tokens(self) -> None:
        async with hishel.AsyncCacheClient() as client:
            resp = await client.post(
                self._access_token_url,
                headers={"authorization": "basic b25lYXBwOm9uZWFwcA=="},
                data={
                    "client_id": "oneapp",
                    "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
                    "grant_type": "refresh_token",
                    "code_verifier": "plain",
                    "refresh_token": self._refresh_token,
                },
            )
            _LOGGER.debug(format_httpx_response(resp))

            if resp.status_code != HTTPStatus.OK:
                raise ToyotaLoginError(f"Token refresh failed. {resp.status_code}, {resp.text}.")

            await self._update_tokens(resp.json())

    async def request_raw(  # noqa: PLR0913
        self,
        method: str,
        endpoint: str,
        vin: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make a raw request to the API."""
        if method not in ("GET", "POST", "PUT", "DELETE"):
            raise ToyotaInternalError("Invalid request method provided")

        if not self._is_token_valid():
            await self._update_token()

        request_headers = {
            "x-api-key": "tTZipv6liF74PwMfk9Ed68AQ0bISswwf3iHQdqcF",
            "x-guid": self._uuid,
            "guid": self._uuid,
            "authorization": f"Bearer {self._token}",
            "x-channel": "ONEAPP",
            "x-brand": "T",
            "user-agent": "okhttp/4.10.0",
        }

        if headers:
            request_headers.update(headers)
        if vin:
            request_headers["vin"] = vin

        response = await self._client.request(
            method,
            f"{self._api_base_url}{endpoint}",
            headers=request_headers,
            json=body,
            params=params,
            follow_redirects=True,
        )
        _LOGGER.debug(format_httpx_response(response))

        if response.status_code in [HTTPStatus.OK, HTTPStatus.ACCEPTED]:
            return response

        raise ToyotaApiError(f"Request Failed. {response.status_code}, {response.text}.")

    async def request_json(  # noqa: PLR0913
        self,
        method: str,
        endpoint: str,
        vin: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a JSON request to the specified endpoint.

        Args:
        ----
            method (str): The HTTP method to use for the request.
            endpoint (str): The endpoint to send the request to.
            vin (Optional[str], optional): The VIN (Vehicle Identification Number) to include
                in the request. Defaults to None.
            body (Optional[Dict[str, Any]], optional): The JSON body to include in the request.
                Defaults to None.
            params (Optional[Dict[str, Any]], optional): The query parameters to
                include in the request. Defaults to None.
            headers (Optional[Dict[str, Any]], optional): The headers to include in the request.
                Defaults to None.

        Returns:
        -------
            The JSON response from the request.

        Examples:
        --------
            response = await request_json("GET", "/cars", vin="1234567890")

        """
        response = await self.request_raw(method, endpoint, vin, body, params, headers)
        return response.json()
