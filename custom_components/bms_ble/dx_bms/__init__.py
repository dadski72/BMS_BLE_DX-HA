"""DX-specific BMS wrappers."""

from typing import Final

CUSTOM_BMS_MODULES: Final[dict[str, str]] = {
    "aiobmsble.bms.jbd_bms": "custom_components.bms_ble.dx_bms.jbd_bms",
    "aiobmsble.bms.redodo_bms": "custom_components.bms_ble.dx_bms.redodo_bms",
    "custom_components.bms_ble.plugins.jbd_bms": "custom_components.bms_ble.dx_bms.jbd_bms",
    "custom_components.bms_ble.plugins.redodo_bms": "custom_components.bms_ble.dx_bms.redodo_bms",
}


def custom_bms_module(module: str) -> str:
    """Return a local wrapper module when this fork extends the BMS class."""
    return CUSTOM_BMS_MODULES.get(module, module)
