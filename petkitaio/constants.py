"""Constants for PetKitAIO"""

from .str_enum import StrEnum

class Region(StrEnum):

    US = 'http://api.petkt.com/latest/'
    ASIA = 'http://api.petktasia.com/latest/'
    CN = 'http://api.petkit.cn/6/'


class Endpoint(StrEnum):

    BLE_CANCEL = 'ble/cancel'
    BLE_CONNECT = 'ble/connect'
    BLE_DEVICES = 'ble/ownSupportBleDevices'
    BLE_POLL = 'ble/poll'
    CALL_PET = 'callPet'
    CANCEL_FEED = 'cancelRealtimeFeed'
    CONTROL_DEVICE = 'controlDevice'
    CONTROL_WF = 'ble/controlDevice'
    DEVICE_DETAIL = 'device_detail'
    DEVICE_RECORD = 'getDeviceRecord'
    DEVICE_ROSTER = 'discovery/device_roster_v2'
    FAMILY_LIST = 'group/family/list'
    FEEDER_DESICCANT_RESET = 'desiccantReset'
    FRESH_ELEMENT_CALIBRATION = 'food_reset'
    FRESH_ELEMENT_CANCEL_FEED = 'cancel_realtime_feed'
    FRESH_ELEMENT_DESICCANT_RESET = 'feeder/desiccant_reset'
    FRESH_ELEMENT_MANUAL_FEED = 'feeder/save_dailyfeed'
    FRESH_ELEMENT_SETTING = 'feeder/update'
    LOGIN = 'user/login'
    MANUAL_FEED = 'saveDailyFeed'
    MAX_ODOR_RESET = 'deodorantReset'
    MINI_DESICCANT_RESET = 'feedermini/desiccant_reset'
    MINI_MANUAL_FEED = 'feedermini/save_dailyfeed'
    MINI_SETTING = 'feedermini/update'
    PET_PROPS = 'pet/updatepetprops'
    REFRESH_HOME = 'discovery/refreshHome'
    REPLENISHED_FOOD = 'added'
    SOUND_LIST = 'soundList'
    STATISTIC = 'statistic'
    UNIT = 'app/saveunit'
    UPDATE_SETTING = 'updateSettings'
    USER_DETAILS = 'user/details2'
    W5 = 'w5/deviceData'

class FeederSetting(StrEnum):

    CHILD_LOCK = 'manualLock'
    DISPENSE_TONE = 'feedSound'
    DO_NOT_DISTURB = 'disturbMode'
    FEED_TONE = 'feedTone'
    FRESH_ELEMENT_CHILD_LOCK = 'settings.manualLock'
    FRESH_ELEMENT_INDICATOR_LIGHT = 'settings.lightMode'
    INDICATOR_LIGHT = 'lightMode'
    MIN_EAT_DURATION = 'shortest'
    MINI_CHILD_LOCK = 'settings.manualLock'
    MINI_INDICATOR_LIGHT = 'settings.lightMode'
    SELECTED_SOUND = 'selectedSound'
    SHORTAGE_ALARM = 'foodWarn'
    SOUND_ENABLE = 'soundEnable'
    SURPLUS = 'surplus'
    SURPLUS_CONTROL = 'surplusControl'
    SYSTEM_SOUND = 'systemSoundEnable'
    VOLUME = 'volume'


class Header(StrEnum):

    ACCEPT = '*/*'
    X_TIMEZONE = '-5.0'
    ACCEPT_LANG = 'en-US;q=1, it-US;q=0.9'
    ENCODING = 'gzip, deflate'
    API_VERSION = '11.2.1'
    CONTENT_TYPE = 'application/x-www-form-urlencoded'
    AGENT = 'PETKIT/11.2.1 (iPhone; iOS 15.1; Scale/3.00)'
    TZ = 'America/New_York'
    CLIENT = 'ios(15.1;iPhone14,3)'
    LOCALE = 'en_US'


class FeederCommand(StrEnum):

    START_CALIBRATION = 'Start calibration'
    STOP_CALIBRATION = 'Stop calibration'

class LitterBoxCommand(StrEnum):

    LIGHT_ON = 'light_on'
    ODOR_REMOVAL = 'start_odor'
    PAUSE_CLEAN = 'stop_clean'
    POWER = 'power'
    RESET_DEODOR = 'reset_deodorizer'
    RESUME_CLEAN = 'continue_clean'
    START_CLEAN = 'start_clean'
    START_MAINTENANCE = 'start_maintenance'
    EXIT_MAINTENANCE = 'exit_maintenance'
    PAUSE_MAINTENANCE_EXIT = 'pause_maintenance_exit'
    RESUME_MAINTENANCE_EXIT = 'resume_maintenance_exit'
    DUMP_LITTER = 'dump_litter'
    PAUSE_LITTER_DUMP = 'pause_litter_dump'
    RESUME_LITTER_DUMP = 'resume_litter_dump'
    RESET_MAX_DEODOR = 'reset_max_deodorizer'


class LitterBoxCommandKey(StrEnum):

    CONTINUE = 'continue_action'
    END = 'end_action'
    POWER = 'power_action'
    START = 'start_action'
    STOP = 'stop_action'


class LitterBoxCommandType(StrEnum):

    CONTINUE = 'continue'
    END = 'end'
    POWER = 'power'
    START = 'start'
    STOP = 'stop'


class LitterBoxSetting(StrEnum):

    AUTO_CLEAN = 'autoWork'
    AUTO_ODOR = 'autoRefresh'
    AVOID_REPEAT_CLEAN = 'avoidRepeat'
    CHILD_LOCK = 'manualLock'
    CLEAN_INTERVAL = 'autoIntervalMin'
    CONT_ROTATION = 'downpos'
    DEEP_CLEAN = 'deepClean'
    DEEP_REFRESH = 'deepRefresh'
    DELAY_CLEAN_TIME = 'stillTime'
    DISABLE_LIGHT_WEIGHT = 'underweight'
    DISPLAY = 'lightMode'
    DO_NOT_DISTURB = 'disturbMode'
    ENHANCED_ADSORPTION = 'bury'
    KITTEN_MODE = 'kitten'
    PERIODIC_CLEAN = 'fixedTimeClear'
    PERIODIC_ODOR = 'fixedTimeRefresh'
    SAND_TYPE = 'sandType'

class PetSetting(StrEnum):

    WEIGHT = 'weight'

class PurifierSetting(StrEnum):

    LIGHT = 'lightMode'
    SOUND = 'sound'

class PurifierCommand(StrEnum):

    POWER = 'power'
    AUTO_MODE = 'auto_mode'
    SILENT_MODE = 'silent_mode'
    STANDARD_MODE = 'standard_mode'
    STRONG_MODE = 'strong_mode'

class PurifierCommandKey(StrEnum):

    POWER = 'power_action'
    MODE = 'mode_action'

class PurifierCommandType(StrEnum):

    POWER = 'power'
    MODE = 'mode'

class W5Command(StrEnum):

    PAUSE = 'Pause'
    NORMAL_TO_PAUSE = 'Normal To Pause'
    SMART_TO_PAUSE = 'Smart To Pause'
    NORMAL = 'Normal'
    SMART = 'Smart'
    RESET_FILTER = 'Reset Filter'
    DO_NOT_DISTURB = 'Do Not Disturb'
    DO_NOT_DISTURB_OFF = 'Do Not Disturb Off'
    FIRST_BLE_CMND = 'First BLE Command'
    SECOND_BLE_CMND = 'Second BLE Command'
    LIGHT_LOW = 'Light Low'
    LIGHT_MEDIUM = 'Light Medium'
    LIGHT_HIGH = 'Light High'
    LIGHT_ON = 'Light On'
    LIGHT_OFF = 'Light Off'


TIMEOUT = 5 * 60

CLIENT_DICT = {
    "locale":"en-US",
    "source":"app.petkit-ios-oversea",
    "platform":"ios",
    "osVersion":"15.1",
    "timezone":"-5.0",
    "timezoneId":"America/New_York",
    "version":"11.2.1",
    "token":"",
    "name":"iPhone14,3"
}

ASIA_REGIONS = [
    'AF',
    'AL',
    'AZ',
    'BH',
    'BD',
    'BT',
    'BN',
    'KH',
    'CN',
    'CY',
    'VA',
    'HK',
    'IN',
    'ID',
    'IR',
    'IQ',
    'IL',
    'JP',
    'JO',
    'KZ',
    'KP',
    'KR',
    'KW',
    'KG',
    'LA',
    'LB',
    'LU',
    'MO',
    'MY',
    'MV',
    'MN',
    'MM',
    'NP',
    'OM',
    'PK',
    'PH',
    'QA',
    'SA',
    'SG',
    'SY',
    'TW',
    'TJ',
    'TH',
    'TL',
    'TM',
    'AE',
    'VN',
    'YE'
]

AUTH_ERROR_CODES = {
    122: 'PetKit username/email or password is incorrect',
    5: 'Login session expired. Your account can only be signed in on one device.',
    125: 'Unregistered e-mail address. The region selected may not be the correct one associated with your account.'
}

BLUETOOTH_ERRORS = {
    3003: 'Bluetooth connection failed. Retrying on next update.'
}

SERVER_ERROR_CODES = {
    1: 'PetKit servers are busy. Please try again later.',
    99: 'PetKit servers are undergoing maintenance. Please try again later.'
}

BLE_HEADER = [-6, -4, -3]
FEEDER_LIST = ['D3', 'D4', 'D4s', 'Feeder', 'FeederMini']
LITTER_LIST = ['T3', 'T4']
PURIFIER_LIST = ['K2']
WATER_FOUNTAIN_LIST = ['W5']

LB_CMD_TO_KEY = {
    LitterBoxCommand.LIGHT_ON: LitterBoxCommandKey.START,
    LitterBoxCommand.POWER: LitterBoxCommandKey.POWER,
    LitterBoxCommand.START_CLEAN: LitterBoxCommandKey.START,
    LitterBoxCommand.PAUSE_CLEAN: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUME_CLEAN: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.ODOR_REMOVAL: LitterBoxCommandKey.START,
    LitterBoxCommand.RESET_DEODOR: LitterBoxCommandKey.START,
    LitterBoxCommand.START_MAINTENANCE: LitterBoxCommandKey.START,
    LitterBoxCommand.EXIT_MAINTENANCE: LitterBoxCommandKey.END,
    LitterBoxCommand.PAUSE_MAINTENANCE_EXIT: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUME_MAINTENANCE_EXIT: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.DUMP_LITTER: LitterBoxCommandKey.START,
    LitterBoxCommand.PAUSE_LITTER_DUMP: LitterBoxCommandKey.STOP,
    LitterBoxCommand.RESUME_LITTER_DUMP: LitterBoxCommandKey.CONTINUE,
    LitterBoxCommand.RESET_MAX_DEODOR: LitterBoxCommandKey.START,
}

LB_CMD_TO_TYPE = {
    LitterBoxCommand.LIGHT_ON: LitterBoxCommandType.START,
    LitterBoxCommand.POWER: LitterBoxCommandType.POWER,
    LitterBoxCommand.START_CLEAN: LitterBoxCommandType.START,
    LitterBoxCommand.PAUSE_CLEAN: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUME_CLEAN: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.ODOR_REMOVAL: LitterBoxCommandType.START,
    LitterBoxCommand.RESET_DEODOR: LitterBoxCommandType.START,
    LitterBoxCommand.START_MAINTENANCE: LitterBoxCommandType.START,
    LitterBoxCommand.EXIT_MAINTENANCE: LitterBoxCommandType.END,
    LitterBoxCommand.PAUSE_MAINTENANCE_EXIT: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUME_MAINTENANCE_EXIT: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.DUMP_LITTER: LitterBoxCommandType.START,
    LitterBoxCommand.PAUSE_LITTER_DUMP: LitterBoxCommandType.STOP,
    LitterBoxCommand.RESUME_LITTER_DUMP: LitterBoxCommandType.CONTINUE,
    LitterBoxCommand.RESET_MAX_DEODOR: LitterBoxCommandType.START,
}

LB_CMD_TO_VALUE = {
    LitterBoxCommand.LIGHT_ON: 7,
    LitterBoxCommand.START_CLEAN: 0,
    LitterBoxCommand.PAUSE_CLEAN: 0,
    LitterBoxCommand.RESUME_CLEAN: 0,
    LitterBoxCommand.ODOR_REMOVAL: 2,
    LitterBoxCommand.RESET_DEODOR: 6,
    LitterBoxCommand.START_MAINTENANCE: 9,
    LitterBoxCommand.EXIT_MAINTENANCE: 9,
    LitterBoxCommand.PAUSE_MAINTENANCE_EXIT: 9,
    LitterBoxCommand.RESUME_MAINTENANCE_EXIT: 9,
    LitterBoxCommand.DUMP_LITTER: 1,
    LitterBoxCommand.PAUSE_LITTER_DUMP: 1,
    LitterBoxCommand.RESUME_LITTER_DUMP: 1,
    LitterBoxCommand.RESET_MAX_DEODOR: 8,
}

PUR_CMD_TO_KEY = {
    PurifierCommand.POWER: PurifierCommandKey.POWER,
    PurifierCommand.AUTO_MODE: PurifierCommandKey.MODE,
    PurifierCommand.SILENT_MODE: PurifierCommandKey.MODE,
    PurifierCommand.STANDARD_MODE: PurifierCommandKey.MODE,
    PurifierCommand.STRONG_MODE: PurifierCommandKey.MODE
}

PUR_CMD_TO_TYPE = {
    PurifierCommand.POWER: PurifierCommandType.POWER,
    PurifierCommand.AUTO_MODE: PurifierCommandType.MODE,
    PurifierCommand.SILENT_MODE: PurifierCommandType.MODE,
    PurifierCommand.STANDARD_MODE: PurifierCommandType.MODE,
    PurifierCommand.STRONG_MODE: PurifierCommandType.MODE
}

PUR_CMD_TO_VALUE = {
    PurifierCommand.AUTO_MODE: 0,
    PurifierCommand.SILENT_MODE: 1,
    PurifierCommand.STANDARD_MODE: 2,
    PurifierCommand.STRONG_MODE: 3
}

W5_COMMAND_TO_CODE = {
    W5Command.DO_NOT_DISTURB: '221',
    W5Command.DO_NOT_DISTURB_OFF: '221',
    W5Command.LIGHT_ON: '221',
    W5Command.LIGHT_OFF: '221',
    W5Command.LIGHT_LOW: '221',
    W5Command.LIGHT_MEDIUM: '221',
    W5Command.LIGHT_HIGH: '221',
    W5Command.PAUSE: '220',
    W5Command.RESET_FILTER: '222',
    W5Command.NORMAL: '220',
    W5Command.NORMAL_TO_PAUSE: '220',
    W5Command.SMART: '220',
    W5Command.SMART_TO_PAUSE: '220',
}

W5_DND_COMMANDS = [W5Command.DO_NOT_DISTURB, W5Command.DO_NOT_DISTURB_OFF]
W5_LIGHT_BRIGHTNESS = [W5Command.LIGHT_LOW, W5Command.LIGHT_MEDIUM, W5Command.LIGHT_HIGH]
W5_LIGHT_POWER = [W5Command.LIGHT_ON, W5Command.LIGHT_OFF]
W5_MODE = [W5Command.NORMAL, W5Command.SMART, W5Command.NORMAL_TO_PAUSE, W5Command.SMART_TO_PAUSE]
W5_SETTINGS_COMMANDS = [
    W5Command.DO_NOT_DISTURB,
    W5Command.DO_NOT_DISTURB_OFF,
    W5Command.LIGHT_LOW,
    W5Command.LIGHT_MEDIUM,
    W5Command.LIGHT_HIGH,
    W5Command.LIGHT_ON,
    W5Command.LIGHT_OFF,
]
