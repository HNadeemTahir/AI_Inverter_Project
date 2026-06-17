# 4kW MPPT Booster — Bill of Materials (BOM) & Purchasing List

**Project:** 4kW MPPT DC-DC Boost Converter (dsPIC30F2010 + UC3843)
**Date:** April 2026
**Target Market:** Hall Road, Lahore / AliExpress

---

## 1. The "Hard to Find" Components (Check Hall Road First, then AliExpress)
*These parts are critical for the Micro-Shunt sensing method. Hall Road usually does not stock these. If unavailable, order online.*

| Item | Part Number / Specs | Qty per Board | AliExpress / Online Notes | Hall Road Backup Option |
| :--- | :--- | :--- | :--- | :--- |
| **Current Sense Amp** | **TI INA181A2IDBVR** (SOT-23-6) | 1 | Search: "INA181A2IDBVR". Make sure top mark is `1AED` (Gain = 50). | **None.** Must build Current Transformer (CT) instead. |
| **Micro-Shunt Resistors** | **2mΩ (R002)**, 2512 SMD, 1% Alloy, 2W | 5 | Search: "2512 alloy resistor R002". Solder all 5 in parallel. | Buy generic Manganin wire from multimeter repair shops. |

---

## 2. Core Control ICs & Gate Drivers
*These are generally available at major IC shops on Hall Road (e.g., EVE-II, Ahtesham Electronics).*

| Item | Part Number / Specs | Qty | Notes |
| :--- | :--- | :--- | :--- |
| **Analog PWM Controller** | **UC3843** | 1 | Standard DIP-8 or SOIC-8. Ask for original ST or TI if possible. |
| **Microcontroller** | **dsPIC30F2010** | 1 | Existing brain for your inverter / MPPT algorithm. |
| **Isolated Gate Driver** | **FOD3150** or **TLP250H** | 1 | Must be isolated. TLP250H is very common on Hall Road. |
| **Fast Switching Diodes** | **1N4148** | 3 | Used for asymmetric gate turn-off path. Buy a strip of 50. |

---

## 3. Power Stage (High Voltage / High Current)
*Available at heavy electronics/inverter repair shops in the market.*

| Item | Part Number / Specs | Qty | Notes |
| :--- | :--- | :--- | :--- |
| **Main Switching IGBTs** | **STGW60H65DFB** (650V, 60A) | 2 | Parallel configuration. Or equivalent TO-247 Field Stop Trench IGBTs. |
| **Boost Fast Diode** | **STTH3006D** (600V, 30A) | 1 | Ultra-fast recovery is MANDATORY. Do not use standard rectifiers. |
| **Input Capacitors** | **470µF / 450V** Electrolytic | 2 | High ripple current rating if possible. |
| **Output Capacitors** | **470µF / 450V** Electrolytic | 2 | (Two in parallel = 940µF). Must handle 380V DC safely. |
| **Pre-Charge Resistor** | **50Ω, 10W or 20W** | 1 | Standard white rectangular cement resistor. |
| **Pre-Charge Relay** | **30A, 12V Coil Relay** | 1 | SLA-12VDC-SL-A or similar heavy-duty PCB relay. |

---

## 4. Passive Components (Gate Drive & Filtering)
*Easily available everywhere.*

| Item | Value / Specs | Qty | Purpose |
| :--- | :--- | :--- | :--- |
| **Turn-ON Resistor** | **15Ω** (1/4W or 1/2W) | 2 | Limits di/dt turn-on spike. |
| **Turn-OFF Resistor** | **5.6Ω** (1/4W or 1/2W) | 2 | Fast Miller-discharge path. |
| **Gate Pull-Down** | **10kΩ** (1/4W) | 2 | Solder directly across Gate-Emitter to prevent ghost turn-on. |
| **RC Filter Resistor** | **150kΩ** (1/2W) | 1 | UC3843 Voltage Feedback divider (High side). |
| **RC Filter Resistor** | **1kΩ** (1/4W) | 1 | UC3843 Voltage Feedback divider (Low side). |

---

## 5. The "Plan B" Current Transformer (CT) Parts
*If you cannot find the INA181 on Hall Road and do not want to pay AliExpress delivery taxes, buy these parts to wind a CT instead.*

| Item | Specs | Qty | Notes |
| :--- | :--- | :--- | :--- |
| **Ferrite Toroidal Core** | Medium size (approx 1-inch diameter) | 1 | From transformer winding shops. Must be ferrite, not iron powder. |
| **Enamelled Copper Wire** | Thin gauge (e.g., 28 SWG) | 1 roll | For winding 100 turns around the core. |
| **CT Burden Resistor** | **2Ω** (1 Watt) | 1 | Converts the 0.5A CT secondary current into 1.0V for the UC3843. |
| **CT Reset Diode** | **1N4148** | 1 | Placed across the burden resistor. |

---
*Created for Hall Road Purchasing Run - April 2026*
