# PetKitAIO

Asynchronous Python library for PetKit's API.

This is PetKit's undocumented API. With that said, future changes made by PetKit may break this library. The API endpoint used is determined based on the region your account is locked to. Although support has been added for the PetKit Asia API endpoint, I have not personally tested it.

## **Currently Supported Devices**:
- [D3 Feeder (Fresh Element Infinity)](https://www.amazon.com/PETKIT-Automatic-Stainless-Programmable-Dispenser/dp/B09JFK8BCQ)
- [D4 Feeder (Fresh Element Solo)](https://www.amazon.com/PETKIT-Automatic-Dispenser-Compatible-Freeze-Dried/dp/B09158J9PF/)
- [Mini Feeder](https://www.amazon.com/PETKIT-Automatic-Stainless-Indicator-Dispenser-2-8L/dp/B08GS1CPHH/)
- [W5 Water Fountain (Eversweet 3 Pro)](https://www.amazon.com/PETKIT-Wireless-Fountain-Stainless-Dispenser/dp/B09QRH6L3M/)
- [T3 Litter Box (Pura X)](https://www.amazon.com/PETKIT-Self-Cleaning-Scooping-Automatic-Multiple/dp/B08T9CCP1M)
- [T4 Litter Box (Pura MAX) with/without Pura Air](https://www.amazon.com/PETKIT-Self-Cleaning-Capacity-Multiple-Automatic/dp/B09KC7Q4YF)

## Important

PetKit accounts can only be logged in on one device at a time. Using this library will result in getting signed out of the mobile app. You can avoid this by creating a secondary account and sharing devices from the main account (except water fountains). However, some device functionality is lost when using a secondary account as well as not being able to share pets between accounts.


This package depends on [aiohttp](https://docs.aiohttp.org/en/stable/) and [tzlocal](https://pypi.org/project/tzlocal/). `Python 3.7` or greater is required.

## Usage

### Creating Client

```python
import asyncio
from petkitaio import PetKitClient
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:

        # Create a client using PetKit account email and password
        client = PetKitClient('email', 'password', session)


        ###################################################################################
        Examples within the examples section utilize the PetKitClient instance created above
        ###################################################################################



loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

## Examples

### Retrieving all PetKit devices on account

```python
# See model.py for details regarding Data Classes created

devices = await client.get_petkit_data()
```

### Manual Feeding
```python
# See model.py for details regarding "Feeder" class


# Reusing retrieved devices from above. Note: A valid amount (in grams) will depend on the capabilities of the feeder.
await client.manual_feeding(feeder=devices.feeders[feederid], amount=10)
```

### Change Feeder Setting
```python
# See constants.py FeederSetting class for available settings
# Additional import needed:
from petkitaio.constants import FeederSetting


# Enabling child lock on a D4 feeder. Note: Mini Feeders use a different setting.
# Reusing retrieved devices from above.
await client.update_feeder_settings(feeder=devices.feeders[feederid], setting=FeederSetting.CHILD_LOCK, value=1)
```

### Reset Feeder Desiccant
```python
# Reusing retrieved devices from above.
await client.reset_feeder_desiccant(feeder=devices.feeders[feederid])
```

### Control Water Fountain via BLE Relay
```python
# A valid relay (set up through the PetKit app) is required in order to send commands to the Eversweet 3 Pro
# See constants.py W5Command class for available commands
# Additional import needed:
from petkitaio.constants import W5Command

# Set Water Fountain to Smart Mode. Reusing retrieved devices from above.
await client.control_water_fountain(water_fountain=devices.water_fountains[water_fountain_id], command=W5Command.SMART)
```
