# PetKitAIO

Asynchronous Python library for PetKit's API.

This is PetKit's undocumented API. With that said, future changes made by PetKit may break this library. The API endpoint used is determined based on the region your account is locked to. See the `Regions` section for available region values.

## **Currently Supported Devices**:

`Feeders`
- [Fresh Element](https://petkit.us/products/petkit-element-wi-fi-enabled-smart-pet-food-container-feeder)
- [D3 (Fresh Element Infinity)](https://www.amazon.com/PETKIT-Automatic-Stainless-Programmable-Dispenser/dp/B09JFK8BCQ)
- [D4 (Fresh Element Solo)](https://www.amazon.com/PETKIT-Automatic-Dispenser-Compatible-Freeze-Dried/dp/B09158J9PF/)
- [D4s (Fresh Element Gemini)](https://www.amazon.com/PETKIT-Automatic-Combination-Dispenser-Stainless/dp/B0BF56RTQH)
- [Mini Feeder](https://www.amazon.com/PETKIT-Automatic-Stainless-Indicator-Dispenser-2-8L/dp/B08GS1CPHH/)

`Litter Boxes`
- [T3 (Pura X)](https://www.amazon.com/PETKIT-Self-Cleaning-Scooping-Automatic-Multiple/dp/B08T9CCP1M)
- [T4 (Pura MAX / Pura MAX 2) with/without Pura Air](https://www.amazon.com/PETKIT-Self-Cleaning-Capacity-Multiple-Automatic/dp/B09KC7Q4YF)

`Purifiers`
- [K2 (Air Magicube)](https://www.instachew.com/product-page/petkit-air-magicube-smart-odor-eliminator)

`Water Fountains`
- [W5 (Eversweet Solo 2)](https://www.amazon.com/PETKIT-EVERSWEET-Wireless-Visualization-Dispenser-2L/dp/B0B3RWF653)
- [W5 (Eversweet 3 Pro)](https://www.amazon.com/PETKIT-Wireless-Fountain-Stainless-Dispenser/dp/B09QRH6L3M/)
- [W5 (Eversweet 3 Pro UVC Version)](https://petkit.com/products/eversweet-3-pro-wireless-pump-uvc)
- [W5 (Eversweet 5 Mini)](https://www.petkit.nl/products/eversweet-5-mini-binnen-2-weken-geleverd)


## Important

PetKit accounts can only be logged in on one device at a time. Using this library will result in getting signed out of the mobile app. If you want to continue using the mobile app, use the family share feature to share devices to a secondary account.

> [!NOTE]
> The secondary account may be used with this library. However, be aware that this library was created with a primary account - using a secondary account with this library will work, but I can't guarantee that all features will work. 


This package depends on [aiohttp](https://docs.aiohttp.org/en/stable/) and [tzlocal](https://pypi.org/project/tzlocal/). `Python 3.7` or greater is required.

## Usage

### Regions
___

<details>
  <summary> <b>See regions available</b> (<i>click to expand</i>)</summary>
  <!---->

| Region                                                |
|-------------------------------------------------------|
| Afghanistan                                           |
| Aland Islands                                         |
| Albania                                               |
| Algeria                                               |
| American Samoa                                        |
| Andorra                                               |
| Angola                                                |
| Anguilla                                              |
| Antarctica                                            |
| Antigua and Barbuda                                   |
| Argentina                                             |
| Armenia                                               |
| Aruba                                                 |
| Australia                                             |
| Austria                                               |
| Azerbaijan                                            |
| Bahamas                                               |
| Bahrain                                               |
| Bangladesh                                            |
| Barbados                                              |
| Belarus                                               |
| Belgium                                               |
| Belize                                                |
| Benin                                                 |
| Bermuda                                               |
| Bhutan                                                |
| Bolivia                                               |
| Bosnia and Herzegovina                                |
| Botswana                                              |
| Bouvet Island                                         |
| Brazil                                                |
| British Indian Ocean Territory                        |
| Brunei Darussalam                                     |
| Bulgaria                                              |
| Burkina Faso                                          |
| Burundi                                               |
| Cambodia                                              |
| Cameroon                                              |
| Canada                                                |
| Cape Verde                                            |
| Cayman Islands                                        |
| Central African Republic                              |
| Chad                                                  |
| Chile                                                 |
| China                                                 |
| Christmas Island                                      |
| Cocos (Keeling) Islands                               |
| Colombia                                              |
| Comoros                                               |
| Congo                                                 |
| Congo (the Democratic Republic of the Congo)          |
| Cook Islands                                          |
| Costa Rica                                            |
| Côte d'Ivoire                                         |
| Croatia                                               |
| Cuba                                                  |
| Cyprus                                                |
| Czech Republic                                        |
| Denmark                                               |
| Djibouti                                              |
| Dominica                                              |
| Dominican Republic                                    |
| Ecuador                                               |
| Egypt                                                 |
| El Salvador                                           |
| Equatorial Guinea                                     |
| Eritrea                                               |
| Estonia                                               |
| Ethiopia                                              |
| Falkland Islands [Malvinas]                           |
| Faroe Islands                                         |
| Fiji                                                  |
| Finland                                               |
| France                                                |
| French Guiana                                         |
| French Polynesia                                      |
| French Southern Territories                           |
| Gabon                                                 |
| Gambia                                                |
| Georgia                                               |
| Germany                                               |
| Ghana                                                 |
| Gibraltar                                             |
| Greece                                                |
| Greenland                                             |
| Grenada                                               |
| Guadeloupe                                            |
| Guam                                                  |
| Guatemala                                             |
| Guernsey                                              |
| Guinea                                                |
| Guinea-Bissau                                         |
| Guyana                                                |
| Haiti                                                 |
| Heard Island and McDonald Islands                     |
| Holy See [Vatican City State]                         |
| Honduras                                              |
| Hong Kong                                             |
| Hungary                                               |
| Iceland                                               |
| India                                                 |
| Indonesia                                             |
| Iran (the Islamic Republic of Iran)                   |
| Iraq                                                  |
| Ireland                                               |
| Isle of Man                                           |
| Israel                                                |
| Italy                                                 |
| Jamaica                                               |
| Japan                                                 |
| Jersey                                                |
| Jordan                                                |
| Kazakhstan                                            |
| Kenya                                                 |
| Kiribati                                              |
| Korea (the Democratic People's Republic of Korea)     |
| Korea (the Republic of Korea)                         |
| Kuwait                                                |
| Kyrgyzstan                                            |
| Lao People's Democratic Republic                      |
| Latvia                                                |
| Lebanon                                               |
| Lesotho                                               |
| Liberia                                               |
| Libyan Arab Jamahiriya                                |
| Liechtenstein                                         |
| Lithuania                                             |
| Luxembourg                                            |
| Macao                                                 |
| Macedonia (the former Yugoslav Republic of Macedonia) |
| Madagascar                                            |
| Malawi                                                |
| Malaysia                                              |
| Maldives                                              |
| Mali                                                  |
| Malta                                                 |
| Marshall Islands                                      |
| Martinique                                            |
| Mauritania                                            |
| Mauritius                                             |
| Mayotte                                               |
| Mexico                                                |
| Micronesia (the Federated States of Micronesia)       |
| Moldova (the Republic of Moldova)                     |
| Monaco                                                |
| Mongolia                                              |
| Montenegro                                            |
| Montserrat                                            |
| Morocco                                               |
| Mozambique                                            |
| Myanmar                                               |
| Namibia                                               |
| Nauru                                                 |
| Nepal                                                 |
| Netherlands                                           |
| Netherlands Antilles                                  |
| New Caledonia                                         |
| New Zealand                                           |
| Nicaragua                                             |
| Niger                                                 |
| Nigeria                                               |
| Niue                                                  |
| Norfolk Island                                        |
| Northern Mariana Islands                              |
| Norway                                                |
| Oman                                                  |
| Pakistan                                              |
| Palau                                                 |
| Palestinian Territory                                 |
| Panama                                                |
| Papua New Guinea                                      |
| Paraguay                                              |
| Peru                                                  |
| Philippines                                           |
| Pitcairn                                              |
| Poland                                                |
| Portugal                                              |
| Puerto Rico                                           |
| Qatar                                                 |
| Réunion                                               |
| Romania                                               |
| Russian Federation                                    |
| Rwanda                                                |
| Saint Helena                                          |
| Saint Kitts and Nevis                                 |
| Saint Lucia                                           |
| Saint Pierre and Miquelon                             |
| Saint Vincent and the Grenadines                      |
| Samoa                                                 |
| San Marino                                            |
| Sao Tome and Principe                                 |
| Saudi Arabia                                          |
| Senegal                                               |
| Serbia                                                |
| Seychelles                                            |
| Sierra Leone                                          |
| Singapore                                             |
| Slovakia                                              |
| Slovenia                                              |
| Solomon Islands                                       |
| Somalia                                               |
| South Africa                                          |
| South Georgia and the South Sandwich Islands          |
| Spain                                                 |
| Sri Lanka                                             |
| Sudan                                                 |
| Suriname                                              |
| Svalbard and Jan Mayen                                |
| Swaziland                                             |
| Sweden                                                |
| Switzerland                                           |
| Syrian Arab Republic                                  |
| Taiwan (Province of China)                            |
| Tajikistan                                            |
| Tanzania,United Republic of                           |
| Thailand                                              |
| Timor-Leste                                           |
| Togo                                                  |
| Tokelau                                               |
| Tonga                                                 |
| Trinidad and Tobago                                   |
| Tunisia                                               |
| Turkey                                                |
| Turkmenistan                                          |
| Turks and Caicos Islands                              |
| Tuvalu                                                |
| Uganda                                                |
| Ukraine                                               |
| United Arab Emirates                                  |
| United Kingdom                                        |
| United States                                         |
| United States Minor Outlying Islands                  |
| Uruguay                                               |
| Uzbekistan                                            |
| Vanuatu                                               |
| Venezuela                                             |
| Viet Nam                                              |
| Virgin Islands (British)                              |
| Virgin Islands (U.S.)                                 |
| Wallis and Futuna                                     |
| Western Sahara                                        |
| Yemen                                                 |
| Zambia                                                |
| Zimbabwe                                              |

</details>

### Creating Client
___

```python
import asyncio
from petkitaio import PetKitClient
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:

        # Create a client using PetKit account email, password, and region
        client = PetKitClient('email', 'password', session, 'United States')


        ####################################################################################
        Examples within the examples section utilize the PetKitClient instance created above
        ####################################################################################



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
