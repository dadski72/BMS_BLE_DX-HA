"""Test BMS discharge switch."""

from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

from custom_components.bms_ble.const import ATTR_DISCHRG_MOSFET
from custom_components.bms_ble.coordinator import BTBmsCoordinator
from custom_components.bms_ble.switch import BTBmsDischargeSwitch, async_setup_entry
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


class DeviceWithDischarge:
    """Test device with discharge control methods."""

    def __init__(self, result: bool = True) -> None:
        """Initialize the device."""
        self.result = result
        self.enable_discharge = AsyncMock(return_value=result)
        self.disable_discharge = AsyncMock(return_value=result)


def coordinator(device, data=None, last_update_success: bool = True):
    """Return a minimal coordinator for switch tests."""
    return SimpleNamespace(
        async_request_refresh=AsyncMock(),
        data=data,
        device=device,
        device_info={},
        last_update_success=last_update_success,
    )


async def test_switch_setup(hass: HomeAssistant) -> None:
    """Test switch entity setup."""
    device = DeviceWithDischarge()
    config_entry = cast(
        "ConfigEntry[BTBmsCoordinator]",
        SimpleNamespace(
            runtime_data=coordinator(device),
            unique_id="cc:cc:cc:cc:cc:cc",
        ),
    )
    entities: list[BTBmsDischargeSwitch] = []

    def add_entities(new_entities, update_before_add: bool = False) -> None:
        entities.extend(new_entities)

    await async_setup_entry(hass, config_entry, cast("AddEntitiesCallback", add_entities))

    assert len(entities) == 1
    assert entities[0].unique_id == "bms_ble-cc:cc:cc:cc:cc:cc-battery_discharging"

    config_entry = cast(
        "ConfigEntry[BTBmsCoordinator]",
        SimpleNamespace(
            runtime_data=coordinator(object()),
            unique_id="cc:cc:cc:cc:cc:cc",
        ),
    )
    entities.clear()

    await async_setup_entry(hass, config_entry, cast("AddEntitiesCallback", add_entities))

    assert entities == []


async def test_switch_state_and_commands() -> None:
    """Test switch state and discharge commands."""
    device = DeviceWithDischarge()
    coord = coordinator(device, {ATTR_DISCHRG_MOSFET: True})
    switch = BTBmsDischargeSwitch(coord, "cc:cc:cc:cc:cc:cc")

    assert switch.is_on is True
    assert switch.available is True
    assert switch.entity_category is EntityCategory.CONFIG

    await switch.async_turn_on()
    device.enable_discharge.assert_awaited_once()
    coord.async_request_refresh.assert_awaited_once()

    coord.async_request_refresh.reset_mock()
    await switch.async_turn_off()
    device.disable_discharge.assert_awaited_once()
    coord.async_request_refresh.assert_awaited_once()

    coord.data = {}
    assert switch.is_on is None

    coord.data = {ATTR_DISCHRG_MOSFET: 1}
    assert switch.is_on is None

    coord.last_update_success = False
    assert switch.available is False


async def test_switch_command_failures() -> None:
    """Test switch command failure paths."""
    device = DeviceWithDischarge(result=False)
    coord = coordinator(device)
    switch = BTBmsDischargeSwitch(coord, "cc:cc:cc:cc:cc:cc")

    await switch.async_turn_on()
    await switch.async_turn_off()

    coord.async_request_refresh.assert_not_awaited()

    coord.device = object()

    await switch.async_turn_on()
    await switch.async_turn_off()

    assert switch.available is False
