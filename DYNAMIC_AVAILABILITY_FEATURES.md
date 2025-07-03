# Battery Protection - Dynamic Availability Enhancements

## 🔄 **Dynamic Battery Availability Features**

The battery protection system now handles batteries that become unavailable during operation due to Bluetooth disconnections, BMS shutdowns, or other issues.

## 📊 **Enhanced Template Sensor Monitoring**

### New Attributes in `sensor.average_battery_level`:

1. **`battery_count`**: Shows "X of Y batteries" format
   - Example: "2 of 3 batteries" (2 available, 3 total detected)

2. **`available_batteries`**: Lists currently available batteries with levels
   - Example: "RIVER 2 MAX-0574 Main (96%), RIVER 2 MAX-0574 (85%)"

3. **`unavailable_batteries`**: Lists currently unavailable batteries with status
   - Example: "Battery 3 (unavailable), Battery 4 (unknown)"
   - Shows "None" when all batteries are available

4. **`individual_levels`**: Enhanced with availability status
   - Now includes `'status': 'available'` for each battery

### Averaging Logic:
- ✅ **Only available batteries** with numeric states are included in average
- ✅ **Returns "unavailable"** when no batteries are available (instead of "0")
- ✅ **Dynamically adjusts** as batteries come online/offline

## 🤖 **Enhanced Automation Logic**

### Improved Data Quality Checks:
```yaml
sufficient_data: >
  {% if total_battery_sensors == 0 %}
    false
  {% elif total_battery_sensors == 1 %}
    {{ battery_entities | length >= 1 }}
  {% else %}
    {{ battery_entities | length >= 1 and (battery_entities | length / total_battery_sensors) >= 0.6 }}
  {% endif %}
```

### Operating Modes:

1. **🚫 No Batteries Available**:
   - Skips all protection logic
   - Disables solar inverter control
   - Logs warning messages

2. **🔋 Single Battery Mode**:
   - Ensures the single battery discharging switch stays ON
   - Enables solar control based on that battery
   - Special logging for single battery operation

3. **🔋🔋 Multiple Battery Mode**:
   - Normal protection logic applies
   - Protection calculations based only on available batteries
   - Adapts limits when battery count changes

### Dynamic Protection Limits:
- **2+ available**: Normal protection rules apply
- **Calculations updated**: Based on currently available batteries only
- **Real-time adaptation**: Changes as batteries go online/offline

## 📈 **Enhanced Logging & Monitoring**

### Detailed Status Logging:
```
🔋 Battery Status: 2/3 available, Average: 85.5%, Solar: on. ⚠️ Unavailable: Battery 3 (unknown)
🔋 Single Battery Mode: Only 1 battery available, ensuring it stays enabled for critical functions
☀️ SOLAR CONTROL DISABLED: No battery data available for solar inverter control
```

### Availability Tracking:
- **Real-time monitoring** of battery connections
- **Warnings** when batteries become unavailable
- **Info messages** when batteries come back online
- **Protection decisions** logged with battery count context

## 🛡️ **Fault Tolerance Features**

### Battery Connection Issues:
- ✅ **Bluetooth drops**: Excluded from averaging until reconnected
- ✅ **BMS shutdowns**: System adapts to remaining batteries
- ✅ **Partial availability**: Continues operating with ≥60% of batteries
- ✅ **Graceful degradation**: Smooth transition between operating modes

### Solar Inverter Protection:
- **No battery data**: Solar control disabled entirely
- **Partial data**: Solar control based on available batteries only
- **Enhanced context**: Logs show how many batteries informed the decision

## 📋 **Real-World Scenarios**

### Scenario 1: Bluetooth Connection Drop
```
🔋 Battery Status: 2/3 available, Average: 85.0%, Solar: on. ⚠️ Unavailable: Battery 3 (unavailable)
🔋 PROTECTED: Disabled discharging for Battery 1 (82% - lowest)
☀️ SOLAR ON: Enabled solar inverter (average battery: 85.0% > 50%, 2 batteries)
```

### Scenario 2: Single Battery Remaining
```
🔋 Battery Status: 1/3 available, Average: 78.0%, Solar: on. ⚠️ Unavailable: Battery 2 (unknown), Battery 3 (unavailable)
🔋 Single Battery Mode: Only 1 battery available, ensuring it stays enabled for critical functions
```

### Scenario 3: All Batteries Offline
```
🔋 Battery Status: 0/3 available, Average: unavailable, Solar: on. ⚠️ Unavailable: Battery 1 (unknown), Battery 2 (unknown), Battery 3 (unavailable)
☀️ SOLAR CONTROL DISABLED: No battery data available for solar inverter control
```

## ⚙️ **Configuration Benefits**

### Startup Resilience:
- ✅ **Startup delays** for BLE connection establishment
- ✅ **Availability thresholds** prevent premature operation
- ✅ **Progressive activation** as batteries come online

### Runtime Resilience:
- ✅ **Dynamic adaptation** to changing battery availability
- ✅ **Fault tolerance** for temporary disconnections
- ✅ **Intelligent averaging** excludes offline batteries
- ✅ **Protection continuity** maintains safety with available batteries

### Monitoring & Debugging:
- ✅ **Comprehensive logging** of availability changes
- ✅ **Dashboard visibility** through template sensor attributes
- ✅ **Real-time status** updates in Home Assistant
- ✅ **Clear error messages** for troubleshooting

## 🎯 **Production Ready Features**

The system now handles all real-world battery availability scenarios:

✅ **BLE Connection Management**: Graceful handling of Bluetooth issues  
✅ **BMS State Changes**: Adapts to battery shutdowns and startups  
✅ **Partial System Operation**: Continues with available batteries  
✅ **Data Quality Assurance**: Only uses reliable battery data  
✅ **Dynamic Averaging**: Real-time calculation updates  
✅ **Comprehensive Monitoring**: Full visibility into system state  

Perfect for production deployment with variable battery connectivity! 🔋⚡🛡️
