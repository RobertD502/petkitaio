# PetKitAIO

Asynchronous Python library for PetKit's API.

This is PetKit's undocumented API. With that said, future changes made by PetKit may break this library. All API calls are made to PetKit's USA servers.

## **Currently Supported Devices**:
- [D4 Feeder (FreshElement Solo)](https://www.amazon.com/PETKIT-Automatic-Dispenser-Compatible-Freeze-Dried/dp/B09158J9PF/)
- [Mini Feeder](https://www.amazon.com/PETKIT-Automatic-Stainless-Indicator-Dispenser-2-8L/dp/B08GS1CPHH/)
- [W5 Water Fountain (Eversweet 3 Pro)](https://www.amazon.com/PETKIT-Wireless-Fountain-Stainless-Dispenser/dp/B09QRH6L3M/)

## Important

`If you don't have a water fountain on your PetKit account:`
Create a new PetKit account and share your devices from your original account to it. This will allow you to use your main account on the mobile app, and the secondary account with this library. Otherwise, your main account will get logged out of the mobile app when using this library. This is a limitation of how PetKit handles authorization.

`If you do have a water fountain:`
Unfortunately, there is no way of sharing a water fountain with a secondary account. As a result, you will need to use your main PetKit account to pull in water fountain data. When doing so, your main account will get signed out of any mobile app it is currently signed in on. This is a limitation of how PetKit handles authorization. If you only want to pull in data for non-water fountain devices, see "If you don't have a water fountain on your PetKit account" above.

This package depends on [aiohttp](https://docs.aiohttp.org/en/stable/) and requires `Python 3.7` or greater.

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
await client.update_feeder_settings(feeder=devices.feeders[feederid], setting=FeederSetting.CHILDLOCK, value=1)
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
