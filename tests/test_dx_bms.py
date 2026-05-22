"""Test DX-specific BMS wrappers."""

from typing import cast
from unittest.mock import AsyncMock

from aiobmsble import BMSSample
from aiobmsble.bms.jbd_bms import BMS as JbdBMS
from aiobmsble.bms.redodo_bms import BMS as RedodoBMS
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError
import pytest

from custom_components.bms_ble.dx_bms import custom_bms_module
from custom_components.bms_ble.dx_bms.jbd_bms import BMS as DxJbdBMS
from custom_components.bms_ble.dx_bms.redodo_bms import BMS as DxRedodoBMS

from .bluetooth import generate_ble_device


def test_custom_bms_module() -> None:
    """Test custom BMS module lookup."""
    assert (
        custom_bms_module("aiobmsble.bms.jbd_bms")
        == "custom_components.bms_ble.dx_bms.jbd_bms"
    )
    assert (
        custom_bms_module("custom_components.bms_ble.plugins.redodo_bms")
        == "custom_components.bms_ble.dx_bms.redodo_bms"
    )
    assert custom_bms_module("aiobmsble.bms.dummy_bms") == "aiobmsble.bms.dummy_bms"


def test_redodo_discharging_state(patch_default_bleak_client) -> None:
    """Test Redodo discharge state decoding."""
    bms = DxRedodoBMS(generate_ble_device(address="cc:cc:cc:cc:cc:cc"))

    assert bms._battery_discharging_state() is False

    bms._msg = bytes([0] * 68 + [0x80])
    assert bms._battery_discharging_state() is False

    bms._msg = bytes([0] * 68 + [0x01])
    assert bms._battery_discharging_state() is True


async def test_redodo_async_update(
    monkeypatch: pytest.MonkeyPatch, patch_default_bleak_client
) -> None:
    """Test Redodo update adds discharge state."""
    bms = DxRedodoBMS(generate_ble_device(address="cc:cc:cc:cc:cc:cc"))
    bms._msg = bytes([0] * 68 + [0x01])

    async def mock_update(_self) -> BMSSample:
        return {"voltage": 12.3}

    monkeypatch.setattr(RedodoBMS, "_async_update", mock_update)

    assert await bms._async_update() == {"voltage": 12.3, "dischrg_mosfet": True}


async def test_redodo_discharge_commands(patch_default_bleak_client) -> None:
    """Test Redodo discharge control commands."""
    bms = DxRedodoBMS(generate_ble_device(address="cc:cc:cc:cc:cc:cc"))
    bms._connect = AsyncMock()
    bms._await_msg = AsyncMock()

    assert await bms.enable_discharge() is True
    bms._await_msg.assert_awaited_with(
        DxRedodoBMS._CMD_ENABLE_DISCHARGE, wait_for_notify=False
    )
    assert bms._last_discharge_state is True

    assert await bms.disable_discharge() is True
    bms._await_msg.assert_awaited_with(
        DxRedodoBMS._CMD_DISABLE_DISCHARGE, wait_for_notify=False
    )
    assert bms._last_discharge_state is False

    bms._connect = AsyncMock(side_effect=BleakError("boom"))
    assert await bms.enable_discharge() is False
    assert await bms.disable_discharge() is False


def test_jbd_notification_handler(
    monkeypatch: pytest.MonkeyPatch, patch_default_bleak_client
) -> None:
    """Test JBD discharge acknowledgement handling."""
    bms = DxJbdBMS(generate_ble_device(address="cc:cc:cc:cc:cc:cc"))
    sender = cast("BleakGATTCharacteristic", object())

    bms._notification_handler(sender, bytearray(DxJbdBMS._CMD_DISCHARGE_ACK))
    assert bms._msg == DxJbdBMS._CMD_DISCHARGE_ACK
    assert bms._msg_event.is_set()
    bms._msg_event.clear()

    called: dict[str, bool] = {"handler": False}

    def mock_handler(_self, _sender, _data) -> None:
        called["handler"] = True

    monkeypatch.setattr(JbdBMS, "_notification_handler", mock_handler)
    bms._notification_handler(sender, bytearray([0x00]))

    assert called["handler"] is True


async def test_jbd_discharge_commands(patch_default_bleak_client) -> None:
    """Test JBD discharge control commands."""
    bms = DxJbdBMS(generate_ble_device(address="cc:cc:cc:cc:cc:cc"))
    bms._connect = AsyncMock()
    bms._await_msg = AsyncMock()

    assert await bms.enable_discharge() is True
    bms._await_msg.assert_awaited_with(DxJbdBMS._CMD_ENABLE_DISCHARGE)

    assert await bms.disable_discharge() is True
    bms._await_msg.assert_awaited_with(DxJbdBMS._CMD_DISABLE_DISCHARGE)

    bms._connect = AsyncMock(side_effect=TimeoutError)
    assert await bms.enable_discharge() is False
    assert await bms.disable_discharge() is False
