"""Module to support Redodo BMS."""

from collections.abc import Callable
from typing import Any, Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from .basebms import AdvertisementPattern, BaseBMS, BMSsample, BMSvalue, crc_sum


class BMS(BaseBMS):
    """Redodo BMS implementation."""

    CRC_POS: Final[int] = -1  # last byte
    HEAD_LEN: Final[int] = 3
    MAX_CELLS: Final[int] = 16
    MAX_TEMP: Final[int] = 5
    _FIELDS: Final[list[tuple[BMSvalue, int, int, bool, Callable[[int], Any]]]] = [
        ("voltage", 12, 2, False, lambda x: float(x / 1000)),
        ("current", 48, 4, True, lambda x: float(x / 1000)),
        ("battery_level", 90, 2, False, lambda x: x),
        ("cycle_charge", 62, 2, False, lambda x: float(x / 100)),
        ("cycles", 96, 4, False, lambda x: x),
        ("problem_code", 76, 4, False, lambda x: x),
    ]

    # Add discharge control commands
    _CMD_ENABLE_DISCHARGE: Final[bytes] = bytes(
        [0x00, 0x00, 0x04, 0x01, 0x0C, 0x55, 0xAA, 0x10]
    )
    _CMD_DISABLE_DISCHARGE: Final[bytes] = bytes(
        [0x00, 0x00, 0x04, 0x01, 0x0D, 0x55, 0xAA, 0x11]
    )

    def __init__(self, ble_device: BLEDevice, reconnect: bool = False) -> None:
        """Initialize BMS."""
        super().__init__(__name__, ble_device, reconnect)
        self._last_discharge_state: bool = False

    @staticmethod
    def matcher_dict_list() -> list[AdvertisementPattern]:
        """Provide BluetoothMatcher definition."""
        return [
            {  # patterns required to exclude "BT-ROCC2440"
                "local_name": pattern,
                "service_uuid": BMS.uuid_services()[0],
                "manufacturer_id": 0x585A,
                "connectable": True,
            }
            for pattern in (
                "R-12*",
                "R-24*",
                "RO-12*",
                "RO-24*",
                "P-12*",
                "P-24*",
                "PQ-12*",
                "PQ-24*",
                "L-12*",  # LiTime
                "L-24*",  # LiTime
            )
        ]

    @staticmethod
    def device_info() -> dict[str, str]:
        """Return device information for the battery management system."""
        return {"manufacturer": "Redodo", "model": "Bluetooth battery"}

    @staticmethod
    def uuid_services() -> list[str]:
        """Return list of 128-bit UUIDs of services required by BMS."""
        return [normalize_uuid_str("ffe0")]

    @staticmethod
    def uuid_rx() -> str:
        """Return 16-bit UUID of characteristic that provides notification/read property."""
        return "ffe1"

    @staticmethod
    def uuid_tx() -> str:
        """Return 16-bit UUID of characteristic that provides write property."""
        return "ffe2"

    @staticmethod
    def _calc_values() -> frozenset[BMSvalue]:
        return frozenset(
            {
                "battery_charging",
                "battery_discharging_state",
                "delta_voltage",
                "cycle_capacity",
                "power",
                "runtime",
                "temperature",
            }
        )  # calculate further values from BMS provided set ones

    def _notification_handler(
        self, _sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Handle the RX characteristics notify event (new data arrives)."""
        self._log.debug("RX BLE data: %s", data)

        if len(data) < 3 or not data.startswith(b"\x00\x00"):
            self._log.debug("incorrect SOF.")
            return

        if len(data) != data[2] + BMS.HEAD_LEN + 1:  # add header length and CRC
            self._log.debug("incorrect frame length (%i)", len(data))
            return

        if (crc := crc_sum(data[: BMS.CRC_POS])) != data[BMS.CRC_POS]:
            self._log.debug(
                "invalid checksum 0x%X != 0x%X", data[len(data) + BMS.CRC_POS], crc
            )
            return

        self._data = data
        self._data_event.set()

    @staticmethod
    def _decode_data(data: bytearray) -> BMSsample:
        result: BMSsample = {}
        for key, idx, size, sign, func in BMS._FIELDS:
            value = int.from_bytes(
                data[idx : idx + size], byteorder="little", signed=sign
            )
            result[key] = func(value)
        return result

    @staticmethod
    def _cell_voltages(data: bytearray, cells: int) -> list[float]:
        """Return cell voltages from status message."""
        return [
            (value / 1000)
            for idx in range(cells)
            if (
                value := int.from_bytes(
                    data[16 + 2 * idx : 16 + 2 * idx + 2], byteorder="little"
                )
            )
        ]

    @staticmethod
    def _temp_sensors(data: bytearray, sensors: int) -> list[int | float]:
        return [
            value
            for idx in range(sensors)
            if (
                value := int.from_bytes(
                    data[52 + idx * 2 : 54 + idx * 2], byteorder="little", signed=True
                )
            )
        ]

    def _battery_discharging_state(self) -> bool:
        """Return interpreted battery discharging state for Redodo BMS."""
        if len(self._data) <= 68:
            return self._last_discharge_state  # Return last known state

        # Log raw data for debugging discharge state
        discharge_byte = self._data[68]
        self._log.warning(
            "Raw byte at offset 68 (discharge state): (%d)", discharge_byte
        )

        # Redodo-specific logic: if raw value is 8 or 12, discharge is OFF
        current_state = discharge_byte not in (0x80, 12)
        self._last_discharge_state = current_state  # Store current state
        self._log.warning(f"discharge state:{current_state}  discharge_byte:{discharge_byte}")
        return current_state

    async def _async_update(self) -> BMSsample:
        """Update battery status information."""
        await self._await_reply(b"\x00\x00\x04\x01\x13\x55\xaa\x17")

        decoded_data = BMS._decode_data(self._data)

        return decoded_data | BMSsample(
            {
                "cell_voltages": BMS._cell_voltages(self._data, BMS.MAX_CELLS),
                "temp_values": BMS._temp_sensors(self._data, BMS.MAX_TEMP),
                "battery_discharging_state": self._battery_discharging_state(),
            }
        )

    async def enable_discharge(self) -> bool:
        """Enable battery discharge."""
        try:
            self._log.warning("=== ENABLE DISCHARGE COMMAND START ===")
            self._log.warning("Command bytes: %s", self._CMD_ENABLE_DISCHARGE.hex())
            await self._connect()
            self._last_discharge_state = True
            await self._await_reply(self._CMD_ENABLE_DISCHARGE, wait_for_notify=False)
            self._log.warning("Discharge enabled successfully")
            self._log.warning("=== ENABLE DISCHARGE COMMAND END ===")
            return True
        except Exception as err:
            self._log.error("Failed to enable discharge: %s", err)
            return False

    async def disable_discharge(self) -> bool:
        """Disable battery discharge."""
        try:
            self._log.warning("=== DISABLE DISCHARGE COMMAND START ===")
            self._log.warning("Command bytes: %s", self._CMD_DISABLE_DISCHARGE.hex())
            await self._connect()
            self._last_discharge_state = False
            await self._await_reply(self._CMD_DISABLE_DISCHARGE, wait_for_notify=False)
            self._log.warning("Discharge disabled successfully")
            self._log.warning("=== DISABLE DISCHARGE COMMAND END ===")
            return True
        except Exception as err:
            self._log.error("Failed to disable discharge: %s", err)
            return False
