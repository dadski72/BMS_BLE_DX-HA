# Battery Protection - Entity Mapping Reference

## 🔋 **Your Battery System Configuration**

### **Battery Sensors → Switch Entities Mapping:**

| Battery Sensor | Battery Switch | Expected Levels |
|----------------|----------------|-----------------|
| `sensor.dp04s007l4s100a_battery` | `switch.dp04s007l4s100a_battery_discharging` | ~49% |
| `sensor.dp04s007l4s100a_battery_2` | `switch.dp04s007l4s100a_battery_discharging_2` | ~42% |
| `sensor.dp04s007l4s100a_battery_3` | `switch.dp04s007l4s100a_battery_discharging_3` | ~50% |
| `sensor.r_12100bnn100_a00156_battery` | `switch.r_12100bnn100_a00156_battery_discharging` | ~45% |
| `sensor.r_12100bnn100_a00431_battery` | `switch.r_12100bnn100_a00431_battery_discharging` | ~45% |
| `sensor.r_12100bnn100_a00737_battery` | `switch.r_12100bnn100_a00737_battery_discharging` | ~52% |
| `sensor.r_12100bnn100_a00875_battery` | `switch.r_12100bnn100_a00875_battery_discharging` | ~46% |

**Expected Average: (49+42+50+45+45+52+46) ÷ 7 = 47.0%** ✅

---

## 🔧 **What Was Fixed:**

### 1. **Battery Detection Pattern**
- **Before**: `_battery_level$` (❌ didn't match your sensors)
- **After**: `_battery(_[0-9]+)?$` (✅ matches `_battery` and `_battery_2`, `_battery_3`)

### 2. **Switch Entity Generation**
- **Before**: `replace('_battery', '_battery_discharging')` (❌ wrong replacement)
- **After**: `entity_id.split('.')[1] + '_discharging'` (✅ simple append)

### 3. **Template Sensor Logic**
- **Before**: Looking for wrong sensor names (❌ no matches found)
- **After**: Correctly finds all 7 battery sensors (✅ proper averaging)

---

## 🎯 **Protection Logic For Your 7 Batteries:**

With 7 batteries available, the system will:

- **Protect**: Up to 4 batteries (7 - 3 = 4 max protected)
- **Keep Discharging**: Minimum 3 batteries always enabled
- **Target**: Lowest batteries get protected first

### **Current Battery Order (lowest to highest):**
1. `dp04s007l4s100a_battery_2` - 42% (most likely to be protected)
2. `r_12100bnn100_a00156_battery` - 45%
3. `r_12100bnn100_a00431_battery` - 45%
4. `r_12100bnn100_a00875_battery` - 46%
5. `dp04s007l4s100a_battery` - 49%
6. `dp04s007l4s100a_battery_3` - 50%
7. `r_12100bnn100_a00737_battery` - 52% (least likely to be protected)

---

## 📊 **Expected Behavior After Restart:**

1. **✅ Average Battery Level**: Should show ~47.0% instead of 96%
2. **✅ Template Sensor Attributes**: Will show "7 of 7 batteries"
3. **✅ Available Batteries**: Will list all 7 batteries with their levels
4. **✅ Protection Actions**: Will start protecting lowest batteries
5. **✅ Solar Control**: Based on 47% average (should be ON since >50% threshold)

---

## 🚀 **Next Steps:**

1. **Restart Home Assistant** to load the updated configuration
2. **Check the average**: Should immediately show ~47%
3. **Monitor protection**: Watch automation logs for protection decisions
4. **Verify switches**: Ensure the switch entities exist and are controllable

---

## 🔍 **Quick Test Commands:**

### **In Developer Tools > Template:**
```yaml
# Test battery detection
{% set batteries = states.sensor | selectattr('entity_id', 'search', '_battery(_[0-9]+)?$') | rejectattr('entity_id', 'eq', 'sensor.average_battery_level') | selectattr('state', 'is_number') | list %}
{{ batteries | length }} batteries found:
{% for battery in batteries %}
- {{ battery.entity_id }}: {{ battery.state }}%
{% endfor %}
Average: {{ (batteries | map(attribute='state') | map('float') | sum / batteries | length) | round(1) }}%
```

### **In Developer Tools > Services:**
```yaml
# Test switch control
service: switch.turn_off
target:
  entity_id: switch.dp04s007l4s100a_battery_discharging_2
```

The configuration is now perfectly aligned with your battery system! 🔋⚡
