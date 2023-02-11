"""Constants for PetKitAIO"""

from .str_enum import StrEnum

class Region(StrEnum):

    US = 'http://api.petkt.com/latest'
    CN = 'http://api.petkit.cn/6'


class Endpoint(StrEnum):

    LOGIN = '/user/login'
    DEVICEROSTER = '/discovery/device_roster'
    W5 = '/w5/deviceData'
    BLEDEVICES = '/ble/ownSupportBleDevices'
    BLECONNECT = '/ble/connect'
    BLEPOLL = '/ble/poll'
    BLECANCEL = '/ble/cancel'
    DEVICEDETAIL = '/device_detail'
    CONTROLWF = '/ble/controlDevice'
    MANUALFEED = '/saveDailyFeed'
    FEEDERSETTING = '/updateSettings'
    FEEDERDESICCANTRESET = '/desiccantReset'
    CANCELFEED = '/cancelRealtimeFeed'
    MINISETTING = '/feedermini/update'
    MINIDESICCANTRESET = '/feedermini/desiccant_reset'
    MINIMANUALFEED = '/feedermini/save_dailyfeed'

class FeederSetting(StrEnum):

    SHORTAGEALARM = 'foodWarn'
    CHILDLOCK = 'manualLock'
    INDICATORLIGHT = 'lightMode'
    DISPENSETONE = 'feedSound'
    MINICHILDLOCK = 'settings.manualLock'
    MINIINDICATORLIGHT = 'settings.lightMode'


class Header(StrEnum):

    ACCEPT = '*/*'
    XTIMEZONE = '-5.0'
    ACCEPTLANG = 'en-US;q=1, it-US;q=0.9'
    ENCODING = 'gzip, deflate'
    APIVERSION = '8.28.0'
    CONTENTTYPE = 'application/x-www-form-urlencoded'
    AGENT = 'PETKIT/8.28.0 (iPhone; iOS 15.1; Scale/3.00)'
    TZ = 'America/New_York'
    CLIENT = 'ios(15.1;iPhone14,3)'
    LOCALE = 'en_US'

class W5Command(StrEnum):

    PAUSE = 'Pause'
    NORMALTOPAUSE = 'Normal To Pause'
    SMARTTOPAUSE = 'Smart To Pause'
    NORMAL = 'Normal'
    SMART = 'Smart'
    RESETFILTER = 'Reset Filter'
    DONOTDISTURB = 'Do Not Disturb'
    DONOTDISTURBOFF = 'Do Not Disturb Off'
    FIRSTBLECMND = 'First BLE Command'
    SECONDBLECMND = 'Second BLE Command'
    LIGHTLOW = 'Light Low'
    LIGHTMEDIUM = 'Light Medium'
    LIGHTHIGH = 'Light High'
    LIGHTON = 'Light On'
    LIGHTOFF = 'Light Off'


TIMEOUT = 5 * 60

CLIENT_DICT = {
    "locale":"en-US",
    "source":"app.petkit-ios-oversea",
    "platform":"ios",
    "osVersion":"15.1",
    "timezone":"-5.0",
    "timezoneId":"America\/New_York",
    "version":"8.28.0",
    "token":"",
    "name":"iPhone14,3"
}

ERROR_CODES = {
    1: 'PetKit servers are busy. Please try again later.',
    122: 'PetKit username/email or password is incorrect',
    5: 'Login session expired. Your account can only be signed in on one device.',
}

BLUETOOTH_ERRORS = {
    3003: 'Bluetooth connection failed. Retrying on next update.'
}

BLE_HEADER = [-6, -4, -3]
FEEDER_LIST = ['D4', 'FeederMini']
LITTER_LIST = ['T3', 'T4']
WATER_FOUNTAIN_LIST = ['W5']
W5_COMMAND_TO_CODE = {
    W5Command.DONOTDISTURB: '221',
    W5Command.DONOTDISTURBOFF: '221',
    W5Command.LIGHTON: '221',
    W5Command.LIGHTOFF: '221',
    W5Command.LIGHTLOW: '221',
    W5Command.LIGHTMEDIUM: '221',
    W5Command.LIGHTHIGH: '221',
    W5Command.PAUSE: '220',
    W5Command.RESETFILTER: '222',
    W5Command.NORMAL: '220',
    W5Command.NORMALTOPAUSE: '220',
    W5Command.SMART: '220',
    W5Command.SMARTTOPAUSE: '220',
}

W5_DND_COMMANDS = [W5Command.DONOTDISTURB, W5Command.DONOTDISTURBOFF]
W5_LIGHT_BRIGHTNESS = [W5Command.LIGHTLOW, W5Command.LIGHTMEDIUM, W5Command.LIGHTHIGH]
W5_LIGHT_POWER = [W5Command.LIGHTON, W5Command.LIGHTOFF]
W5_MODE = [W5Command.NORMAL, W5Command.SMART, W5Command.NORMALTOPAUSE, W5Command.SMARTTOPAUSE]
W5_SETTINGS_COMMANDS = [
    W5Command.DONOTDISTURB,
    W5Command.DONOTDISTURBOFF,
    W5Command.LIGHTLOW,
    W5Command.LIGHTMEDIUM,
    W5Command.LIGHTHIGH,
    W5Command.LIGHTON,
    W5Command.LIGHTOFF,
]
