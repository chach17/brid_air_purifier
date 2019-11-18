"""Support for Homekit sensors."""
from homeassistant.const import TEMP_FAHRENHEIT, TEMP_CELSIUS

from . import KNOWN_DEVICES, HomeKitEntity
from . import const
from homeassistant.const import DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY
import logging

_LOGGER = logging.getLogger(__name__)

BRIGHTNESS_ICON = "mdi:brightness-6"
ICON_AIR_FILTER = "mdi:air-filter"
ICON_AIR_QUALITY = "mdi:air-purifier"
ICON_BRID_MODE = "mdi:dip-switch"
ICON_BRID_NWF_FILTER = "mdi:air-filter"
ICON_BRID_HONEYCOMB_FILTER = "mdi:hexagon-multiple"
ICON_BRID_MODULE_COUNT = "mdi:database"
ICON_TEMPERATURE = "mdi:thermometer"
ICON_HUMIDITY = "mdi:water-percent"
ICON_CARBON_MONOXIDE = "mdi:skull-crossbones"

CO2_ICON = "periodic-table-co2"
MODE_ICON = "dip-switch"

UNIT_PERCENT = "%"
UNIT_LUX = "lux"
UNIT_PPM = "ppm"

# Mapping from Homekit air-quality levels
AIR_QUALITY_LEVELS = {
    0: 'Unknown',
    1: 'Excellent',
    2: 'Good',
    3: 'Fair',
    4: 'Inferior',
    5: 'Poor'
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    def set_mode(call):
        entity_id = call.data.get('entity_id')
        mode = call.data.get('mode')

        entity_object = hass.data.get(const.KNOWN_ENTITIES)[entity_id]
        if entity_object is not None:
            hass.async_create_task(
                entity_object.set_mode(mode)
            )

    """Set up Homekit sensor support."""
    hass.data[const.KNOWN_ENTITIES] = {}
    if discovery_info is not None:
        accessory = hass.data[const.KNOWN_DEVICES][discovery_info['serial']]
        devtype = discovery_info['device-type']

        if devtype == 'humidity':
            add_entities(
                [BridHumiditySensor(accessory, discovery_info)], True)
        elif devtype == 'temperature':
            add_entities(
                [BridTemperatureSensor(accessory, discovery_info)], True)
        elif devtype == 'air-quality':
            add_entities(
                [BridAirQualitySensor(accessory, discovery_info)], True)
        elif devtype == 'carbon-monoxide':
            add_entities(
                [BridCarbonMonoxideSensor(accessory, discovery_info)], True)
        elif devtype == 'filter-maintenance':
            add_entities([BridFilterReplacementSensor(accessory, discovery_info)], True)
        elif devtype == 'air-purifier':
            brid_mode_sensor = BridModeSensor(accessory, discovery_info)
            brid_module_sensor = BridModuleSensor(accessory, discovery_info)
            add_entities([brid_mode_sensor, brid_module_sensor], True)
            while True:
                if brid_mode_sensor.entity_id is not None:
                    break

            _LOGGER.debug("Added Brid With Entity ID: %s", brid_mode_sensor.entity_id)
            hass.data[const.KNOWN_ENTITIES][brid_mode_sensor.entity_id] = brid_mode_sensor
            hass.services.register(const.DOMAIN, 'set_mode', set_mode)


class BridFilterReplacementSensor(HomeKitEntity):
    """Representation of a Homekit humidity sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None

    def get_characteristic_types(self):
        return [
            const.UUID_FILTER_LIFE_LEVEL
        ]

    def _setup_filter_life_level(self, char):
        self._filter_type = char['description']

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._filter_type

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {} {}".format(super().name, self._filter_type, "Filter Change")

    @property
    def icon(self):
        """Return the sensor icon."""
        if self._filter_type == 'NWF Filter Life Level':
            return ICON_BRID_NWF_FILTER
        else:
            return ICON_BRID_HONEYCOMB_FILTER

    @property
    def unit_of_measurement(self):
        """Return units for the sensor."""
        return UNIT_PERCENT

    def _update_filter_life_level(self, value):
        self._state = value

    @property
    def state(self):
        """Return the current value."""
        return round(self._state, 1)


class BridHumiditySensor(HomeKitEntity):
    """Representation of a Homekit humidity sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None

    def get_characteristic_types(self):
        """Define the homekit characteristics the entity is tracking."""
        return [
            const.UUID_RELATIVE_HUMIDITY
        ]

    @property
    def device_class(self) -> str:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_HUMIDITY

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(super().name, "Humidity")

    @property
    def icon(self):
        """Return the sensor icon."""
        return ICON_HUMIDITY

    @property
    def unit_of_measurement(self):
        """Return units for the sensor."""
        return UNIT_PERCENT

    def _update_relative_humidity_current(self, value):
        self._state = value

    @property
    def state(self):
        """Return the current humidity."""
        return self._state


class BridModuleSensor(HomeKitEntity):
    """Representation of a Homekit humidity sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None

    def get_characteristic_types(self):
        return [
            const.UUID_BRID_NUMBER_OF_MODULES
        ]

    def _short_name_for_characteristic(self, char):
        if char['type'] == const.UUID_BRID_NUMBER_OF_MODULES:
            return "module_count"
        else:
            return super()._short_name_for_characteristic(char)

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(super().name, "Module Count")

    @property
    def icon(self):
        """Return the sensor icon."""
        return ICON_BRID_MODULE_COUNT

    @property
    def unique_id(self):
        return 'module_count'

    def _update_module_count(self, value):
        self._state = value

    @property
    def state(self):
        """Return the current humidity."""
        return self._state


class BridModeSensor(HomeKitEntity):
    """Representation of a Homekit humidity sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None
        self._number_of_modules = 0

    def get_characteristic_types(self):
        return [
            const.UUID_BRID_MODE
        ]

    def _short_name_for_characteristic(self, char):
        if char['type'] == const.UUID_BRID_MODE:
            return "mode"
        else:
            return super()._short_name_for_characteristic(char)

    async def set_mode(self, mode):
        """Turn the specified switch on."""
        characteristics = [{'aid': self._aid,
                            'iid': self._chars['mode'],
                            'value': mode}]

        await self._accessory.put_characteristics(characteristics)
        self._update_mode(mode)

    @property
    def unique_id(self):
        return 'mode'

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(super().name, "Mode")

    @property
    def icon(self):
        """Return the sensor icon."""
        return ICON_BRID_MODE

    def _update_mode(self, value):
        self._state = const.BRID_MODES[value]

    @property
    def state(self):
        """Return the current humidity."""
        return self._state


class BridTemperatureSensor(HomeKitEntity):
    """Representation of a Homekit temperature sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None

    def get_characteristic_types(self):
        """Define the homekit characteristics the entity is tracking."""
        return [
            const.UUID_TEMPERATURE_CURRENT
        ]

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(super().name, "Temperature")

    @property
    def icon(self):
        """Return the sensor icon."""
        return ICON_TEMPERATURE

    @property
    def device_class(self) -> str:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return units for the sensor."""
        return TEMP_CELSIUS

    def _update_temperature_current(self, value):
        self._state = value

    @property
    def state(self):
        """Return the current temperature in Celsius."""
        return round(self._state, 1)


class BridAirQualitySensor(HomeKitEntity):
    """Representation of a Homekit light level sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None

    def get_characteristic_types(self):
        """Define the homekit characteristics the entity is tracking."""
        # pylint: disable=import-error
        from homekit.model.characteristics import CharacteristicsTypes

        return [
            const.UUID_AIR_QUALITY
        ]

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(super().name, "Air Quality")

    @property
    def icon(self):
        """Return the sensor icon."""
        return ICON_AIR_QUALITY

    def _update_air_quality(self, value):
        self._state = value

    @property
    def state(self):
        """Return the current light level in lux."""
        return AIR_QUALITY_LEVELS.get(self._state, None)


class BridCarbonMonoxideSensor(HomeKitEntity):
    """Representation of a Homekit light level sensor."""

    def __init__(self, *args):
        """Initialise the entity."""
        super().__init__(*args)
        self._state = None

    def get_characteristic_types(self):
        """Define the homekit characteristics the entity is tracking."""
        # pylint: disable=import-error
        from homekit.model.characteristics import CharacteristicsTypes

        return [
            const.UUID_CARBON_MONOXIDE_LEVEL
        ]

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(super().name, "Carbon Monoxide")

    @property
    def device_class(self) -> str:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return "co"

    @property
    def icon(self):
        """Return the sensor icon."""
        return ICON_CARBON_MONOXIDE

    @property
    def unit_of_measurement(self):
        """Return units for the sensor."""
        return UNIT_PPM

    def _update_carbon_monoxide_level(self, value):
        self._state = value

    @property
    def state(self):
        """Return the current light level in lux."""
        return self._state
