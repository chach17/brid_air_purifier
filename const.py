"""Constants for the homekit_controller component."""
DOMAIN = 'brid_air_purifier'

KNOWN_ENTITIES = "{}-entities".format(DOMAIN)
KNOWN_DEVICES = "{}-devices".format(DOMAIN)
CONTROLLER = "{}-controller".format(DOMAIN)

HOMEKIT_DIR = '.brid_air_purifier'
PAIRING_FILE = 'pairing.json'

UUID_RELATIVE_HUMIDITY = "00000010-0000-1000-8000-0026BB765291"
UUID_AIR_QUALITY = "00000095-0000-1000-8000-0026BB765291"
UUID_FILTER_CHANGE_INDICATION = "000000AC-0000-1000-8000-0026BB765291"
UUID_FILTER_LIFE_LEVEL = "000000AB-0000-1000-8000-0026BB765291"
UUID_CARBON_MONOXIDE_LEVEL = "00000090-0000-1000-8000-0026BB765291"
UUID_CARBON_MONOXIDE_DETECTED = "00000069-0000-1000-8000-0026BB765291"
UUID_TEMPERATURE_CURRENT = "00000011-0000-1000-8000-0026BB765291"
UUID_BRID_MODE = "34ACFBA1-D9FB-11E7-8F1A-0800200C9A66"
UUID_BRID_NUMBER_OF_MODULES = "65DFBA32-EBD2-11E7-8F1A-0800200C9A66"


# Mapping from Homekit type to component.
HOMEKIT_ACCESSORY_DISPATCH = {
    'humidity': 'sensor',
    'temperature': 'sensor',
    'air-quality': 'sensor',
    'carbon-monoxide': 'sensor',
    'air-purifier': 'sensor',
    'filter-maintenance': 'sensor'
}

BRID_MODES = {
    0: 'Off',
    1: 'Smart',
    2: 'Auto',
    3: 'Boost',
    4: 'Night'
}
