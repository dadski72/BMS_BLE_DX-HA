# Battery Protection System - Fixed Version

## Overview
The battery protection automation has been fixed to resolve the Home Assistant `for_each` compatibility issue. The system now uses simple entity ID lists instead of complex state objects.

## What Was Fixed
1. **for_each Loop Compatibility**: Changed from complex state objects to simple entity ID strings
2. **Template Simplification**: Simplified battery sensor collection to use entity IDs directly
3. **Variable References**: Updated all references to use the new simplified structure

## Key Features
✅ **Smart Battery Protection**: Protects lowest batteries while maintaining minimum discharging count  
✅ **Solar Inverter Control**: Automatically manages solar inverter based on average battery level  
✅ **Template Sensor**: Provides average battery level with detailed attributes  
✅ **Error-Free Templates**: All Jinja2 templates are now compatible with Home Assistant  
✅ **Comprehensive Logging**: Clear logging for all actions and decisions  

## Protection Logic
- **2 batteries**: Protect 1 (keep 1 discharging)
- **3 batteries**: Protect 1 (keep 2 discharging) 
- **4+ batteries**: Protect up to `total - 3` batteries (keep minimum 3 discharging)

## Solar Inverter Logic
- **≤40% average**: Turn OFF solar inverter
- **>50% average**: Turn ON solar inverter
- **40-50% range**: Hysteresis zone (no change)

## Installation

### Method 1: Package (Recommended)
1. Create folder: `config/packages/`
2. Copy `simple_battery_protection.yaml` to `config/packages/battery_protection.yaml`
3. Add to `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

### Method 2: Direct Integration
1. Copy template section to `configuration.yaml`
2. Copy automation section to `automations.yaml`

## Required Entities
Your battery sensors must follow this naming pattern:
- `sensor.battery1_battery_level`
- `sensor.battery2_battery_level`
- `sensor.battery3_battery_level`
- etc.

Your battery discharging switches must follow this pattern:
- `switch.battery1_battery_discharging`
- `switch.battery2_battery_discharging`
- `switch.battery3_battery_discharging`
- etc.

## Template Sensor Attributes
The `sensor.average_battery_level` provides:
- **State**: Average battery level percentage
- **battery_count**: Number of detected batteries
- **individual_levels**: List of all battery levels
- **solar_inverter_status**: Current solar inverter state
- **protection_status**: Current protection status message

## Monitoring
Check Home Assistant logs for:
- `battery_protection` logger entries
- Debug messages every minute
- Warning messages for protection actions
- Info messages for solar inverter control

## Testing
1. Restart Home Assistant after installation
2. Check that `sensor.average_battery_level` appears
3. Monitor automation in Developer Tools > Events
4. Check logs for battery_protection entries

## Troubleshooting
1. **Sensor not appearing**: Check entity naming pattern
2. **Automation not running**: Verify trigger and conditions
3. **No protection actions**: Check switch entity IDs match pattern
4. **Template errors**: Check Home Assistant logs for template issues

## Files
- `simple_battery_protection.yaml`: Complete working system
- `BATTERY_PROTECTION_FIXED.md`: This documentation
- `BATTERY_PROTECTION_README.md`: Original detailed documentation

The system is now ready for production use! 🔋⚡
