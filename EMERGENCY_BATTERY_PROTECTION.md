# Emergency Battery Protection - Solar Inverter Override

## 🚨 **Emergency Battery Enablement Feature**

When the solar inverter is turned OFF, the system now automatically enables ALL battery discharging switches to ensure maximum power availability during critical situations.

## 🔧 **How It Works**

### **Scenario 1: Automatic Solar Shutdown (≤40% average)**
When the automation turns off the solar inverter due to low battery levels:

1. **Solar inverter is turned OFF** (≤40% average battery level)
2. **ALL protected batteries are immediately enabled** 
3. **Emergency logging** indicates which batteries were enabled
4. **Maximum power availability** for critical loads

### **Scenario 2: Manual/External Solar Shutdown**
When the solar inverter is OFF for any reason (manual, other automation, etc.):

1. **Every automation cycle** checks if solar inverter is OFF
2. **ALL disabled batteries are enabled** regardless of protection rules
3. **Emergency mode logging** shows system is in maximum power mode
4. **Overrides normal protection logic** when solar is OFF

## 📊 **Emergency Logic Priority**

### **Normal Operation (Solar ON):**
- ✅ Protect lowest batteries (up to 4 of 7 batteries)
- ✅ Maintain minimum 3 batteries discharging
- ✅ Smart protection based on battery levels

### **Emergency Mode (Solar OFF):**
- 🚨 **ALL 7 batteries enabled for discharging**
- 🚨 **Maximum power availability**
- 🚨 **Protection rules suspended**
- 🚨 **Emergency logging active**

## 🔄 **State Transitions**

### **Entering Emergency Mode:**
```
Solar Inverter ON → OFF (≤40% or manual)
├── All protected batteries → ENABLED
├── Emergency logging activated
└── Maximum power mode engaged
```

### **Exiting Emergency Mode:**
```
Solar Inverter OFF → ON (>50% average)
├── Emergency mode ends
├── Normal protection resumes
└── Smart battery management active
```

## 📝 **Log Messages**

### **Emergency Activation:**
```
🚨 SOLAR INVERTER OFF: Emergency mode - ensuring all batteries are enabled for maximum power availability
🚨 EMERGENCY ENABLE: dp04s007l4s100a_battery discharging enabled (solar inverter is OFF)
🚨 EMERGENCY ENABLE: r_12100bnn100_a00156_battery discharging enabled (solar inverter is OFF)
```

### **Emergency During Auto-Shutdown:**
```
☀️ SOLAR OFF: Disabled solar inverter (average battery: 38.2% ≤ 40%, 7 batteries)
🚨 EMERGENCY: Enabled dp04s007l4s100a_battery_2 discharging due to solar inverter shutdown
🚨 EMERGENCY: Enabled r_12100bnn100_a00156_battery discharging due to solar inverter shutdown
```

## ⚡ **Benefits**

### **🛡️ Protection During Crisis:**
- **Prevents load shedding** when batteries are critically low
- **Maximizes available power** during emergencies
- **Overrides conservative protection** when needed most

### **🤖 Intelligent Response:**
- **Automatic detection** of solar inverter state
- **Immediate response** to emergency conditions
- **Seamless integration** with existing protection logic

### **📊 Clear Monitoring:**
- **Emergency state logging** for troubleshooting
- **Battery enablement tracking** for each battery
- **Clear distinction** between normal and emergency modes

## 🎯 **Use Cases**

1. **Critical Load Support**: When solar is off, all batteries provide maximum power
2. **Emergency Backup**: Manual solar shutdown enables all batteries immediately  
3. **System Recovery**: Low battery conditions get full battery bank support
4. **Maintenance Mode**: Solar inverter maintenance doesn't limit battery availability

## 🔧 **Configuration Notes**

- **Runs every minute**: Checks solar inverter state continuously
- **Immediate response**: No delay when emergency mode is detected
- **All batteries**: Every available battery is enabled when solar is OFF
- **Automatic recovery**: Returns to normal protection when solar comes back ON

The system now provides maximum power availability when you need it most! 🔋⚡🚨
