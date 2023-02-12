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

from petkitaio.constants import (
    BLE_HEADER,
    BLUETOOTH_ERRORS,
    CLIENT_DICT,
    Endpoint,
    ERROR_CODES,
    FEEDER_LIST,
    FeederSetting,
    Header,
    LITTER_LIST,
    Region,
    TIMEOUT,
    WATER_FOUNTAIN_LIST,
    W5Command,
    W5_COMMAND_TO_CODE,
    W5_DND_COMMANDS,
    W5_LIGHT_BRIGHTNESS,
    W5_LIGHT_POWER,
    W5_SETTINGS_COMMANDS,
)
from petkitaio.exceptions import (AuthError, BluetoothError, PetKitError)
from petkitaio.model import (Feeder, LitterBox, PetKitData, W5Fountain)

LOGGER = logging.getLogger(__name__)


class PetKitClient:
    """PetKit client."""

    def __init__(
        self, username: str, password: str, session: ClientSession | None = None, timeout: int = TIMEOUT
    ) -> None:
        """Initialize PetKit Client.

        username: PetKit username/email
        password: PetKit account password
        session: aiohttp.ClientSession or None to create a new session
        """

        self.username: str = username
        self.password: str = password
        self.base_url: Region = Region.US
        self._session: ClientSession = session if session else ClientSession()
        self.timeout: int = timeout
        self.token: str | None = None
        self.token_expiration: datetime | None = None
        self.user_id: str | None = None
        self.has_relay: bool = False
        self.ble_sequence: int = 0

    async def login(self) -> None:
        login_url = f'{self.base_url}{Endpoint.LOGIN}'

        headers = {
            'Accept': Header.ACCEPT,
            'Accept-Language': Header.ACCEPTLANG,
            'Accept-Encoding': Header.ENCODING,
            'X-Api-Version': Header.APIVERSION,
            'Content-Type': Header.CONTENTTYPE,
            'User-Agent': Header.AGENT,
            'X-Client': Header.CLIENT,
        }

        data = {
            'client': str(CLIENT_DICT),
            'encrypt': '1',
            'oldVersion': Header.APIVERSION,
            'password': hashlib.md5(self.password.encode()).hexdigest(),
            'username': self.username
        }

        response = await self._post(login_url, headers, data)
        self.user_id = response['result']['session']['userId']
        self.token = response['result']['session']['id']
        self.token_expiration = datetime.now() + timedelta(seconds=response['result']['session']['expiresIn'])

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
            await self.login()
        else:
            return None

    async def create_header(self) -> dict[str, str]:
        """Create header for interaction with devices."""

        header = {
            'X-Session': self.token,
            'F-Session': self.token,
            'Accept': Header.ACCEPT,
            'Accept-Language': Header.ACCEPTLANG,
            'Accept-Encoding': Header.ENCODING,
            'X-Api-Version': Header.APIVERSION,
            'Content-Type': Header.CONTENTTYPE,
            'User-Agent': Header.AGENT,
            'X-Client': Header.CLIENT,
        }
        return header

    async def get_device_roster(self) -> dict[str, Any]:
        """Fetch device roster endpoint to get all available devices."""

        await self.check_token()
        url = f'{self.base_url}{Endpoint.DEVICEROSTER}'
        header = await self.create_header()
        data = {
            'day': str(datetime.now().date()).replace('-', ''),
        }
        device_roster = await self._post(url, header, data)
        return device_roster

    async def get_petkit_data(self) -> PetKitData:
        """Fetch data for all PetKit devices."""

        device_roster = await self.get_device_roster()
        if 'hasRelay' in device_roster['result']:
            self.has_relay = device_roster['result']['hasRelay']
        else:
            self.has_relay = False
        header = await self.create_header()

        fountains_data: dict[int, W5Fountain] = {}
        feeders_data: dict[int, Feeder] = {}
        litter_boxes_data: dict[int, LitterBox] = {}

        devices = device_roster['result']['devices']
        LOGGER.debug(f'Found the following PetKit devices: {devices}')
        if devices:
            for device in devices:
                # W5 Water Fountain
                if device['type'] in WATER_FOUNTAIN_LIST:
                    device_type: str = device['type'].lower()
                    fountain_data: dict[str, Any] = {}
                    relay_tc: int | None = None
                    wf_url = f'{self.base_url}{Endpoint.W5}'
                    data = {
                        'id': device['data']['id']
                    }

                    if self.has_relay:
                        ble_available: bool = False
                        main_online: bool = False
                        fountain_tcode = str(device['data']['typeCode'])
                        ble_url = f'{self.base_url}{Endpoint.BLEDEVICES}'
                        relay_devices = await self._post(ble_url, header, data={})
                        if relay_devices['result']:
                            ble_available = True
                            for relay_device in relay_devices['result']:
                                if relay_device['pim'] == 1:
                                    main_online = True
                                    break
                                else:
                                    main_online = False

                            if ble_available and main_online:
                                device_details = await self._post(wf_url, header, data)
                                mac = device_details['result']['mac']
                                type_code = int(f'1{fountain_tcode}')
                                relay_tc = type_code
                                conn_url = f'{self.base_url}{Endpoint.BLECONNECT}'
                                ble_data = {
                                    'bleId': device_details['result']['id'],
                                    'mac': mac,
                                    'type': type_code
                                }
                                conn_resp = await self._post(conn_url, header, ble_data)
                                # Check to see if BLE connection was successful
                                if conn_resp['result']['state'] != 1:
                                    LOGGER.warning(f'BLE connection to {device_details["result"]["name"]} failed. Will try again during next refresh.')
                                    fountain_data = device_details
                                else:
                                    poll_url = f'{self.base_url}{Endpoint.BLEPOLL}'
                                    poll_resp = await self._post(poll_url, header, ble_data)
                                    if poll_resp['result'] != 0:
                                        LOGGER.warning(
                                            f'BLE polling to {device_details["result"]["name"]} failed. Will try again during next refresh.')
                                        fountain_data = device_details
                                    else:
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
                                            #LOGGER.error('BLE connection failed. Trying again on next update.')
                                            pass
                                        finally:
                                            fountain_data = await self._post(wf_url, header, data)
                            if not main_online:
                                LOGGER.warning(f'Unable to use BLE relay: Main relay device is reported as being offline. Fetching latest available data.')
                                fountain_data = await self._post(wf_url, header, data)
                        else:
                            fountain_data = await self._post(wf_url, header, data)
                    else:
                        fountain_data = await self._post(wf_url, header, data)

                    fountains_data[fountain_data['result']['id']] = W5Fountain(
                        id=fountain_data['result']['id'],
                        data=fountain_data['result'],
                        type=device_type,
                        ble_relay=relay_tc
                    )
                # Feeders
                if device['type'] in FEEDER_LIST:
                    feeder_url = f'{self.base_url}/{device["type"].lower()}{Endpoint.DEVICEDETAIL}'
                    data = {
                        'id': device['data']['id']
                    }
                    feeder_data = await self._post(feeder_url, header, data)
                    feeders_data[feeder_data['result']['id']] = Feeder(
                        id=feeder_data['result']['id'],
                        data=feeder_data['result'],
                        type=device['type'].lower()
                    )
                # Litter Boxes
                if device['type'] in LITTER_LIST:
                    litter_url = f'{self.base_url}/{device["type"].lower()}{Endpoint.DEVICEDETAIL}'
                    data = {
                        'id': device['data']['id']
                    }
                    litter_data = await self._post(litter_url, header, data)
                    litter_boxes_data[litter_data['result']['id']] = LitterBox(
                        id=litter_data['result']['id'],
                        data=litter_data['result'],
                        type=device['type'].lower()
                    )

        return PetKitData(user_id=self.user_id, feeders=feeders_data, litter_boxes=litter_boxes_data, water_fountains=fountains_data)


    async def _post(self, url: str, headers: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        """Make POST API call."""

        async with self._session.post(url, headers=headers, data=data, timeout=self.timeout) as resp:
            return await self._response(resp)

    @staticmethod
    async def _response(resp: ClientResponse) -> dict[str, Any]:
        """Return response from API call."""

        if resp.status != 200:
            error = await resp.text()
            raise PetKitError(f'PetKit API error: {error}')
        try:
            response: dict[str, Any] = await resp.json()
        except Exception as error:
            raise PetKitError(f'Could not return json {error}') from error
        if 'error' in response:
            code = response['error']['code']
            if code in ERROR_CODES:
                raise AuthError(f'PetKit Error {code}: {ERROR_CODES[code]}')
            elif code in BLUETOOTH_ERRORS:
                raise BluetoothError(f'{BLUETOOTH_ERRORS[code]}')
            else:
                raise PetKitError(f'PetKit Error {code}: {response["error"]["msg"]}')
        return response


# <--------------------------------------- Methods for controlling devices --------------------------------------->


    async def initial_ble_commands(self, device: dict[str, Any], relay_type: int) -> None:
        """We have to make two calls to get updated date from the water fountain."""
        command_url = f'{self.base_url}{Endpoint.CONTROLWF}'
        header = await self.create_header()
        data1 = await self.create_ble_data(W5Command.FIRSTBLECMND)
        first_command = {
            'bleId': device['result']['id'],
            'cmd': '215',
            'data': data1,
            'mac': device['result']['mac'],
            'type': relay_type
        }
        await self._post(command_url, header, first_command)
        self.ble_sequence += 1

        data2 = await self.create_ble_data(W5Command.SECONDBLECMND)
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
        if command == W5Command.FIRSTBLECMND:
            byte_list = [-6, -4, -3, -41, 1, self.ble_sequence, 0, 0, -5]
        if command == W5Command.SECONDBLECMND:
            byte_list = [-6, -4, -3, -40, 1, self.ble_sequence, 0, 0, -5]
        if command == W5Command.NORMALTOPAUSE:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 0, 1, -5]
        if command == W5Command.SMARTTOPAUSE:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 0, 2, -5]
        if command == W5Command.NORMAL:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 1, 1, -5]
        if command == W5Command.SMART:
            byte_list = [-6, -4, -3, -36, 1, self.ble_sequence, 2, 0, 1, 2, -5]

        if command == W5Command.LIGHTOFF:
            # byte_list example = [-6, -4, -3, -35, 1, self.ble_sequence, 13, 0, 3, 3, 0, light_brightness, 0, 0, 0, 0, 0, 5, 40, 1, 104, -5]
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[0])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHTON:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[1])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHTLOW:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[1])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHTMEDIUM:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[2])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.LIGHTHIGH:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[3])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.DONOTDISTURB:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[1])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.DONOTDISTURBOFF:
            data_list = await self.w5_command_data_creator(device=device, command=command, setting=[0])
            byte_list = await self.create_ble_byte_list(command=-35, data_list=data_list)

        if command == W5Command.RESETFILTER:
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

    async def control_water_fountain(self, water_fountain: W5Fountain, command: W5Command):
        """Set the mode on W5 Water Fountain."""
        if water_fountain.ble_relay is None:
            raise PetKitError(f'{water_fountain.data["name"]} does not have a valid BLE relay.')
        else:
            # Pause command sent depends on initial mode
            if command == W5Command.PAUSE:
                if water_fountain.data['powerStatus'] == 0:
                    raise PetKitError(f'{water_fountain.data["name"]} is already paused.')
                else:
                    if water_fountain.data['mode'] == 1:
                        ble_data = await self.create_ble_data(W5Command.NORMALTOPAUSE, water_fountain)
                    else:
                        ble_data = await self.create_ble_data(W5Command.SMARTTOPAUSE, water_fountain)

            # make sure light is on if brightness is being set
            elif command in W5_LIGHT_BRIGHTNESS:
                if water_fountain.data['settings']['lampRingSwitch'] != 1:
                    raise PetKitError(f'{water_fountain.data["name"]} indicator light is Off. You can only change light brightness when the indicator light is On.')
                else:
                    ble_data = await self.create_ble_data(command, water_fountain)
            # Handle all other commands
            else:
                # Also send current light brightness in case command is to turn indicator light on/off
#                light_brightness = water_fountain.data['settings']['lampRingBrightness']
                ble_data = await self.create_ble_data(command, water_fountain)
            header = await self.create_header()
            conn_data = {
                'bleId': water_fountain.data['id'],
                'mac': water_fountain.data['mac'],
                'type': water_fountain.ble_relay
            }
            connect_url = f'{self.base_url}{Endpoint.BLECONNECT}'
            poll_url = f'{self.base_url}{Endpoint.BLEPOLL}'
            command_url = f'{self.base_url}{Endpoint.CONTROLWF}'
            cmnd_code = W5_COMMAND_TO_CODE[command]

            command_data = {
                'bleId': water_fountain.data['id'],
                'cmd': cmnd_code,
                'data': ble_data,
                'mac': water_fountain.data['mac'],
                'type': water_fountain.ble_relay
            }
            # Initiate BLE connection and poll
            await self._post(connect_url, header, conn_data)
            await self._post(poll_url, header, conn_data)
            # Ensure BLE connection is made before sending command
            await asyncio.sleep(2)
            # Send command to water fountain via BLE relay
            send_command = await self._post(command_url, header, command_data)
            # Reset ble_sequence
            self.ble_sequence = 0


    async def manual_feeding(self, feeder: Feeder, amount: int) -> None:
        """Dispense food manually.
        Mini Feeder allowed amount (in grams) is 5, 10, 15, 20, 25, 30, 35, 40, 45, 50.
        D4 (Element Solo) allowed amount is 10, 20, 30, 40, 50.
        """

        if feeder.type == 'feedermini':
            url = f'{self.base_url}{Endpoint.MINIMANUALFEED}'
        else:
            url = f'{self.base_url}/{feeder.type}{Endpoint.MANUALFEED}'
        header = await self.create_header()
        data = {
            'amount': amount,
            'day': str(datetime.now().date()).replace('-', ''),
            'deviceId': feeder.id,
            'time': '-1'
        }
        await self._post(url, header, data)

    async def update_feeder_settings(self, feeder: Feeder, setting: FeederSetting, value: int) -> None:
        """Change the setting on a feeder."""

        if feeder.type == 'feedermini':
            url = f'{self.base_url}{Endpoint.MINISETTING}'
        else:
            url = f'{self.base_url}/{feeder.type}{Endpoint.FEEDERSETTING}'
        header = await self.create_header()
        setting = {
            setting: value
        }
        data = {
            'id': feeder.id,
            'kv': json.dumps(setting)
        }
        await self._post(url, header, data)

    async def cancel_manual_feed(self, feeder: Feeder) -> None:
        """Cancel a manual feed that is currently in progress. Not available for mini feeders"""

        url = f'{self.base_url}/{feeder.type}{Endpoint.CANCELFEED}'
        header = await self.create_header()
        data = {
            'day': str(datetime.now().date()).replace('-', ''),
            'deviceId': feeder.id
        }
        await self._post(url, header, data)

    async def reset_feeder_desiccant(self, feeder: Feeder) -> None:
        """Reset the desiccant of a single feeder."""

        if feeder.type == 'feedermini':
            url = f'{self.base_url}{Endpoint.MINIDESICCANTRESET}'
        else:
            url = f'{self.base_url}/{feeder.type}{Endpoint.FEEDERDESICCANTRESET}'
        header = await self.create_header()
        data = {
            'deviceId': feeder.id
        }
        await self._post(url, header, data)
