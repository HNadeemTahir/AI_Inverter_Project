# MPPT Boost Converter: Inductor Design Calculations

This document details the mathematical calculations used to determine the exact requirements for the main power inductor (L2) in the 4kW MPPT DC-DC Boost Converter.

## 1. Fixed System Parameters
* **Target Output Voltage (V_out):** 380V DC
* **Switching Frequency (f_sw):** 20,000 Hz (20 kHz)
* **Estimated Efficiency (n):** 0.95 (95%)

---

## 2. Dynamic Input Scenarios (Firmware Controlled)
The MCU dynamically limits power based on the available input voltage from the solar panels. We evaluate the two extreme scenarios:

* **Scenario A (2 Panels):** V_in = 100V, Maximum Power (P_out) = 1000W
* **Scenario B (4 Panels):** V_in = 200V, Maximum Power (P_out) = 3000W

---

## 3. Maximum Input Current (I_in) Calculation
**Formula:** `I_in = P_out / (V_in * n)`

* **Scenario A (100V, 1000W):**
  I_in = 1000 / (100 * 0.95)
  I_in = 10.52 Amps

* **Scenario B (200V, 3000W):**
  I_in = 3000 / (200 * 0.95)
  I_in = 15.78 Amps

*Conclusion:* The maximum continuous DC current the inductor will see is safely limited by the firmware to **~16 to 18 Amps**.

---

## 4. Duty Cycle (D) Calculation
**Formula:** `D = 1 - (V_in / V_out)`

* **Scenario A (100V):**
  D = 1 - (100 / 380)
  D = 0.736  (73.6% Duty Cycle)

* **Scenario B (200V):**
  D = 1 - (200 / 380)
  D = 0.473  (47.3% Duty Cycle)

---

## 5. Required Inductance (L) Calculation
**Formula:** `L = (V_in * D) / (f_sw * Delta_IL)`
*(Where Delta_IL is the allowed peak-to-peak current ripple. We design for a maximum ripple of 8 Amps).*

* **Worst-Case Ripple Calculation (Scenario B):**
  L = (200 * 0.473) / (20000 * 8)
  L = 94.6 / 160000
  L = 0.000591 Henries
  **L = 591 µH**

* **Low Power/Tighter Ripple Calculation (Scenario A, assuming 4A ripple):**
  L = (100 * 0.736) / (20000 * 4)
  L = 73.6 / 80000
  L = 0.00092 Henries
  **L = 920 µH**

*Conclusion:* The target inductor value for stable operation across all dynamic conditions is **600 µH to 1000 µH (1 mH)**.

---

## 6. Peak Saturation Current (I_peak)
To prevent the magnetic core from saturating (which would destroy the IGBTs), the inductor must handle the absolute peak of the current ripple.

**Formula:** `I_peak = I_in_max + (Delta_IL / 2)`

I_peak = 18A + (8A / 2)
I_peak = 18A + 4A
**I_peak = 22 Amps**

---

## 7. Physical Layout Requirements
Based strictly on the mathematics above, the physical hardware assigned to `L2` in the PCB layout must meet the following criteria:

1. **Wire Gauge:** Must be at least 12 AWG (or dual 14 AWG strands) to safely carry 18A RMS without overheating.
2. **Core Saturation:** Must be rated for > 25A peak saturation current.
3. **Physical Footprint Size:** Winding 1 mH of 12 AWG wire requires a massive core volume. The outer diameter of the toroid will be approximately **45mm to 60mm**. The PCB footprint MUST accommodate a minimum of 40mm pin-pitch to prevent mechanical stress on the board.
