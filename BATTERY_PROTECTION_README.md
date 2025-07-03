# Battery Protection Templates for Home Assistant

This repository contains Home Assistant templates for automatically managing battery discharge protection based on battery levels. The system monitors all BMS batteries and disables discharging for the battery with the lowest level while enabling it for others.

## Overview

The BMS BLE integration creates entities like:
- `sensor.{battery_name}_battery_level` - Battery level in percentage
- `switch.{battery_name}_battery_discharging` - Controls discharge enable/disable

These templates automatically:
1. **Monitor** all battery level sensors every minute
2. **Calculate** minimum discharging requirements based on battery count
3. **Turn OFF** discharging for batteries that become the lowest (respecting minimums)
4. **Turn ON** discharging for batteries that are no longer among the lowest
5. **Maintain** minimum discharging batteries: 3+ total→3 min discharging, 3 total→2 min, 2 total→1 min, 1 total→1 discharging
6. **Log** all protection actions for monitoring

## Available Templates

### 1. Simple Battery Protection (`simple_battery_protection.yaml`)
**Best for: Basic setups with minimal configuration**

- Single automation that runs every minute
- Automatically finds all battery sensors
- Protects the lowest battery by disabling discharge
- Minimal logging
- Easy to understand and modify

```yaml
# Add to configuration.yaml
automation: !include simple_battery_protection.yaml
```

### 2. Complete Battery Protection (`battery_protection_template.yaml`)
**Best for: Users who want detailed monitoring and status**

- Template sensors for battery status monitoring
- Binary sensor for protection status
- Detailed logging and attributes
- Optional notification framework
- Dashboard-friendly sensors

### 3. Advanced Battery Protection (`advanced_battery_protection.yaml`)
**Best for: Power users who want full control and safety features**

- Input helpers for runtime configuration
- Configurable protection threshold
- Emergency protection for critically low batteries
- Detailed status monitoring
- Daily status reports
- Multiple safety layers

## Installation

### Method 1: Direct Integration
Add the chosen template directly to your `configuration.yaml`:

```yaml
# For simple protection
automation: !include simple_battery_protection.yaml

# For complete protection (add each section)
template: !include battery_protection_template.yaml
automation: !include battery_protection_template.yaml
binary_sensor: !include battery_protection_template.yaml
```

### Method 2: Package Method (Recommended)
1. Create a `packages` folder in your Home Assistant config directory
2. Copy the chosen YAML file to `packages/battery_protection.yaml`
3. Add to `configuration.yaml`:
```yaml
homeassistant:
  packages: !include_dir_named packages
```

### Method 3: Split Configuration
If you already use split configurations:
```yaml
automation: !include automations.yaml
template: !include templates.yaml
# etc.
```
Then add the relevant sections to each file.

## Configuration

### Simple Version
No configuration needed - works automatically.

### Advanced Version
After installation, configure via Home Assistant UI:

1. **Enable Protection**: Toggle `input_boolean.battery_protection_enabled`
2. **Set Threshold**: Adjust `input_number.battery_protection_threshold` (default: 15%)
3. **Monitor Status**: Check `sensor.battery_manager_status` for detailed info

## Entity Naming Requirements

The templates automatically detect battery entities with these patterns:
- Battery sensors: `sensor.*_battery_level`
- Discharge switches: `switch.*_battery_discharging`

The switch entity name is derived from the sensor name:
```
sensor.redodo_battery_1_battery_level
→ switch.redodo_battery_1_battery_discharging
```

## How It Works

### Protection Logic
1. **Every minute**, scan for all `*_battery_level` sensors
2. **Calculate minimum discharging requirement** based on total battery count:
   - **4+ batteries**: At least 3 must keep discharging (max 1-3 can be protected)
   - **3 batteries**: At least 2 must keep discharging (max 1 can be protected)
   - **2 batteries**: At least 1 must keep discharging (max 1 can be protected)
   - **1 battery**: Must keep discharging (0 can be protected)
3. **Turn OFF discharging** for batteries that:
   - Are currently ON and become the lowest level (if protection limit allows)
   - Are currently ON and fall below the critical threshold (advanced version)
   - Are among the lowest and need protection to meet minimum requirements
4. **Turn ON discharging** for batteries that:
   - Are currently OFF and are no longer among the lowest needing protection
   - Are currently OFF and we have too many protected (exceeding minimum requirements)
5. **Smart balancing**: Only makes changes when necessary to maintain optimal protection

### Safety Features (Advanced Version)
- **Emergency Protection**: Immediately protects batteries below 5%
- **Configurable Threshold**: Protect batteries below custom percentage
- **Switch Availability Check**: Only acts on available switches
- **Multiple Protection Layers**: Lowest battery + threshold protection
- **Daily Reports**: Status summary every morning

## Monitoring and Logs

### Log Messages
Protection actions are logged with these prefixes:
- `🛡️ PROTECTED:` - Battery discharge disabled
- `✅ ENABLED:` - Battery discharge enabled
- `🚨 EMERGENCY:` - Emergency protection triggered
- `📊 Daily Battery Report:` - Status summary

### Home Assistant Logs
View logs in **Settings → System → Logs** or filter by:
```
Logger: battery_protection
```

### Dashboard Integration
Add these entities to your dashboard:
- `sensor.battery_manager_status` - Overall status
- `binary_sensor.battery_protection_active` - Protection indicator
- `input_boolean.battery_protection_enabled` - Enable/disable toggle
- `input_number.battery_protection_threshold` - Threshold setting

## Customization

### Changing Check Interval
Modify the time_pattern trigger:
```yaml
trigger:
  - platform: time_pattern
    minutes: "/5"  # Every 5 minutes instead of every minute
```

### Adding Notifications
Uncomment and configure the notification sections in the templates:
```yaml
# Add your notification service
notify:
  - name: battery_alerts
    platform: telegram  # or pushbullet, email, etc.
    # ... your configuration
```

### Custom Thresholds
For the simple version, add a condition:
```yaml
condition:
  - condition: template
    value_template: "{{ battery_level < 20 }}"  # Custom 20% threshold
```

## Troubleshooting

### No Batteries Detected
- Check that your BMS integration is working
- Verify sensor names match pattern `*_battery_level`
- Check Home Assistant logs for template errors

### Switches Not Found
- Ensure discharge switches exist: `switch.*_battery_discharging`
- Check that switches are not disabled
- Verify switch entity IDs in Developer Tools

### Protection Not Working
- Check that `input_boolean.battery_protection_enabled` is ON (advanced version)
- Verify automation is enabled in Settings → Automations
- Check logs for error messages
- Ensure batteries have different levels (system only acts when levels differ)

### False Triggers
- Increase the time interval between checks
- Add minimum difference conditions
- Check for sensor availability before acting

## Example Dashboard Card

```yaml
type: entities
title: Battery Protection System
entities:
  - entity: sensor.battery_manager_status
    name: Status
  - entity: binary_sensor.battery_protection_active
    name: Protection Active
  - entity: input_boolean.battery_protection_enabled
    name: Enable Protection
  - entity: input_number.battery_protection_threshold
    name: Protection Threshold
  - type: attribute
    entity: sensor.battery_manager_status
    attribute: lowest_battery
    name: Lowest Battery
  - type: attribute
    entity: sensor.battery_manager_status
    attribute: lowest_level
    name: Lowest Level
    suffix: "%"
```

## Safety Notes

- **Test thoroughly** before relying on automated protection
- **Monitor logs** initially to ensure correct operation
- **Keep manual override** capability for emergency situations
- **Regular maintenance** of battery sensors and switches
- **Backup power protection** - ensure Home Assistant remains powered during battery protection scenarios

## Support

This template is designed for the BMS BLE Home Assistant integration. For issues:

1. Check Home Assistant logs for specific error messages
2. Verify all entity names match the expected patterns
3. Test with Developer Tools → Templates
4. Check that your BMS integration supports discharge control

## License

This template is provided as-is for educational and practical use. Test thoroughly before production use.
