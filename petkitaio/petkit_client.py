"""Python API for PetKit Devices"""
from __future__ import annotations

import base64
from typing import Any
import asyncio
from datetime import datetime, timedelta
from itertools import chain
import json
import logging
import urllib.parse as urlencode

from aiohttp import ClientResponse, ClientSession
import hashlib
from tzlocal import get_localzone_name

from petkitaio.constants import (
    AUTH_ERROR_CODES,
    BLE_HEADER,
    BLUETOOTH_ERRORS,
    CLIENT_DICT,
    Endpoint,
    FeederCommand,
    FEEDER_LIST,
    FeederSetting,
    Header,
    LB_CMD_TO_KEY,
    LB_CMD_TO_TYPE,
    LB_CMD_TO_VALUE,
    LitterBoxCommand,
    LitterBoxSetting,
    LITTER_LIST,
    PetSetting,
    PurifierCommand,
    PUR_CMD_TO_KEY,
    PUR_CMD_TO_TYPE,
    PUR_CMD_TO_VALUE,
    PURIFIER_LIST,
    PurifierSetting,
    Region,
    SERVER_ERROR_CODES,
    TIMEOUT,
    WATER_FOUNTAIN_LIST,
    W5Command,
    W5_COMMAND_TO_CODE,
    W5_DND_COMMANDS,
    W5_LIGHT_BRIGHTNESS,
    W5_LIGHT_POWER,
    W5_SETTINGS_COMMANDS,
)
from petkitaio.exceptions import (AuthError, BluetoothError, PetKitError, RegionError, ServerError, TimezoneError)
from petkitaio.model import (Feeder, LitterBox, Pet, PetKitData, Purifier, W5Fountain)

LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """PetKit client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession | None = None,
        region: str = None,
        timezone: str = None,
        timeout: int = TIMEOUT
    ) -> None:
        """Initialize PetKit Client.

        username: PetKit username/email
        password: PetKit account password
        session: aiohttp.ClientSession or None to create a new session
        region: See available regions in Documentation
        timezone: automatically obtained from system if not specified
        """

        # Catch if a user failed to define a region
        if region is None:
            raise RegionError('A region must be specified in order to log into your PetKit account.')

        self.username: str = username
        self.password: str = password
        self.region: str = region
        self.base_url: str = ''
        self.servers_dict: dict = {}
        self._session: ClientSession = session if session else ClientSession()
        self.tz: str = get_localzone_name() if timezone is None else timezone
        self.timeout: int = timeout
        self.token: str | None = None
        self.token_expiration: datetime | None = None
        self.user_id: str | None = None
        self.use_ble_relay: bool = True
        self.ble_sequence: int = 0
        self.manually_paused: dict[int, bool] = {}
        self.manual_pause_end: dict[int, datetime | None] = {}
        self.last_manual_feed_id: dict[int, str | None] = {}
        self.last_ble_poll: dict[int, datetime | None]  = {}
        self.group_ids: set[int] = set()
        self.missing_relay_log_count: dict[int, int] = {}

    async def get_api_server_list(self) -> None:
        """Fetches a list of all api urls categorized by region."""

        url = 'https://passport.petkt.com/6/account/regionservers'

        headers = {
            'Accept': Header.ACCEPT,
            'Accept-Language': Header.ACCEPT_LANG,
            'Accept-Encoding': Header.ENCODING,
            'X-Api-Version': Header.API_VERSION,
            'Content-Type': Header.CONTENT_TYPE,
            'User-Agent': Header.AGENT,
            'X-Client': Header.CLIENT,
        }
        data = {}
        response = await self._post(url, headers, data)
        server_list = response['result']['list']
        for region in server_list:
            self.servers_dict[region["name"]] = {
                "id": region["id"],
                "url": region["gateway"]
            }

    async def login(self) -> None:

        await self.get_api_server_list()
        # Determine the user's base URL
        if self.region == "China":
            self.base_url = Region.CN
        elif self.region in self.servers_dict:
            self.base_url = self.servers_dict[self.region]["url"]
        else:
            raise RegionError('Region specified is not a valid region.')

        login_url = f'{self.base_url}{Endpoint.LOGIN}'

        headers = {
            'Accept': Header.ACCEPT,
            'Accept-Language': Header.ACCEPT_LANG,
            'Accept-Encoding': Header.ENCODING,
            'X-Api-Version': Header.API_VERSION,
            'Content-Type': Header.CONTENT_TYPE,
            'User-Agent': Header.AGENT,
            'X-Client': Header.CLIENT,
        }

        data = {
            'client': str(CLIENT_DICT),
            'encrypt': '1',
            'oldVersion': Header.API_VERSION,
            'password': hashlib.md5(self.password.encode()).hexdigest(),
            'region': self.servers_dict[self.region]["id"],
            'username': self.username
        }
        LOGGER.debug(
            f'Logging in at {login_url} with region {self.region}'
        )
        response = await self._post(login_url, headers, data)
        self.user_id = response['result']['session']['userId']
        self.token = response['result']['session']['id']
        self.token_expiration = datetime.now() + timedelta(seconds=response['result']['session']['expiresIn'])
        ## Obtain all group IDs
        await self.get_group_ids()

    async def get_group_ids(self) -> None:
        """Grab groups (families) the account is associated with
        which will be used to grab device rosters.
        """

        families_url = f'{self.base_url}{Endpoint.FAMILY_LIST}'
        header = await self.create_header()
        data = {}
        LOGGER.debug(f'Grabbing group IDs at {families_url}')
        groups = await self._post(families_url, header, data)
        for group in groups['result']:
            self.group_ids.add(group['groupId'])
        LOGGER.debug(f'Found the following group IDs: {self.group_ids}')

    async def check_token(self) -> None:
        """Check to see if there is a valid token or if token is about to expire.
        If there is no token, a new token is obtained. In addition,
        if the current token is about to expire within 60 minutes
        or has already expired, a new token is obtained.
        """

        current_dt = datetime.now()
        if (self.token or self.token_expiration) is None:
            await self.login()
        elif (self.token_expiration-current_dt).total_seconds() < 3600:
            LOGGER.debug('Token expired. Obtaining new token.')
            await self.login()
        else:
            return None

    async def create_header(self) -> dict[str, str]:
        """Create header for interaction with devices."""

        if self.tz is None:
            raise TimezoneError("Unable to find the TZ environmental variable on the OS")
        header = {
            'X-Session': self.token,
            'F-Session': self.token,
            'Accept': Header.ACCEPT,
            'Accept-Language': Header.ACCEPT_LANG,
            'Accept-Encoding': Header.ENCODING,
            'X-Api-Version': Header.API_VERSION,
            'Content-Type': Header.CONTENT_TYPE,
            'User-Agent': Header.AGENT,
            'X-Client': Header.CLIENT,
            'X-TimezoneId': self.tz,
        }
        return header

    async def get_device_rosters(self) -> dict[int, Any]:
        """Fetch device roster endpoint to get all available devices."""

        await self.check_token()
        url = f'{self.base_url}{Endpoint.DEVICE_ROSTER}'
        header = await self.create_header()
        device_rosters = {}
        LOGGER.debug(f'Fetching device rosters at {url}')
        for group_id in self.group_ids:
            data = {
                'day': str(datetime.now().date()).replace('-', ''),
                'groupId': group_id
            }
            device_roster = await self._post(url, header, data)
            device_rosters[group_id] = device_roster
        LOGGER.debug(
            f'Found the following device rosters:\n'
            f'{json.dumps(device_rosters, indent=4)}'
        )
        return device_rosters

    async def get_petkit_data(self) -> PetKitData:
        """Fetch data for all PetKit devices."""

        device_rosters = await self.get_device_rosters()
        fountains_data: dict[int, W5Fountain] = {}
        feeders_data: dict[int, Feeder] = {}
        litter_boxes_data: dict[int, LitterBox] = {}
        purifiers_data: dict[int, Purifier] = {}
        header = await self.create_header()

        for group_id in device_rosters:
            device_roster = device_rosters[group_id]
            LOGGER.debug(
                f'Parsing device roster for group ID {group_id}:\n'
                f'{json.dumps(device_roster, indent = 4)}'
            )
            group_has_relay: bool = False
            if 'hasRelay' in device_roster['result']:
                group_has_relay = device_roster['result']['hasRelay']

            devices = device_roster['result']['devices']
            LOGGER.debug(
                f'Found the following PetKit devices in family:\n'
                f'{json.dumps(devices, indent = 4)}'
            )
            if devices:
                for device in devices:
                    # W5 Water Fountain
                    if device['type'] in WATER_FOUNTAIN_LIST:
                        wf_instance, wf_id = await self._handle_water_fountain(device=device, has_relay=group_has_relay, header=header)
                        fountains_data[wf_id] = wf_instance

                    # Feeders
                    if device['type'] in FEEDER_LIST:
                        feeder_instance, feeder_id = await self._handle_feeder(device=device, header=header)
                        feeders_data[feeder_id] = feeder_instance

                    # Litter Boxes
                    if device['type'] in LITTER_LIST:
                        litter_box_instance, litter_box_id = await self._handle_litter_box(device=device, header=header)
                        litter_boxes_data[litter_box_id] = litter_box_instance

                    # Purifiers
                    if device['type'] in PURIFIER_LIST:
                        purifier_instance, purifier_id = await self._handle_purifier(device=device, header=header)
                        purifiers_data[purifier_id] = purifier_instance

        # Pets
        pets_data = await self._handle_pets(header=header)
        LOGGER.debug('PetKitData instance creation successful')
        return PetKitData(
            user_id=self.user_id,
            feeders=feeders_data,
            litter_boxes=litter_boxes_data,
            water_fountains=fountains_data,
            pets=pets_data,
            purifiers=purifiers_data
        )

    async def _handle_water_fountain(self, device: dict[str, Any], has_relay: bool, header: dict[str, str]) -> (W5Fountain, int):
        """Handle parsing water fountain and initiating BLE relay connection."""

        device_type: str = device['type'].lower()
        fountain_data: dict[str, Any] = {}
        relay_tc: int = 14
        wf_url = f'{self.base_url}{Endpoint.W5}'
        data = {
            'id': device['id']
        }
        # Set missing relay log count to 0 during first run
        if device['id'] not in self.missing_relay_log_count:
            self.missing_relay_log_count[device['id']] = 0

        if has_relay and self.use_ble_relay:
            # Reset log count to 0 in case relay becomes available
            self.missing_relay_log_count[device['id']] = 0
            current_dt = datetime.now()
            ### Only initiate BLE relay if 7 minutes have elapsed since the last time the relay was initiated.
            ### This helps prevent some devices, such as the Pura Max, from locking up (i.e., doesn't
            ### automatically cycle after cat usage) if they are asked to initiate the BLE relay too frequently.
            can_poll: bool = False
            if device['id'] not in self.last_ble_poll:
                can_poll = True
            else:
                LOGGER.debug(
                    f'Water fountain({device["id"]}) - Last successful BLE '
                    f'relay polling: {self.last_ble_poll[device["id"]]}'
                )
                if (current_dt-self.last_ble_poll[device['id']]).total_seconds() >= 420:
                    can_poll = True
                else:
                    can_poll = False
            if can_poll:
                LOGGER.debug(f'Polling water fountain({device["id"]}) via BLE relay')
                ble_connect_attempt: int = 1
                ble_poll_attempt: int = 1
                main_online: bool = False
                ble_url = f'{self.base_url}{Endpoint.BLE_DEVICES}'
                conn_url = f'{self.base_url}{Endpoint.BLE_CONNECT}'
                poll_url = f'{self.base_url}{Endpoint.BLE_POLL}'
                disconnect_url = f'{self.base_url}{Endpoint.BLE_CANCEL}'
                LOGGER.debug('Fetching associated relay devices')
                relay_devices = await self._post(ble_url, header, data={'groupId': device['groupId'],})
                LOGGER.debug(
                    f'Associated relay devices response:\n'
                    f'{json.dumps(relay_devices, indent = 4)}'
                )
                if relay_devices['result']:
                    ble_available = True
                    for relay_device in relay_devices['result']:
                        if relay_device['pim'] == 1:
                            LOGGER.debug('Main relay device online')
                            main_online = True
                            break
                        else:
                            LOGGER.debug('Main relay device not online')
                            main_online = False

                    if ble_available and main_online:
                        LOGGER.debug(f'Fetching water fountain({device["id"]}) details page at {wf_url}')
                        device_details = await self._post(wf_url, header, data)
                        LOGGER.debug(
                            f'Device details response:\n'
                            f'{json.dumps(device_details, indent = 4)}'
                        )
                        mac = device_details['result']['mac']
                        ble_data = {
                            'bleId': device_details['result']['id'],
                            'mac': mac,
                            'type': relay_tc
                        }
                        LOGGER.debug(
                            f'Starting BLE relay connection for {device_details["result"]["name"]}'
                            f'({device_details["result"]["id"]})'
                        )
                        conn_success = await self.start_ble_connection(conn_url, header, ble_data, ble_connect_attempt)
                        if conn_success:
                            LOGGER.debug(
                                f'BLE relay connection successful for {device_details["result"]["name"]}. '
                                f'Attempting to poll the device now.'
                            )
                            poll_success = await self.poll_ble_connection(poll_url, header, ble_data, ble_poll_attempt)
                            if poll_success:
                                LOGGER.debug(
                                    f'BLE relay polling successful for {device_details["result"]["name"]}. '
                                    f'Sending initial BLE commands.'
                                )
                                # Wait a bit for BLE connection to be established before looking up most recent data
                                await asyncio.sleep(2)
                                # Need to reset ble_sequence if get_petkit_data is being called multiple times without a W5Commmand sent in between
                                # Need to add 1 to the sequence after ble connect and poll are successful
                                if self.ble_sequence != 0:
                                    self.ble_sequence = 0
                                self.ble_sequence += 1
                                try:
                                    await self.initial_ble_commands(device_details, relay_tc)
                                except BluetoothError:
                                    pass
                                finally:
                                    # Remember last time BLE relay was successfully initiated
                                    self.last_ble_poll[device['id']] = datetime.now()
                                    LOGGER.debug(
                                        f'Fetching data for {device_details["result"]["name"]} '
                                        f'at {wf_url}'
                                    )
                                    fountain_data = await self._post(wf_url, header, data)
                                    LOGGER.debug(
                                        f'Water fountain data response:\n'
                                        f'{json.dumps(fountain_data, indent = 4)}'
                                    )
                                    # Make sure to sever the BLE connection after getting updated data
                                    await asyncio.sleep(2)
                                    LOGGER.debug(
                                        f'Disconnecting from relay for water fountain '
                                        f'{device_details["result"]["name"]}'
                                    )
                                    await self._post(disconnect_url, header, ble_data)
                            else:
                                LOGGER.warning(
                                    f'BLE polling to {device_details["result"]["name"]} failed after 4 attempts. Will try again during next refresh.'
                                )
                                # Sever the BLE relay connection if polling attempts fail
                                await asyncio.sleep(2)
                                LOGGER.debug(
                                    f'Disconnecting from relay for water fountain '
                                    f'{device_details["result"]["name"]}'
                                )
                                await self._post(disconnect_url, header, ble_data)
                                fountain_data = device_details
                        else:
                            LOGGER.warning(
                                f'BLE connection to {device_details["result"]["name"]} failed after 4 attempts. Will try again during next refresh.'
                            )
                            fountain_data = device_details

                    if not main_online:
                        LOGGER.warning(
                            f'Unable to use BLE relay: Main relay device is reported as being offline. Fetching latest available data.'
                        )
                        fountain_data = await self._post(wf_url, header, data)
                        LOGGER.debug(
                            f'Water fountain data response:\n'
                            f'{json.dumps(fountain_data, indent=4)}'
                        )
                else:
                    LOGGER.debug(
                        'No associated relay devices found in response. Fetching latest data available from API.'
                    )
                    fountain_data = await self._post(wf_url, header, data)
                    LOGGER.debug(
                        f'Water fountain data response:\n'
                        f'{json.dumps(fountain_data, indent=4)}'
                    )
            else:
                LOGGER.debug(
                    f'Too early to poll again via BLE relay.\n'
                    f'Last Poll: {self.last_ble_poll[device["id"]]}\n'
                    f'Next Poll: {self.last_ble_poll[device["id"]] + timedelta(seconds=420)}\n'
                    f'Fetching latest data available from API.'
                )
                fountain_data = await self._post(wf_url, header, data)
                LOGGER.debug(
                    f'Water fountain data response:\n'
                    f'{json.dumps(fountain_data, indent=4)}'
                )
        else:
            if self.use_ble_relay and self.missing_relay_log_count[device['id']] == 0:
                LOGGER.warning(
                    f'PetKit servers are reporting no PetKit device exists that can act as the BLE relay '
                    f'for the water fountain({device["id"]}).\n'
                    f'    If you DON\'T have a PetKit BLE relay device:\n'
                    f'     * You will not be able to control the water fountain and the most recent data will\n'
                    f'       reflect the last time the PetKit app was used to establish a direct bluetooth connection.\n'
                    f'    If you DO have a PetKit BLE relay device:\n'
                    f'     * PetKit may temporarily be reporting the BLE relay device as not being available.\n'
                    f'       Until the BLE relay device is reported to be available again, you will not be able\n'
                    f'       to control the water fountain and the most recent data will reflect the last time the\n'
                    f'       BLE relay or PetKit app (direct bluetooth connection) was used.'
                )
                # Set the log count so that the message is only logged once if the relay is missing
                # and only once after a relay device becomes unavailable.
                self.missing_relay_log_count[device['id']] = 1
            LOGGER.debug('Fetching latest data available from API.')
            fountain_data = await self._post(wf_url, header, data)
            LOGGER.debug(
                f'Water fountain data response:\n'
                f'{json.dumps(fountain_data, indent=4)}'
            )
        wf_instance = W5Fountain(
            id=fountain_data['result']['id'],
            data=fountain_data['result'],
            type=device_type,
            group_relay=has_relay,
            ble_relay=relay_tc,
        )
        return wf_instance, fountain_data['result']['id']

    async def _handle_feeder(self, device: dict[str, Any], header: dict[str, str]) -> (Feeder, int):
        """Handle parsing feeder data."""

        sound_list: dict[int, str] = {}
        device_type_lower = device["type"].lower()
        feeder_url = f'{self.base_url}{device_type_lower}/{Endpoint.DEVICE_DETAIL}'
        data = {
            'id': device['id']
        }
        LOGGER.debug(
            f'Fetching data for feeder({device["id"]}) at {feeder_url}'
        )
        feeder_data = await self._post(feeder_url, header, data)
        LOGGER.debug(
            f' Feeder data response:\n'
            f'{json.dumps(feeder_data, indent=4)}'
        )
        # Populate the last manual feeding ID for the Gemini(d4s) feeder if it exists
        if feeder_data['result']['id'] in self.last_manual_feed_id:
            last_manual_feed_id = self.last_manual_feed_id[feeder_data['result']['id']]
        else:
            last_manual_feed_id = None

        if device['type'] in ['D3']:
            sound_list[-1] = 'Default'
            sound_url = f'{self.base_url}{device_type_lower}/{Endpoint.SOUND_LIST}'
            sound_data = {
                'deviceId': device['id']
            }
            LOGGER.debug(
                f'Fetching sound list for {feeder_data["result"]["name"]} at {feeder_url}'
            )
            sound_response = await self._post(sound_url, header, sound_data)
            LOGGER.debug(
                f'Sound data response:\n'
                f'{json.dumps(sound_response, indent=4)}'
            )
            result = sound_response['result']
            for sound in result:
                sound_list[sound['id']] = sound['name']

        feeder_instance = Feeder(
            id=feeder_data['result']['id'],
            data=feeder_data['result'],
            type=device_type_lower,
            sound_list=sound_list,
            last_manual_feed_id=last_manual_feed_id
        )
        return feeder_instance, feeder_data['result']['id']

    async def _handle_litter_box(self, device: dict[str, Any], header: dict[str, str]) -> (LitterBox, int):
        """Handle parsing litter box data."""

        ### Fetch device_detail page
        device_type_lower = device["type"].lower()
        dd_url = f'{self.base_url}{device_type_lower}/{Endpoint.DEVICE_DETAIL}'
        dd_data = {
            'id': device['id']
        }
        LOGGER.debug(
            f'Fetching litter box({device["id"]}) device details page at {dd_url}'
        )
        device_detail = await self._post(dd_url, header, dd_data)
        LOGGER.debug(
            f'Litter box data response:\n'
            f'{json.dumps(device_detail, indent=4)}'
        )

        ### Fetch DeviceRecord page
        dr_url = f'{self.base_url}{device_type_lower}/{Endpoint.DEVICE_RECORD}'
        if device['type'] == 'T4':
            date_key = 'date'
        else:
            date_key = 'day'
        dr_data = {
            date_key: str(datetime.now().date()).replace('-', ''),
            'deviceId': device['id']
        }
        LOGGER.debug(
            f'Fetching litter box({device["id"]}) device record page at {dr_url}'
        )
        device_record = await self._post(dr_url, header, dr_data)
        LOGGER.debug(
            f'Litter box record response:\n'
            f'{json.dumps(device_record, indent=4)}'
        )

        ### Fetch statistic page
        stat_url = f'{self.base_url}{device_type_lower}/{Endpoint.STATISTIC}'
        stat_data = {
            'deviceId': device['id'],
            'endDate': str(datetime.now().date()).replace('-', ''),
            'startDate': str(datetime.now().date()).replace('-', ''),
            'type': 0
        }
        LOGGER.debug(
            f'Fetching litter box({device["id"]}) statistics page at {stat_url}'
        )
        device_stats = await self._post(stat_url, header, stat_data)
        LOGGER.debug(
            f'Litter box statistics response:\n'
            f'{json.dumps(device_stats, indent=4)}'
        )

        if device_detail['result']['id'] in self.manually_paused:
            # Check to see if manual pause is currently True
            if self.manually_paused[device_detail['result']['id']]:
                await self.check_manual_pause_expiration(device_detail['result']['id'])
                manually_paused = self.manually_paused[device_detail['result']['id']]
                LOGGER.debug(
                    f'Litter box({device["id"]}) manual pause state: {manually_paused}'
                )
            else:
                manually_paused = False
                LOGGER.debug(
                    f'Litter box({device["id"]}) manual pause state: {manually_paused}'
                )
        else:
            # Set to False on initial run
            manually_paused = False
            LOGGER.debug(
                f'Litter box({device["id"]}) manual pause state: {manually_paused}'
            )

        if device_detail['result']['id'] in self.manual_pause_end:
            manual_pause_end = self.manual_pause_end[device_detail['result']['id']]
            LOGGER.debug(
                f'Litter box({device["id"]}) manual pause end: {manual_pause_end}'
            )
        else:
            # Set to None on initial run
            manual_pause_end = None
            LOGGER.debug(
                f'Litter box({device["id"]}) manual pause end: {manual_pause_end}'
            )
        ### Create LitterBox Object
        litter_box_instance = LitterBox(
            id=device_detail['result']['id'],
            device_detail=device_detail['result'],
            device_record=device_record['result'],
            statistics=device_stats['result'],
            type=device_type_lower,
            manually_paused=manually_paused,
            manual_pause_end=manual_pause_end,
        )
        return litter_box_instance, device_detail['result']['id']

    async def _handle_purifier(self, device: dict[str, Any], header: dict[str, str]) -> (Purifier, int):
        """Handle parsing purifier data."""

        ### Fetch device_detail page
        device_type_lower = device["type"].lower()
        dd_url = f'{self.base_url}{device_type_lower}/{Endpoint.DEVICE_DETAIL}'
        dd_data = {
            'id': device['id']
        }
        LOGGER.debug(
            f'Fetching purifier({device["id"]}) device details page at {dd_url}'
        )
        device_detail = await self._post(dd_url, header, dd_data)
        LOGGER.debug(
            f'Purifier data response:\n'
            f'{json.dumps(device_detail, indent=4)}'
        )

        ### Create Purifier Object ###
        purifier_instance = Purifier(
            id=device_detail['result']['id'],
            device_detail=device_detail['result'],
            type=device_type_lower,
        )
        return purifier_instance, device_detail['result']['id']

    async def _handle_pets(self, header: dict[str, str]) -> dict[int, Pet]:
        """Handle parsing pet data."""

        pets_data: dict[int, Pet] = {}
        ### Get user details page
        details_url = f'{self.base_url}{Endpoint.USER_DETAILS}'
        details_data = {
            'userId': self.user_id
        }
        LOGGER.debug(f'Fetching pets from user details page at {details_url}')
        user_details = await self._post(details_url, header, details_data)
        LOGGER.debug(
            f'User details/pets page response:\n'
            f'{json.dumps(user_details, indent=4)}'
        )
        user_pets = user_details['result']['user']['dogs']
        if user_pets:
            for pet in user_pets:
                ### Create Pet Object
                pets_data[int(pet['id'])] = Pet(
                    id=pet['id'],
                    data=pet,
                    type=pet['type']['name']
                )
        return pets_data

    async def _post(self, url: str, headers: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        """Make POST API call."""

        async with self._session.post(url, headers=headers, data=data, timeout=self.timeout) as resp:
            return await self._response(resp)

    @staticmethod
    async def _response(resp: ClientResponse) -> dict[str, Any]:
        """Return response from API call."""

#        if resp.status != 200:
#            error = await resp.text()
#            raise PetKitError(f'PetKit API Error Encountered. Status: {resp.status}; Error: {error}')
        try:
            response: dict[str, Any] = await resp.json()
        except Exception as error:
            raise PetKitError(f'Could not return json {error}') from error
        if 'error' in response:
            code = response['error']['code']
            if code in AUTH_ERROR_CODES:
                raise AuthError(f'PetKit Error {code}: {AUTH_ERROR_CODES[code]}')
            elif code in SERVER_ERROR_CODES:
                raise ServerError(f'PetKit Error {code}: {SERVER_ERROR_CODES[code]}')
            elif code in BLUETOOTH_ERRORS:
                raise BluetoothError(f'{BLUETOOTH_ERRORS[code]}')
            else:
                raise PetKitError(f'PetKit Error {code}: {response["error"]["msg"]}')
        return response


# <--------------------------------------- Methods for controlling devices --------------------------------------->


    async def start_ble_connection(self, conn_url: str, header: dict[str, Any], ble_data: dict[str, Any], ble_connect_attempt: int) -> bool:
        """Used to initiate the BLE relay connection."""

        # Stop trying to connect via BLE relay after 4 attempts
        if ble_connect_attempt > 4:
            LOGGER.debug(
                f'BLE connection attempt count: {ble_connect_attempt}. Connection unsuccessful.'
            )
            conn_success = False
            return conn_success
        else:
            conn_resp = await self._post(conn_url, header, ble_data)
            LOGGER.debug(
                f'BLE connection attempt {ble_connect_attempt} response:\n'
                f'{json.dumps(conn_resp, indent=4)}'
            )
            # State should be 1 if connection was successful 
            if conn_resp['result']['state'] != 1:
                LOGGER.debug('BLE connection attempt failed.')
                ble_connect_attempt += 1
                await asyncio.sleep(3)
                await self.start_ble_connection(conn_url, header, ble_data, ble_connect_attempt)
            else:
                conn_success = True
                return conn_success

    async def poll_ble_connection(self, poll_url: str, header: dict[str, Any], ble_data: dict[str, Any], ble_poll_attempt: int) -> bool:
        """Initiate polling via the BLE relay and attempt again if it fails."""

        # Stop trying to poll via BLE relay after 4 attempts
        if ble_poll_attempt > 4:
            LOGGER.debug(
                f'BLE polling attempt count: {ble_poll_attempt}. Polling unsuccessful.'
            )
            poll_success = False
            return poll_success
        else:
            poll_resp = await self._post(poll_url, header, ble_data)
            LOGGER.debug(
                f'BLE polling attempt {ble_poll_attempt} response:\n'
                f'{json.dumps(poll_resp, indent=4)}'
            )
            # Result should be 0 if polling was successful 
            if poll_resp['result'] != 0:
                LOGGER.debug('BLE polling attempt failed.')
                ble_poll_attempt += 1
                await asyncio.sleep(3)
                await self.poll_ble_connection(poll_url, header, ble_data, ble_poll_attempt)
            else:
                poll_success = True
                return poll_success
        
    
    async def initial_ble_commands(self, device: dict[str, Any], relay_type: int) -> None:
        """We have to make two calls to get updated date from the water fountain."""
        command_url = f'{self.base_url}{Endpoint.CONTROL_WF}'
        header = await self.create_header()
        data1 = await self.create_ble_data(W5Command.FIRST_BLE_CMND)
        first_command = {
            'bleId': device['result']['id'],
            'cmd': '215',
            'data': data1,
            'mac': device['result']['mac'],
            'type': relay_type
        }
        await self._post(command_url, header, first_command)
        self.ble_sequence += 1

        data2 = await self.create_ble_data(W5Command.SECOND_BLE_CMND)
        second_command = {
            'bleId': device['result']['id'],
            'cmd': '216',
            'data': data2,
            'mac': device['result']['mac'],
            'type': relay_type
        }
        await self._post(command_url, header, second_command)
        self.ble_sequence += 1


    async def create_ble_data(self, command: W5Command, device: W5Fountain | None = None) -> str:
        """Create URL encoded data from specific byte array."""

        byte_list: list = []
        if command == W5Command.FIRST_BLE_CMND:
            byte_list = [-6, -4, -3, -41, 1, self.ble_sequence, 0, 0, -5]
        if command == W5Command.SECOND_BLE_CMND:
            byte_list = [-6, -4, -3, -40, 1, self.ble_sequence, 0, 0, -5]
        if command == W5Command.NORMAL_TO_PAUSE:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 0, 1, -5]
        if command == W5Command.SMART_TO_PAUSE:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 0, 2, -5]
        if command == W5Command.NORMAL:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 1, 1, -5]
        if command == W5Command.SMART:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 1, 2, -5]

        if command == W5Command.LIGHT_OFF:
            # byte_list example = [-6, -4, -3, -35, 1, self.ble_sequence, 13, 0, 3, 3, 0, light_brightness, 0, 0, 0, 0, 0, 5, 40, 1, 104, -5]
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[0])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHT_ON:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[1])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHT_LOW:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[1])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHT_MEDIUM:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[2])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHT_HIGH:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[3])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.DO_NOT_DISTURB:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[1])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.DO_NOT_DISTURB_OFF:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[0])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.RESET_FILTER:
            byte_list = [-6, -4, -3, -34, 1, self.ble_sequence, 0, 0, -5]

        byte_array = bytearray([x % 256 for x in byte_list])
        b64_encoded = base64.b64encode(byte_array)
        url_encoded = urlencode.quote(b64_encoded, 'utf-8')
        return url_encoded

    async def w5_command_data_creator(self, device: W5Fountain, command: W5Command, setting: list) -> list:
        """Create W5 settings byte array as list."""

        data: list = []
        device_data = device.data
        if command in W5_SETTINGS_COMMANDS:
            light_up = await self.short_to_byte_list(input=device_data['settings']['lampRingLightUpTime'])
            light_out = await self.short_to_byte_list(input=device_data['settings']['lampRingGoOutTime'])
            disturb_start = await self.short_to_byte_list(input=device_data['settings']['noDisturbingStartTime'])
            disturb_end = await self.short_to_byte_list(input=device_data['settings']['noDisturbingEndTime'])

            if command in W5_LIGHT_POWER:
                data = list(chain(
                                [device_data['settings']['smartWorkingTime']],
                                [device_data['settings']['smartSleepTime']],
                                setting,
                                [device_data['settings']['lampRingBrightness']],
                                light_up,
                                light_out,
                                [device_data['settings']['noDisturbingSwitch']],
                                disturb_start,
                                disturb_end,
                            )
                        )
            if command in W5_LIGHT_BRIGHTNESS:
                data = list(chain(
                                [device_data['settings']['smartWorkingTime']],
                                [device_data['settings']['smartSleepTime']],
                                [device_data['settings']['lampRingSwitch']],
                                setting,
                                light_up,
                                light_out,
                                [device_data['settings']['noDisturbingSwitch']],
                                disturb_start,
                                disturb_end,
                            )
                        )
            if command in W5_DND_COMMANDS:
                data = list(chain(
                                [device_data['settings']['smartWorkingTime']],
                                [device_data['settings']['smartSleepTime']],
                                [device_data['settings']['lampRingSwitch']],
                                [device_data['settings']['lampRingBrightness']],
                                light_up,
                                light_out,
                                setting,
                                disturb_start,
                                disturb_end,
                            )
                        )
        return data

    async def create_ble_byte_list(self, command: int, data_list: list[int]) -> list[int]:
        """Creates final byte list which is to be encoded before being sent."""

        byte_list = list(chain(
            BLE_HEADER,
            [command],
            [1],
            [self.ble_sequence],
            [(len(data_list) & 255)],
            [(len(data_list) >> 8)],
            data_list,
            [-5]
        ))
        return byte_list

    @staticmethod
    async def short_to_byte_list(input: int) -> list:
        """Take a short and creates a list with bytes represented in int format."""

        byte_list: list = []
        i: int = 0
        while i < 2:
            i2: int = i + 1
            byte_list.append(((input >> (16 - (i2 * 8))) & 255))
            i = i2
        return byte_list

    async def get_litter_box_record(self, id: int, type: str, header: dict[str, Any]) -> dict[str, Any]:
        """Fetch the litter box getDeviceRecord endpoint."""

        url = f'{self.base_url}{type}/{Endpoint.DEVICE_RECORD}'
        data = {
            'day': str(datetime.now().date()).replace('-', ''),
            'deviceId': id
        }
        response = await self._post(url, header, data)
        return response

    async def control_water_fountain(self, water_fountain: W5Fountain, command: W5Command):
        """Set the mode on W5 Water Fountain."""
        if not water_fountain.group_relay:
            raise PetKitError(f'{water_fountain.data["name"]} does not have a valid PetKit device to use as a BLE relay.')
        else:
            # Pause command sent depends on initial mode
            if command == W5Command.PAUSE:
                if water_fountain.data['powerStatus'] == 0:
                    raise PetKitError(f'{water_fountain.data["name"]} is already paused.')
                else:
                    if water_fountain.data['mode'] == 1:
                        ble_data = await self.create_ble_data(W5Command.NORMAL_TO_PAUSE, water_fountain)
                    else:
                        ble_data = await self.create_ble_data(W5Command.SMART_TO_PAUSE, water_fountain)

            # make sure light is on if brightness is being set
            elif command in W5_LIGHT_BRIGHTNESS:
                if water_fountain.data['settings']['lampRingSwitch'] != 1:
                    raise PetKitError(f'{water_fountain.data["name"]} indicator light is Off. You can only change light brightness when the indicator light is On.')
                else:
                    ble_data = await self.create_ble_data(command, water_fountain)
            # Handle all other commands
            else:
                ble_data = await self.create_ble_data(command, water_fountain)
            header = await self.create_header()
            conn_data = {
                'bleId': water_fountain.data['id'],
                'mac': water_fountain.data['mac'],
                'type': water_fountain.ble_relay
            }
            connect_url = f'{self.base_url}{Endpoint.BLE_CONNECT}'
            poll_url = f'{self.base_url}{Endpoint.BLE_POLL}'
            command_url = f'{self.base_url}{Endpoint.CONTROL_WF}'
            disconnect_url = f'{self.base_url}{Endpoint.BLE_CANCEL}'
            cmnd_code = W5_COMMAND_TO_CODE[command]

            command_data = {
                'bleId': water_fountain.data['id'],
                'cmd': cmnd_code,
                'data': ble_data,
                'mac': water_fountain.data['mac'],
                'type': water_fountain.ble_relay
            }
            # Initiate BLE connection and poll
            conn_success = await self.start_ble_connection(connect_url, header, conn_data, 1)
            if conn_success:
                poll_success = await self.poll_ble_connection(poll_url, header, conn_data, 1)
                if poll_success:
                    # Ensure BLE connection is made before sending command
                    await asyncio.sleep(4)
                    # Send command to water fountain via BLE relay
                    await self._post(command_url, header, command_data)
                    # Reset ble_sequence
                    self.ble_sequence = 0
                    # Sever Relay connection when done
                    await asyncio.sleep(2)
                    await self._post(disconnect_url, header, conn_data)
                else:
                    raise BluetoothError(f'BLE polling step failed while attempting to send the command to the water fountain')
            else:
                raise BluetoothError(f'BLE connection step failed while attempting to send the command to the water fountain')
            
#            await self._post(connect_url, header, conn_data)
#            await self._post(poll_url, header, conn_data)
            # Ensure BLE connection is made before sending command
#            await asyncio.sleep(2)
            # Send command to water fountain via BLE relay
#            await self._post(command_url, header, command_data)
            # Reset ble_sequence
#            self.ble_sequence = 0

    async def call_pet(self, feeder: Feeder) -> None:
        """Call pet on D3 (Infinity) feeder."""

        url = f'{self.base_url}{feeder.type}/{Endpoint.CALL_PET}'
        header = await self.create_header()
        data = {
            'deviceId': feeder.id
        }
        await self._post(url, header, data)

    async def control_litter_box(self, litter_box: LitterBox, command: LitterBoxCommand) -> None:
        """Control PetKit litter boxes."""

        url = f'{self.base_url}{litter_box.type}/{Endpoint.CONTROL_DEVICE}'
        value: int = 0

        if litter_box.type == 't4':
            if command == LitterBoxCommand.START_CLEAN:
                # If the litter box is currently paused then send a resume cleaning command.
                # Otherwise, you can't start a manual clean while it is in an unsupported mode.
                if 'workState' in litter_box.device_detail['state']:
                    state =  litter_box.device_detail['state']['workState']
                    # This workState is equivalent to a paused manual cleaning
                    if (state['workMode'] == 0) and (state['workProcess'] == 20):
                        command = LitterBoxCommand.RESUME_CLEAN
                        self.manually_paused[litter_box.id] = False
                        self.manual_pause_end[litter_box.id] = None
                    else:
                        raise PetKitError('Unable to call start cleaning command while litter box is in operation.')
            if command == LitterBoxCommand.PAUSE_CLEAN:
                self.manually_paused[litter_box.id] = True
                ## The manual pause will end after a 10-minute wait + 1 minute to complete cleaning
                self.manual_pause_end[litter_box.id] = datetime.now() + timedelta(seconds=660)

        if command == LitterBoxCommand.POWER:
            #If litter box is currently turned on then you want the command to turn it off
            if litter_box.device_detail['state']['power'] == 1:
                value = 0
            else:
                value = 1
        # For all non-power commands, get the value associated with the command
        else:
            value = LB_CMD_TO_VALUE[command]

        key = LB_CMD_TO_KEY[command]
        header = await self.create_header()

        command_dict = {
            key: value
        }
        data = {
            'id': litter_box.id,
            'kv': json.dumps(command_dict),
            'type': LB_CMD_TO_TYPE[command]
        }
        await self._post(url, header, data)

        ### For Pura X, if the current session was ended while the device was paused, the new session wouldn't know the manual pause is active.
        ### Only way of resuming cleaning is to send the START_CLEAN command followed by a RESUME_CLEAN command.
        ### In addition, the resume command doesn't work by itself - start followed by resume is always needed if currently paused.
        ### Check if the device is currently paused - if so, the resume command needs to be sent after start clean.
        ### Unlike the Pura Max, we need to send the START clean command before getting the litter box record due to the Pura X not returning its current workState.
        if litter_box.type == 't3':
            if command == LitterBoxCommand.START_CLEAN:
                await asyncio.sleep(1)
                record = await self.get_litter_box_record(litter_box.id, litter_box.type, header)
                if record['result']:
                    last_item = record['result'][-1]
                    if last_item['enumEventType'] == 'clean_over':
                        if (last_item['content']['startReason'] in [0, 1, 2, 3]) and (last_item['content']['result'] == 3):
                            await self.control_litter_box(litter_box, LitterBoxCommand.RESUME_CLEAN)
                            self.manually_paused[litter_box.id] = False
                            self.manual_pause_end[litter_box.id] = None

            if command == LitterBoxCommand.PAUSE_CLEAN:
                self.manually_paused[litter_box.id] = True
                ## The manual pause will end after a 10-minute wait + 1 minute to complete cleaning
                self.manual_pause_end[litter_box.id] = datetime.now() + timedelta(seconds=660)

    async def control_purifier(self, purifier: Purifier, command: PurifierCommand) -> None:
        """Control PetKit purifiers."""

        url = f'{self.base_url}{purifier.type}/{Endpoint.CONTROL_DEVICE}'
        value: int = 0
        if command == PurifierCommand.POWER:
            # Power of 1 means it is on. Power of 2 means it is on and in standby mode
            if purifier.device_detail['state']['power'] in [1, 2]:
                value = 0
            else:
                value = 1
        else:
            value = PUR_CMD_TO_VALUE[command]
        key = PUR_CMD_TO_KEY[command]
        header = await self.create_header()
        command_dict = {
            key: value
        }
        data = {
            'id': purifier.id,
            'kv': json.dumps(command_dict),
            'type': PUR_CMD_TO_TYPE[command]
        }
        await self._post(url, header, data)

    async def check_manual_pause_expiration(self, id: int):
        """Check to see if manual pause has expired and litter box resumed the cleaning on its own."""

        current_dt = datetime.now()
        current_end = self.manual_pause_end[id]
        if (current_end - current_dt).total_seconds() <= 0:
            self.manual_pause_end[id] = None
            self.manually_paused[id] = False

    async def manual_feeding(self, feeder: Feeder, amount: int) -> None:
        """Dispense food manually.
        Mini Feeder allowed amount (in grams) is 5, 10, 15, 20, 25, 30, 35, 40, 45, 50.
        D4 (Element Solo) allowed amount is 10, 20, 30, 40, 50.
        """

        if feeder.type == 'feedermini':
            url = f'{self.base_url}{Endpoint.MINI_MANUAL_FEED}'
        elif feeder.type == 'feeder':
            url = f'{self.base_url}{Endpoint.FRESH_ELEMENT_MANUAL_FEED}'
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.MANUAL_FEED}'
        header = await self.create_header()
        data = {
            'amount': amount,
            'day': str(datetime.now().date()).replace('-', ''),
            'deviceId': feeder.id,
            'time': '-1'
        }
        await self._post(url, header, data)

    async def dual_hopper_manual_feeding(self, feeder: Feeder, amount1: int = 0, amount2: int = 0) -> None:
        """Dispense food manually for dual hopper Gemini feeder.
        Allowed amount for each side ranges from 0 to 10 portions.
        """

        invalid_amount1 = (amount1 < 0) or (amount1 > 10)
        invalid_amount2 = (amount2 < 0) or (amount2 > 10)
        if invalid_amount1 or invalid_amount2:
            raise PetKitError('Invalid portion amount specified. Each hopper can only take a portion value between/including 0 to 10')
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.MANUAL_FEED}'
            header = await self.create_header()
            data = {
                'amount1': amount1,
                'amount2': amount2,
                'day': str(datetime.now().date()).replace('-', ''),
                'deviceId': feeder.id,
                'name': '',
                'time': '-1'
            }
            response = await self._post(url, header, data)
            feeder.last_manual_feed_id = response['result']['id']
            self.last_manual_feed_id[feeder.id] = response['result']['id']

    async def update_feeder_settings(self, feeder: Feeder, setting: FeederSetting, value: int) -> None:
        """Change the setting on a feeder."""

        if feeder.type == 'feedermini':
            url = f'{self.base_url}{Endpoint.MINI_SETTING}'
        # Fresh Element Feeder
        elif feeder.type == 'feeder':
            url = f'{self.base_url}{Endpoint.FRESH_ELEMENT_SETTING}'
        # D3 and D4 Feeders
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.UPDATE_SETTING}'
        header = await self.create_header()
        setting_dict = {
            setting: value
        }
        data = {
            'id': feeder.id,
            'kv': json.dumps(setting_dict)
        }
        await self._post(url, header, data)

    async def update_litter_box_settings(self, litter_box: LitterBox, setting: LitterBoxSetting | None = None, value: int | None = None) -> None:
        """Change the setting on a litter box."""

        url = f'{self.base_url}{litter_box.type}/{Endpoint.UPDATE_SETTING}'
        header = await self.create_header()
        setting_dict = {
            setting: value
        }
        data = {
            'id': litter_box.id,
            'kv': json.dumps(setting_dict)
        }
        await self._post(url, header, data)

    async def update_pet_settings(self, pet: Pet, setting: PetSetting, value: int | float) -> None:
        """Change the setting for a pet."""

        url = f'{self.base_url}{Endpoint.PET_PROPS}'
        header = await self.create_header()
        setting_dict = {
            setting: value
        }
        data = {
            'petId': int(pet.id),
            'kv': json.dumps(setting_dict)
        }
        await self._post(url, header, data)

    async def update_purifier_settings(self, purifier: Purifier, setting: PurifierSetting, value: int) -> None:
        """Change the setting on a purifier."""

        url = f'{self.base_url}{purifier.type}/{Endpoint.UPDATE_SETTING}'
        header = await self.create_header()
        setting_dict = {
            setting: value
        }
        data = {
            'id': purifier.id,
            'kv': json.dumps(setting_dict)
        }
        await self._post(url, header, data)

    async def cancel_manual_feed(self, feeder: Feeder) -> None:
        """Cancel a manual feed that is currently in progress. Not available for mini feeders"""

        # Fresh Element feeder
        if feeder.type == 'feeder':
            url = f'{self.base_url}{feeder.type}/{Endpoint.FRESH_ELEMENT_CANCEL_FEED}'
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.CANCEL_FEED}'
        header = await self.create_header()
        if feeder.type == 'd4s':
            if feeder.last_manual_feed_id is None:
                raise PetKitError('Unable to cancel manual feeding. No valid last manual feeding ID found.')
            else:
                data = {
                    'day': str(datetime.now().date()).replace('-', ''),
                    'deviceId': feeder.id,
                    'id': feeder.last_manual_feed_id
                }
                self.last_manual_feed_id[feeder.id] = None
                # Reset the last manual feed id attribute
                feeder.last_manual_feed_id = None
        else:
            data = {
                'day': str(datetime.now().date()).replace('-', ''),
                'deviceId': feeder.id
            }
        await self._post(url, header, data)

    async def reset_feeder_desiccant(self, feeder: Feeder) -> None:
        """Reset the desiccant of a single feeder."""

        if feeder.type == 'feedermini':
            url = f'{self.base_url}{Endpoint.MINI_DESICCANT_RESET}'
        # Fresh Element Feeder
        elif feeder.type == 'feeder':
            url = f'{self.base_url}{Endpoint.FRESH_ELEMENT_DESICCANT_RESET}'
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.FEEDER_DESICCANT_RESET}'
        header = await self.create_header()
        data = {
            'deviceId': feeder.id
        }
        await self._post(url, header, data)

    async def reset_pura_max_deodorizer(self, litter_box: LitterBox) -> None:
        """Reset the N50 odor eliminator for Pura Max."""

        if litter_box.type != 't4':
            raise PetKitError('Invalid litter box type. Only Pura Max litter boxes have N50 odor eliminators.')
        url = f'{self.base_url}{litter_box.type}/{Endpoint.MAX_ODOR_RESET}'
        header = await self.create_header()
        data = {
            'deviceId': litter_box.id
        }
        await self._post(url, header, data)

    async def food_replenished(self, feeder: Feeder) -> None:
        """Tell PetKit servers that food in the feeder has been replenished.
        Currently only used for the D4s (Gemini) feeder.
        If you don't send this command after adding food to the feeder containers,
        the food state (empty/not empty) won't change until the next scheduled or manual feeding.
        """

        if feeder.type != 'd4s':
            raise PetKitError('The food_replenished method is only used with D4s (Gemini) feeders.')
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.REPLENISHED_FOOD}'
            header = await self.create_header()
            data = {
                'deviceId': feeder.id,
                'noRemind': 3
            }
            await self._post(url, header, data)

    async def fresh_element_calibration(self, feeder: Feeder, command: FeederCommand) -> None:
        """Start/stop calibration command to Fresh Element feeder.
        This needs to be done whenever batteries are added or removed.
        """

        if feeder.type != 'feeder':
            raise PetKitError('Calibration is only used for Fresh Element feeders.')
        else:
            url = f'{self.base_url}{feeder.type}/{Endpoint.FRESH_ELEMENT_CALIBRATION}'
            header = await self.create_header()
            if command == FeederCommand.START_CALIBRATION:
                value = 1
            else:
                value = 0
            data = {
                'action': value,
                'deviceId': feeder.id
            }
            await self._post(url, header, data)
