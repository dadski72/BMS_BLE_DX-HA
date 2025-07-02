"""Switch platform for BLE Battery Management System integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BTBmsConfigEntry
from .const import DOMAIN, LOGGER
from .coordinator import BTBmsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: BTBmsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    coordinator = config_entry.runtime_data
    
    LOGGER.debug("Setting up switch platform for BMS: %s", 
                 coordinator.bms.__class__.__module__)
    
    # Add discharge switch for any BMS that has discharge control methods
    if (hasattr(coordinator.bms, "enable_discharge") and 
        hasattr(coordinator.bms, "disable_discharge")):
        LOGGER.debug("Adding discharge control switch for BMS: %s", 
                     coordinator.bms.__class__.__name__)
        async_add_entities([
            BTBmsDischargeSwitch(
                coordinator, format_mac(config_entry.unique_id)
            )
        ])
    else:
        LOGGER.debug("BMS %s does not support discharge control", 
                     coordinator.bms.__class__.__name__)


class BTBmsDischargeSwitch(CoordinatorEntity[BTBmsCoordinator], SwitchEntity):
    """Representation of a BMS discharge switch."""

    def __init__(
        self, coordinator: BTBmsCoordinator, unique_id: str
    ) -> None:
        """Initialize the switch."""
        self._attr_unique_id = f"{DOMAIN}-{unique_id}-discharge_control"
        self._attr_device_info = coordinator.device_info
        self._attr_has_entity_name = True
        self._attr_name = "Discharge Control"
        self._attr_icon = "mdi:battery-arrow-down"
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return true if discharge is enabled."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("battery_discharging_state", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on discharge."""
        if hasattr(self.coordinator.bms, "enable_discharge"):
            success = await self.coordinator.bms.enable_discharge()
            if success:
                await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off discharge."""
        if hasattr(self.coordinator.bms, "disable_discharge"):
            success = await self.coordinator.bms.disable_discharge()
            if success:
                await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and hasattr(self.coordinator.bms, "enable_discharge")
            and hasattr(self.coordinator.bms, "disable_discharge")
        )
