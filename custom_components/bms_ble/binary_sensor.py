"""Support for BMS_BLE binary sensors."""

from collections.abc import Callable

from aiobmsble import BMSMode, BMSSample

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import ATTR_BATTERY_CHARGING, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BTBmsConfigEntry
from .const import (
    ATTR_BALANCER,
    ATTR_BATTERY_MODE,
    ATTR_CELL_COUNT,
    ATTR_CELLS,
    ATTR_CHRG_MOSFET,
    ATTR_CONNECTED,
    ATTR_DISCHRG_MOSFET,
    ATTR_HEATER,
    ATTR_LQ,
    ATTR_PROBLEM,
    ATTR_PROBLEM_CODE,
    DOMAIN,
)
from .coordinator import BTBmsCoordinator

PARALLEL_UPDATES = 0


class BmsBinaryEntityDescription(BinarySensorEntityDescription, frozen_or_thawed=True):
    """Describes BMS sensor entity."""

    attr_fn: Callable[[BMSSample], dict[str, int | str]] | None = None


BINARY_SENSOR_TYPES: list[BmsBinaryEntityDescription] = [
    BmsBinaryEntityDescription(
        attr_fn=lambda data: (
            {
                ATTR_BATTERY_MODE: data.get(
                    ATTR_BATTERY_MODE, BMSMode.UNKNOWN
                ).name.lower()
            }
            if ATTR_BATTERY_MODE in data
            else {}
        ),
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        key=ATTR_BATTERY_CHARGING,
    ),
    BmsBinaryEntityDescription(
        attr_fn=lambda data: (
            {
                ATTR_CELLS: f"{data.get(ATTR_BALANCER, 0):0{data.get(ATTR_CELL_COUNT, 8)}b}"[
                    ::-1
                ]
            }
            if isinstance(data.get(ATTR_BALANCER), int)
            else {}
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        key=ATTR_BALANCER,
        name="Balancer",
        translation_key=ATTR_BALANCER,
    ),
    BmsBinaryEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        key=ATTR_CHRG_MOSFET,
        name="Charge MOSFET",
        translation_key=ATTR_CHRG_MOSFET,
    ),
    BmsBinaryEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        key=ATTR_DISCHRG_MOSFET,
        name="Discharge MOSFET",
        translation_key=ATTR_DISCHRG_MOSFET,
    ),
    BmsBinaryEntityDescription(
        device_class=BinarySensorDeviceClass.HEAT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        key=ATTR_HEATER,
        translation_key=ATTR_HEATER,
    ),
    BmsBinaryEntityDescription(
        attr_fn=lambda data: (
            {ATTR_PROBLEM_CODE: data.get("problem_code", 0)}
            if "problem_code" in data
            else {}
        ),
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        key=ATTR_PROBLEM,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: BTBmsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in Home Assistant."""

    bms: BTBmsCoordinator = config_entry.runtime_data
    mac: str = format_mac(config_entry.unique_id)
    entities: list[BinarySensorEntity] = [BMSConnectionSensor(bms, mac)]
    for descr in BINARY_SENSOR_TYPES:
        if descr.key not in bms.data:
            continue
        entities.append(BMSBinarySensor(bms, descr, mac))
    async_add_entities(entities)


class BMSBinarySensor(CoordinatorEntity[BTBmsCoordinator], BinarySensorEntity):
    """The generic BMS binary sensor implementation."""

    _unrecorded_attributes: frozenset[str] = frozenset({ATTR_CELLS})
    entity_description: BmsBinaryEntityDescription

    def __init__(
        self,
        bms: BTBmsCoordinator,
        descr: BmsBinaryEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize BMS binary sensor."""
        self._attr_unique_id = f"{DOMAIN}-{unique_id}-{descr.key}"
        self._attr_device_info = bms.device_info
        self._attr_has_entity_name = True
        self.entity_description: BmsBinaryEntityDescription = descr
        super().__init__(bms)

    @property
    def available(self) -> bool:
        """Stay available while a previous sample exists, retaining its value.

        Matches the regular BMS sensors: keep the last known state through a
        Bluetooth drop-out instead of going "unavailable". The "Connection"
        binary sensor reports the actual link state.
        """
        return self.coordinator.data is not None

    @property
    def is_on(self) -> bool | None:
        """Handle updated data from the coordinator."""
        return bool(self.coordinator.data.get(self.entity_description.key))

    @property
    def extra_state_attributes(self) -> dict[str, int | str] | None:
        """Return entity specific state attributes, e.g. cell voltages."""
        return (
            fn(self.coordinator.data)
            if (fn := self.entity_description.attr_fn)
            else None
        )


class BMSConnectionSensor(CoordinatorEntity[BTBmsCoordinator], BinarySensorEntity):
    """Reports whether the BMS Bluetooth link is currently up.

    Unlike the data sensors, this entity is always available so that a dropped
    connection is reported as "off" (disconnected) rather than "unavailable".
    """

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, bms: BTBmsCoordinator, unique_id: str) -> None:
        """Initialize the BMS connection sensor."""
        self._attr_unique_id = f"{DOMAIN}-{unique_id}-{ATTR_CONNECTED}"
        self._attr_device_info = bms.device_info
        self._attr_translation_key = ATTR_CONNECTED
        super().__init__(bms)

    @property
    def available(self) -> bool:
        """Always available, so a down link is reported as 'off'."""
        return True

    @property
    def is_on(self) -> bool:
        """Return True while the BMS link is up (last update succeeded)."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, int]:
        """Expose link quality (successful reads over the last 100 attempts)."""
        return {ATTR_LQ: self.coordinator.link_quality}
