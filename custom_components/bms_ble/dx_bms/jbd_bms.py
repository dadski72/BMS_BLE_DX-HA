"""JBD BMS wrapper with discharge control support."""

from typing import Final

from aiobmsble.bms.jbd_bms import BMS as JbdBMS
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError


class BMS(JbdBMS):  # type: ignore[misc]
    """JBD smart BMS implementation extended with discharge control."""

    _CMD_ENABLE_DISCHARGE: Final[bytes] = bytes(
        [0xDD, 0x5A, 0xE1, 0x02, 0x00, 0x00, 0xFF, 0x1D, 0x77]
    )
    _CMD_DISABLE_DISCHARGE: Final[bytes] = bytes(
        [0xDD, 0x5A, 0xE1, 0x02, 0x00, 0x02, 0xFF, 0x1B, 0x77]
    )
    _CMD_DISCHARGE_ACK: Final[bytes] = bytes(
        [0xDD, 0xE1, 0x00, 0x00, 0x00, 0x00, 0x77]
    )

    def _notification_handler(
        self, sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Handle discharge command acknowledgements and normal JBD data."""
        if bytes(data) == self._CMD_DISCHARGE_ACK:
            self._msg = bytes(data)
            self._msg_event.set()
            return

        super()._notification_handler(sender, data)

    async def enable_discharge(self) -> bool:
        """Enable battery discharge."""
        try:
            await self._connect()
            await self._await_msg(self._CMD_ENABLE_DISCHARGE)
        except (BleakError, EOFError, TimeoutError) as err:
            self._log.error("Failed to enable discharge: %s", err)
            return False

        return True

    async def disable_discharge(self) -> bool:
        """Disable battery discharge."""
        try:
            await self._connect()
            await self._await_msg(self._CMD_DISABLE_DISCHARGE)
        except (BleakError, EOFError, TimeoutError) as err:
            self._log.error("Failed to disable discharge: %s", err)
            return False

        return True
