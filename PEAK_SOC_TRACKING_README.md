# Battery Peak SOC Tracking Feature

This enhancement adds intelligent peak SOC tracking to the battery protection system. Instead of only using the current highest SOC among all batteries, the system now remembers the highest SOC each battery has reached and uses that for turn-off decisions.

## How It Works

### Peak SOC Storage
- Each battery's highest reached SOC is stored in an `input_number` helper
- The system automatically creates and updates these values as batteries charge
- Values persist through Home Assistant restarts

### Turn-Off Logic Enhancement
For each battery, the system now:
1. **Stores Peak SOC**: When a battery's SOC increases, the new peak is stored
2. **Uses Stored Peak**: When deciding to turn off a battery, it compares:
   - Current SOC vs (Stored Peak SOC - 2%) if the stored peak exists and is higher than current SOC
   - Current SOC vs (Current Highest SOC - 2%) as fallback
3. **Turn-On Logic**: Unchanged - still uses current highest SOC

### Example Scenario
- Battery A reaches 85% SOC (stored as peak)
- Battery A's SOC drops to 75% during discharge
- Other batteries are at 80% SOC
- **Old logic**: Would compare 75% vs (80% - 2% = 78%) → keep battery ON
- **New logic**: Compares 75% vs (85% - 2% = 83%) → turn battery OFF

This prevents batteries from continuing to discharge when they've already given their fair share based on their peak charge level.

## Installation

### 1. Add Input Number Helpers
Add the contents of `battery_peak_soc_storage.yaml` to your Home Assistant configuration:

```yaml
# In configuration.yaml
input_number: !include battery_peak_soc_storage.yaml
```

Or manually create the helpers via the UI under Settings > Devices & Services > Helpers.

### 2. Update Battery Names
Edit `battery_peak_soc_storage.yaml` to match your actual battery naming pattern. The automation expects:
- Battery sensors: `sensor.dadski_battery_[name]_soc`
- Peak storage: `input_number.battery_[name]_peak_soc`

### 3. Add Reset Automation (Optional)
Include the reset script from `battery_peak_soc_reset_script.yaml` for manual peak SOC resets.

## Usage

### Automatic Operation
- The system automatically tracks and stores peak SOC values
- No manual intervention required for normal operation
- Peak values are used automatically in turn-off decisions

### Manual Reset
Reset peak SOC values when needed:
```yaml
service: script.reset_battery_peak_soc
```

Or trigger via event:
```yaml
service: automation.trigger
target:
  entity_id: automation.battery_peak_soc_reset
```

### When Reset Occurs
Peak SOC values are automatically reset when:
- Any battery reaches 98% SOC or higher (near full charge)
- Manual reset is triggered

## Monitoring

### Log Messages
The enhanced logging shows:
- Peak SOC tracking: `Peak:85%` for each battery
- Reference SOC used: `RefSOC=85%` in decision making
- Turn-off reasons: `(reference 85% - 2, peak: 85%)`

### Example Log Output
```
Battery Protection: Updated peak SOC for a1: 82.5% -> 85.2%
Peak SOC tracking: a1=Current:85.2%/Peak:85.2%, a2=Current:83.1%/Peak:83.1%
Battery a1: SOC=75.5%, Peak=85.2%, RefSOC=85.2%, PlannedAction=TURN_OFF, Reason="SOC 75.5% <= 83.2% (peak 85.2% - 2) - should be OFF"
```

## Benefits

1. **Fairer Discharge**: Batteries that have reached higher peaks are turned off sooner
2. **Reduced Oscillation**: Less switching on/off as SOC levels fluctuate
3. **Better Balance**: Encourages more even utilization across battery bank
4. **Smarter Logic**: Takes battery charge history into account, not just current state

## Configuration

### Customizing Turn-Off Threshold
The 2% threshold can be adjusted in the automation code. Look for `(reference_soc - 2)` and change the value as needed.

### Adding New Batteries
1. Add new `input_number` helper in `battery_peak_soc_storage.yaml`
2. Follow naming pattern: `battery_[name]_peak_soc`
3. The automation automatically discovers new batteries matching the sensor pattern

## Troubleshooting

### Missing Peak SOC Helpers
If you see errors about missing `input_number.battery_*_peak_soc` entities:
1. Ensure the helpers are created in Home Assistant
2. Check that naming matches your battery IDs exactly
3. Restart Home Assistant after adding new helpers

### Peak SOC Not Updating
Check that:
1. Battery SOC sensors are providing valid numeric values
2. The automation is running (check logs for "Peak SOC tracking" messages)
3. Input number helpers have write permissions

### Reset Not Working
Verify that:
1. The reset automation is enabled
2. At least one battery reaches 98% SOC for automatic reset
3. Manual reset script is properly configured
