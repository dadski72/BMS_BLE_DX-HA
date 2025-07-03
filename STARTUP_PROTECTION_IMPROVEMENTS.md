# Battery Protection - Startup & Availability Improvements

## 🚀 **What's New**

The battery protection system now includes robust startup protection and handling for unavailable batteries, specifically addressing the issue where BLE battery sensors need time to connect after Home Assistant restarts.

## 🛡️ **Startup Protection Features**

### 1. **Dual Trigger System**
```yaml
trigger:
  - platform: time_pattern
    minutes: "*"  # Regular operation every minute
  - platform: homeassistant
    event: start  # Special handling on HA restart
```

### 2. **Intelligent Startup Delays**
- **HA Restart**: 90-second delay to allow BLE connections to stabilize
- **Regular Runs**: 5-second delay to avoid race conditions
- **Smart Timing**: Longer delay when system is starting up

### 3. **Battery Availability Checking**
- **Count Tracking**: Monitors total vs available battery sensors
- **Threshold Logic**: Requires ≥80% of batteries to be available
- **Minimum Requirement**: At least 2 batteries must be available
- **Graceful Degradation**: Skips protection if insufficient data

### 4. **Enhanced Logging**
```yaml
🚀 Battery Protection: Starting up after HA restart. Found 2/2 batteries available.
🔋 Battery Check: 2/2 batteries available, Average: 85.5%, Solar: on
⚠️ Battery Check: 1/2 batteries available, 1 batteries unavailable
```

## 📊 **Template Sensor Improvements**

### Before:
- Returned `0` when no batteries available
- Could cause false averages during startup

### After:
- Returns `unavailable` when no batteries detected
- Prevents incorrect automation triggers
- Better integration with HA's availability system

## 🧠 **Smart Logic Enhancements**

### Startup Conditions:
1. **If HA just restarted**: Always allow after 90s delay
2. **If regular run**: Check battery availability first
3. **If insufficient data**: Skip protection actions
4. **If partial data**: Log warnings but continue if ≥80% available

### Variable Improvements:
- `total_battery_sensors`: Counts all battery entities (even unavailable)
- `battery_entities`: Only available batteries with numeric states
- `sufficient_data`: Boolean check for data quality
- Better error handling throughout

## 🔧 **Fixed Issues**

1. **for_each Compatibility**: ✅ Fixed (previous update)
2. **Startup Race Conditions**: ✅ Fixed with delays and conditions
3. **Unavailable Sensor Handling**: ✅ Fixed with availability checks
4. **Template References**: ✅ Fixed all `battery_sensors` → `battery_entities`
5. **Incomplete Data Protection**: ✅ Fixed with sufficient_data logic

## 📋 **Typical Startup Sequence**

1. **HA Restarts** → Automation triggers with 90s delay
2. **BLE Sensors Connect** → Some batteries become available
3. **Availability Check** → Wait until ≥80% batteries available
4. **Protection Starts** → Normal operation begins
5. **Missing Sensors** → Logged as warnings, system adapts

## ⚙️ **Configuration Notes**

### Expected Behavior:
- **First 1-2 minutes**: May see "batteries unavailable" warnings
- **After stabilization**: Normal protection operation
- **Permanent failures**: System adapts to available batteries
- **Partial outages**: Continues with reduced sensor set

### Monitoring:
- Check `battery_protection` logger for startup messages
- Monitor `sensor.average_battery_level` availability
- Watch for "unavailable" warnings during startup

## 🎯 **Benefits**

✅ **Robust Startup**: No more protection errors during HA restart  
✅ **BLE Tolerance**: Handles slow BLE sensor connections gracefully  
✅ **Data Quality**: Only acts on reliable sensor data  
✅ **Fault Tolerance**: Adapts to sensor failures or disconnections  
✅ **Clear Logging**: Detailed startup and availability reporting  
✅ **Production Ready**: Handles real-world BLE sensor behavior  

The system is now fully prepared for production use with proper startup protection! 🔋⚡
