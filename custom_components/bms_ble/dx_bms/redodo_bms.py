"""Redodo BMS wrapper with discharge control support."""

from typing import Any, Final

from aiobmsble import BMSSample
from aiobmsble.bms.redodo_bms import BMS as RedodoBMS
from bleak.exc import BleakError


class BMS(RedodoBMS):  # type: ignore[misc]
    """Redodo BMS implementation extended with discharge control."""

    _CMD_ENABLE_DISCHARGE: Final[bytes] = bytes(
        [0x00, 0x00, 0x04, 0x01, 0x0C, 0x55, 0xAA, 0x10]
    )
    _CMD_DISABLE_DISCHARGE: Final[bytes] = bytes(
        [0x00, 0x00, 0x04, 0x01, 0x0D, 0x55, 0xAA, 0x11]
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the wrapper."""
        super().__init__(*args, **kwargs)
        self._last_discharge_state: bool = False

    def _battery_discharging_state(self) -> bool:
        """Return interpreted battery discharging state for Redodo BMS."""
        if len(self._msg) <= 68:
            return self._last_discharge_state

        current_state = self._msg[68] not in (0x80, 0xC8)
        self._last_discharge_state = current_state
        return current_state

    async def _async_update(self) -> BMSSample:
        """Update battery status information."""
        result = await super()._async_update()
        result["dischrg_mosfet"] = self._battery_discharging_state()
        return result

    async def enable_discharge(self) -> bool:
        """Enable battery discharge."""
        try:
            await self._connect()
            await self._await_msg(self._CMD_ENABLE_DISCHARGE, wait_for_notify=False)
        except (BleakError, EOFError, TimeoutError) as err:
            self._log.error("Failed to enable discharge: %s", err)
            return False

        self._last_discharge_state = True
        return True

    async def disable_discharge(self) -> bool:
        """Disable battery discharge."""
        try:
            await self._connect()
            await self._await_msg(self._CMD_DISABLE_DISCHARGE, wait_for_notify=False)
        except (BleakError, EOFError, TimeoutError) as err:
            self._log.error("Failed to disable discharge: %s", err)
            return False

        self._last_discharge_state = False
        return True
