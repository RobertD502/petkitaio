"""Constants for PetKitAIO"""

from .str_enum import StrEnum

class Region(StrEnum):

    US = 'http://api.petkt.com/latest'
    CN = 'http://api.petkit.cn/6'


class Endpoint(StrEnum):

    BLECANCEL = '/ble/cancel'
    BLECONNECT = '/ble/connect'
    BLEDEVICES = '/ble/ownSupportBleDevices'
    BLEPOLL = '/ble/poll'
    CALLPET = '/callPet'
    CANCELFEED = '/cancelRealtimeFeed'
    CONTROLDEVICE = '/controlDevice'
    CONTROLWF = '/ble/controlDevice'
    DEVICEDETAIL = '/device_detail'
    DEVICERECORD = '/getDeviceRecord'
    DEVICEROSTER = '/discovery/device_roster'
    FEEDERDESICCANTRESET = '/desiccantReset'
    LOGIN = '/user/login'
    MANUALFEED = '/saveDailyFeed'
    MINIDESICCANTRESET = '/feedermini/desiccant_reset'
    MINIMANUALFEED = '/feedermini/save_dailyfeed'
    MINISETTING = '/feedermini/update'
    PETPROPS = '/pet/updatepetprops'
    REFRESHHOME = '/discovery/refreshHome'
    SOUNDLIST = '/soundList'
    STATISTIC = '/statistic'
    UNIT = '/app/saveunit'
    UPDATESETTING = '/updateSettings'
    USERDETAILS = '/user/details2'
    W5 = '/w5/deviceData'

class FeederSetting(StrEnum):

    CHILDLOCK = 'manualLock'
    DISPENSETONE = 'feedSound'
    DONOTDISTURB = 'disturbMode'
    INDICATORLIGHT = 'lightMode'
    MINICHILDLOCK = 'settings.manualLock'
    MINIINDICATORLIGHT = 'settings.lightMode'
    SELECTEDSOUND = 'selectedSound'
    SHORTAGEALARM = 'foodWarn'
    SOUNDENABLE = 'soundEnable'
    SURPLUS = 'surplus'
    SURPLUSCONTROL = 'surplusControl'
    SYSTEMSOUND = 'systemSoundEnable'
    VOLUME = 'volume'


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


class LitterBoxCommand(StrEnum):

    POWER = 'power'
    STARTCLEAN = 'start_clean'
    PAUSECLEAN = 'stop_clean'
    RESUMECLEAN = 'continue_clean'
    ODORREMOVAL = 'start_odor'
    RESETDEODOR = 'reset_odor'


class LitterBoxCommandKey(StrEnum):

    POWER = 'power_action'
    START = 'start_action'
    STOP = 'stop_action'
    CONTINUE = 'continue_action'


class LitterBoxCommandType(StrEnum):

    POWER = 'power'
    START = 'start'
    STOP = 'stop'
    CONTINUE = 'continue'


class LitterBoxSetting(StrEnum):

    AUTOCLEAN = 'autoWork'
    AUTOODOR = 'autoRefresh'
    AVOIDREPEATCLEAN = 'avoidRepeat'
    CHILDLOCK = 'manualLock'
    CLEANINTERVAL = 'autoIntervalMin'
    DELAYCLEANTIME = 'stillTime'
    DISABLELIGHTWEIGHT = 'underweight'
    DISPLAY = 'lightMode'
    DONOTDISTURB = 'disturbMode'
    KITTENMODE = 'kitten'
    PERIODICCLEAN = 'fixedTimeClear'
    PERIODICODOR = 'fixedTimeRefresh'
    SANDTYPE = 'sandType'

class PetSetting(StrEnum):

    WEIGHT ='weight'

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
FEEDER_LIST = ['D3', 'D4', 'FeederMini']
LITTER_LIST = ['T3']
WATER_FOUNTAIN_LIST = ['W5']

LB_CMD_TO_KEY = {
    LitterBoxCommand.POWER: LitterBoxCommandKey.POWER,
    LitterBoxCommand.STARTCLEAN: LitterBoxCommandKey.START,
    LitterBoxCommand.PAUSECLEAN: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUMECLEAN: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.ODORREMOVAL: LitterBoxCommandKey.START,
    LitterBoxCommand.RESETDEODOR: LitterBoxCommandKey.START
}

LB_CMD_TO_TYPE = {
    LitterBoxCommand.POWER: LitterBoxCommandType.POWER,
    LitterBoxCommand.STARTCLEAN: LitterBoxCommandType.START,
    LitterBoxCommand.PAUSECLEAN: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUMECLEAN: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.ODORREMOVAL: LitterBoxCommandType.START,
    LitterBoxCommand.RESETDEODOR: LitterBoxCommandType.START,
}

LB_CMD_TO_VALUE = {
    LitterBoxCommand.STARTCLEAN: 0,
    LitterBoxCommand.PAUSECLEAN: 0,
    LitterBoxCommand.RESUMECLEAN: 0,
    LitterBoxCommand.ODORREMOVAL: 2,
    LitterBoxCommand.RESETDEODOR: 6,
}

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
