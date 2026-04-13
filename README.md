# Inverter Digital Twin (dsPIC30F2010 + FGY75T120SWD)

Closed-loop SPICE simulation of a 220V/50Hz off-grid pure sine wave inverter with ATS grid sharing capability. Models the complete signal chain from dsPIC30F2010 firmware logic through isolated gate drivers to physical IGBT switching, including electro-thermal junction monitoring and hardware fault protection.

---

## Version 6.3 — Dead-Time Compensation + Python Automation

This version extends the simulation with **current-direction dependent dead-time compensation**, **8 automated `.meas` measurements** for data extraction, and a **Python batch automation script** (`run_simulation.py`) for headless NgSpice execution. Built on top of V6.1's closed-loop PI regulation, electro-thermal modeling, and hardware fault protection.

### Key Technical Achievements
*   **220V RMS Output**: Verified stable 50Hz AC power with 311V Peak magnitude.
*   **True Unipolar SPWM**: 16kHz switching logic mirroring `dsPIC30F2010` firmware (`Spwm.c`).
*   **Closed-Loop PI Control**: Proportional + Integral regulation with continuous-time equivalent gains.
*   **ZMPT101B Sensor Delay**: 200μs RC lag model matching real transformer + filter response.
*   **Inductive Motor Load**: R-L series model (20Ω / 100mH) with verified current phase lag.
*   **Gate Safety Network**: 10kΩ pull-downs, 15V Zener clamps, HF bootstrap bypass on all 4 IGBTs.
*   **High-Fidelity LC Filter**: 3mH dual-coil + 10μF CBB film capacitor (market-standard values).
*   **Dead-Time Protection**: ~2μs shoot-through prevention gap (mirrors dsPIC `DTCON1` register).
*   **DT Compensation**: Current-direction dependent compensation using `tanh()` smooth switching.
*   **Electro-Thermal Model**: Foster RC thermal network with datasheet-verified Rth(j-c) = 0.21 °C/W.
*   **Short Circuit Protection**: CT + Rectifier + Comparator + INT0 latch (trips at 50A, ~1μs response).
*   **Automated .meas Metrics**: 8 measurements (V_rms, V_peak, I_rms, I_peak, P_out, P_in, Tj_max, Tj_avg).
*   **Python Batch Automation**: `run_simulation.py` — headless NgSpice execution via `subprocess`.

---

## Project Structure

```
AI_Inverter_Project/
├── models/                     # Device subcircuits
│   ├── FGY75T120SWD.lib       # onsemi 1200V/75A IGBT model
│   └── tlp250h.sub            # TLP250H isolated gate driver
├── src/                        # SPICE netlists
│   ├── H_Bridge_Full.cir      # Master simulation (V6.3)
│   └── H_Bridge_THI_Experimental.cir  # Third Harmonic Injection test
├── results/                    # Waveform screenshots
│   ├── 01_output_voltage_motor_load.png
│   ├── 02_voltage_current_phase_lag.png
│   ├── 03_reference_vs_feedback.png
│   ├── 04_pi_controller_signals.png
│   ├── 05_zmpt101b_delay_effect.png
│   ├── 06_dead_time_pwm_zoomed.png
│   ├── 07_dc_bus_current_analysis.png
│   ├── 08_output_voltage_v61.png
│   ├── 09_spwm_logic.png
│   ├── 10_thermal_transient_ripple.png
│   ├── 11_dc_bus_freewheeling.png
│   ├── 12_short_circuit_protection.png
│   └── 13_dead_time_zoom.png
├── docs/                       # Technical design notes
│   └── thermal_equivalent_circuit.png  # Electro-thermal schematic
├── run_simulation.py           # Python batch automation script
├── Run_Inverter.bat            # Quick-launch script (GUI mode)
└── README.md
```

---

## Simulation Results (V6.3)

### 1. Output Voltage — Inductive Motor Load
![Output Voltage](results/01_output_voltage_motor_load.png)
*50Hz output driving a 20Ω/100mH R-L load. Peak voltage ±311V. Ripple visible at voltage peaks is due to inductive load back-EMF interaction.*

### 2. Voltage-Current Phase Lag
![Phase Lag](results/02_voltage_current_phase_lag.png)
*Load current (red) lags output voltage (green) by approximately 57°, consistent with arctan(ωL/R) for a 20Ω/100mH load at 50Hz.*

### 3. PI Controller: Reference vs Feedback
![Reference vs Feedback](results/03_reference_vs_feedback.png)
*Reference sine (green) vs ZMPT101B feedback (red). PI controller maintains close tracking despite 200µs sensor transport delay.*

### 4. PI Controller Internal Signals
![PI Internals](results/04_pi_controller_signals.png)
*PI controller error signal and correction output. Integral term accumulates during startup transient and stabilizes within 2 cycles.*

### 5. ZMPT101B Sensor Delay Effect
![ZMPT Delay](results/05_zmpt101b_delay_effect.png)
*Instantaneous voltage feedback (green) vs filtered feedback through 2kΩ/100nF RC network (red). The 200µs group delay models the physical ZMPT101B transformer response.*

### 6. Dead-Time Protection — PWM Gate Signals (V6.1)
![Dead-Time PWM](results/06_dead_time_pwm_zoomed.png)
*Leg A gate signals showing ~2µs dead-time gap between HS and LS transitions. Both signals held at 0V during the gap to prevent shoot-through, matching dsPIC DTCON1 register configuration.*

### 7. DC Bus Current Analysis — Energy Flow Verification (V6.1)
![DC Bus Current](results/07_dc_bus_current_analysis.png)
*DC bus current i(V_DC_Link). Negative excursions represent power delivery to the load; positive spikes at zero-crossings indicate inductive energy returning through body diodes. Net average power ≈ 560W.*

### 8. Output Voltage + Current with Dead-Time (V6.1)
![Output V6.1](results/08_output_voltage_v61.png)
*Output voltage (green) with scaled load current ×20 (red). Phase lag of ~57° confirms correct R-L load behavior. Peak voltage reduced to ~280V due to expected dead-time voltage distortion.*

### 9. Unipolar SPWM Logic (Zero-Crossing Crossover)
![Unipolar SPWM](results/09_spwm_logic.png)
*Full 20ms cycle showing Unipolar SPWM operation. Leg A switches at 16kHz during the positive half-cycle while Leg B remains clamped, with roles exchanged at the zero-crossing. This halves the total switching events compared to Bipolar modulation.*

### 10. Sub-Microsecond Dead-Time Validation
![Dead-Time Validation](results/13_dead_time_zoom.png)
*Single switching event captured over ~20µs. The 2µs interval where both gate signals are at 0V corresponds to the DTCON1 dead-band register setting.*

### 11. DC Bus Energy Flow (Four-Quadrant Freewheeling)
![Freewheeling](results/11_dc_bus_freewheeling.png)
*DC bus current showing four-quadrant energy flow. Negative excursions represent load power delivery; positive excursions indicate inductive energy recirculating to the DC bus through body diodes.*

### 12. Electro-Thermal Junction Ripple (Micro-Thermal)
![Thermal Ripple](results/10_thermal_transient_ripple.png)
*Foster RC thermal network output over 60ms. Junction node exhibits 50Hz thermal ripple corresponding to the AC power cycle. Heatsink node remains stable at 45°C due to its large thermal mass (C_Heatsink = 10F).*

### 13. Hardware Short-Circuit Latch (50A Trip-Point)
![Short Circuit](results/12_short_circuit_protection.png)
*Short circuit test: 0.1Ω fault applied at t=25ms. Inductor current ramps at di/dt = V_bus / L_total through the 6mH output filter. CT comparator triggers the INT0 fault latch at 50A, disabling PWM drive. Current decays through freewheeling diodes.*

---

## Electro-Thermal IGBT Model

![Thermal Equivalent Circuit](docs/thermal_equivalent_circuit.png)

The simulation includes a **Foster RC thermal network** that maps IGBT power dissipation to junction temperature using the standard SPICE electrical-thermal analogy:

| Thermal Domain | Electrical Equivalent | Unit |
|---|---|---|
| Power (Heat Source) | Current Source | W → A |
| Temperature | Voltage | °C → V |
| Thermal Mass | Capacitance | J/°C → F |
| Thermal Resistance | Resistance | °C/W → Ω |

**All thermal parameters sourced from the onsemi FGY75T120SWD datasheet:**

| Thermal Stage | Parameter | Value | Source |
|---|---|---|---|
| Junction → Case | R_Junction | 0.21 °C/W | Datasheet Rth(j-c) max |
| Junction Thermal Mass | C_Junction | 0.05 F | Silicon die |
| Case → Heatsink | R_Paste | 0.24 °C/W | TO-247 + thermal grease |
| Heatsink → Ambient | R_Heatsink | 1.0 °C/W | Aluminum, natural convection |
| Heatsink Thermal Mass | C_Heatsink | 10 F | Aluminum heatsink block |
| Ambient Temperature | V_Ambient | 45V (= 45°C) | Worst-case summer ambient |

### 1. Transient Junction Ripple (Micro-Thermal Analysis)
*To view: Run `plot v(Thermal_Power_In) v(Case_Temp) v(Heatsink_Temp)` after 60ms simulate.*

Because the inverter drives a 50Hz AC load, power dissipation is periodic rather than constant. The IGBT conducts during its assigned half-cycle and is off during the complement. This produces a **50Hz thermal ripple** (20ms periodicity) at the silicon junction.

The coupled SPICE simulation captures this `Z_th(j-c)` transient impedance directly. The 10F heatsink capacitance remains flat at 45°C over the 60ms window, while the 0.05F junction node ripples at 50Hz in phase with the AC load current.

### 2. Steady-State Heatsink Sizing (Macro-Thermal Analysis)
It is computationally prohibitive to run a 1us-timestep SPICE simulation for 10 real minutes to watch the macroscopic heatsink warm up. Instead, industry-standard methodology relies on decoupled average-power extraction.

Assuming an extracted average power loss of `P_avg ≈ 40W` per IGBT during high-load condition:

> **T_steady_state = P_avg × (R_th_jc + R_th_cs + R_th_sa) + T_ambient**
> **T_steady_state = 40W × (0.21 + 0.24 + 1.0) + 45°C = 103°C**

For a `1.0 °C/W` aluminum heatsink, the calculated steady-state junction temperature remains below the FGY75T120SWD absolute maximum rating of `175°C` at 45°C continuous ambient.

---

## Component Level Modeling

### TLP250H Isolated Gate Driver
- **Custom 8-Pin Subcircuit**: Behavioral LED sensing, 150ns propagation delay, totem-pole output.
- **Protection**: 15V Zener (BZT52C15), 10kΩ pull-down, asymmetric turn-on/off resistors (15Ω/5.6Ω).

### FGY75T120SWD IGBT (onsemi)
- **1200V/75A Field Stop VII**: Models Miller Plateau and switching transitions.
- **Thermal**: Rth(j-c) = 0.21 °C/W, Tj_max = 175°C, PD_max = 714W @ Tc=25°C.

### ZMPT101B Voltage Sensor
- **200μs RC Delay**: Models transformer coupling + PCB filter (R=2kΩ, C=100nF).
- **Scaling**: 311V peak → 0.389V peak (0.00125 V/V gain + 0.5V bias).

### Short Circuit Protection (CT + INT0 Latch)
- **Current Transformer**: 1A:1V ratio, full-wave rectified.
- **Hardware Comparator**: Trips at 50A primary (50V across burden resistor).
- **INT0 MCU Latch**: G-source + capacitor latch mimics `SPWM_Stop()` on dsPIC INT0 interrupt.
- **Fault Test**: 0.1Ω short applied at t=25ms to validate protection response.

---

## How to Run

1. Clone this repository.
2. Install [NgSpice](https://ngspice.sourceforge.io/) (v46 or later).
3. Install [Python](https://www.python.org/) (v3.10 or later).

### Option A: Interactive Mode (GUI)
```spice
ngspice src/H_Bridge_Full.cir
run
plot v(OUT_A, OUT_B)                      * Output voltage
plot v(OUT_A, OUT_B) i(V_Meter)*20        * Voltage + current
plot v(Sine_V) v(SNS_V_DELAYED)           * Reference vs feedback
plot v(SIG_ERR) v(SIG_PI_CORR)            * PI controller signals
plot v(SNS_V_FB) v(SNS_V_DELAYED)         * ZMPT101B delay
plot v(PWM_HS_A) v(PWM_LS_A) xlimit 0.009 0.00920   * Dead-time gap
plot i(V_DC_Link)                         * DC bus current (energy flow)
plot v(Thermal_Power_In) v(Case_Temp) v(Heatsink_Temp)  * Thermal monitoring
plot v(SIG_Fault)                         * Short circuit fault flag
```

### Option B: Python Batch Mode (Headless)
```bash
python run_simulation.py
```
Runs NgSpice silently via `ngspice_con.exe` and prints all `.meas` results:
```
v_out_rms    = 1.921e+02   (192V RMS)
v_out_peak   = 2.855e+02   (286V peak)
i_load_rms   = 5.037e+00   (5.04A RMS)
p_load_avg   = 5.084e+02   (508W output)
p_dc_input   = -5.217e+02  (522W input → η = 97.4%)
tj_max       = 4.598e+01   (46.0°C junction peak)
```

---

## NgSpice Compatibility Notes
- `limit()` function is **not supported** in NgSpice 46 B-source expressions (silently returns 0V).
- `sdt()` integrator function is **not available**; replaced with G-source + Capacitor model.
- `.PARAM` variables **cannot be used** inside B-source expressions; values must be hardcoded directly.
- Tested on: NgSpice 46 (Windows 64-bit).

---

## Roadmap
- [x] TLP250H 8-Pin Behavioral Subcircuit
- [x] FGY75T120SWD IGBT Modeling
- [x] 400V Full H-Bridge Pure Sine (Open-Loop)
- [x] **Closed-Loop PI Voltage Regulation**
- [x] **Inductive Motor Load with Phase Lag Analysis**
- [x] **ZMPT101B Sensor Delay Modeling (200μs)**
- [x] **Dead-Time Implementation (2μs safety gap)**
- [x] **Dead-Time Compensation (Current-Direction Dependent)**
- [x] **Short Circuit Protection (CT + Comparator + INT0 Latch)**
- [x] **Electro-Thermal IGBT Model (Foster RC Network, Datasheet-Verified)**
- [x] **Automated .meas Metrics (8 Engineering Measurements)**
- [x] **Python Batch Automation (run_simulation.py)**
- [ ] THI (Third Harmonic Injection) Matching Firmware
- [ ] Parametric Sweep & CSV Data Export
- [ ] MPPT Solar Charging Integration
- [ ] AI Surrogate Model Training (Scikit-Learn)

---

## Author
**Nadeem Tahir** — Embedded Systems & Power Electronics Engineer

Designs and builds production-grade inverters and motor drives from schematic to firmware across multiple MCU platforms (dsPIC, PIC, STM32, ESP32).

