"""Switch platform for BLE Battery Management System integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BTBmsConfigEntry
from .const import ATTR_DISCHRG_MOSFET, DOMAIN, LOGGER
from .coordinator import BTBmsCoordinator


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: BTBmsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    coordinator = config_entry.runtime_data

    if hasattr(coordinator.device, "enable_discharge") and hasattr(
        coordinator.device, "disable_discharge"
    ):
        async_add_entities(
            [BTBmsDischargeSwitch(coordinator, format_mac(config_entry.unique_id))]
        )


class BTBmsDischargeSwitch(CoordinatorEntity[BTBmsCoordinator], SwitchEntity):
    """Representation of a BMS discharge switch."""

    def __init__(
        self, coordinator: BTBmsCoordinator, unique_id: str
    ) -> None:
        """Initialize the switch."""
        self._attr_unique_id = f"{DOMAIN}-{unique_id}-battery_discharging"
        self._attr_device_info = coordinator.device_info
        self._attr_has_entity_name = True
        self._attr_name = "Battery discharging"
        self._attr_icon = "mdi:battery-arrow-down"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_class = None
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return true if discharge is enabled."""
        if not self.coordinator.data:
            return None

        discharge_state = self.coordinator.data.get(ATTR_DISCHRG_MOSFET)
        if isinstance(discharge_state, bool):
            return discharge_state

        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on discharge."""
        if hasattr(self.coordinator.device, "enable_discharge"):
            success = await self.coordinator.device.enable_discharge()
            if success:
                await self.coordinator.async_request_refresh()
            else:
                LOGGER.warning("Failed to enable discharge")
        else:
            LOGGER.error("BMS does not have enable_discharge method!")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off discharge."""
        if hasattr(self.coordinator.device, "disable_discharge"):
            success = await self.coordinator.device.disable_discharge()
            if success:
                await self.coordinator.async_request_refresh()
            else:
                LOGGER.warning("Failed to disable discharge")
        else:
            LOGGER.error("BMS does not have disable_discharge method!")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and hasattr(self.coordinator.device, "enable_discharge")
            and hasattr(self.coordinator.device, "disable_discharge")
        )
