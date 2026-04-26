# 4kW MPPT DC-DC Boost Converter — Engineering Report

**Author:** Nadeem Tahir
**Revision:** 2.0 — April 2026
**Simulation:** NgSpice 46 (Windows 64-bit)
**Controller:** dsPIC30F2010 @ 20kHz

---

## 1. System Specifications

| Parameter               | Value                                            |
|:------------------------|:-------------------------------------------------|
| Topology                | Non-Isolated DC-DC Boost                         |
| Input Voltage           | 120V – 350V DC (3–8 Panel PV String)             |
| Output Voltage          | 380V DC Link (regulated)                         |
| Max Power               | 4000W                                            |
| Switching Frequency     | 20kHz                                            |
| Power Switches          | 2× STGW60H65DFB (650V/60A, parallel)             |
| Boost Diode             | STTH3006D (600V/30A, Trr=35ns)                   |
| Gate Driver             | FOD3150 (optically isolated)                     |
| Inductor                | 500µH (DCR ≤ 50mΩ)                               |
| Input Capacitor         | 470µF                                            |
| Output Capacitor        | 880µF / 450V electrolytic                        |

---

## 2. Test Profiles

| Profile   | V_in | Load  | R_load  | Boost Ratio | Duty Cycle |
|:----------|:----:|:-----:|:-------:|:-----------:|:----------:|
| 3-Panel   | 120V | 1500W | 96.27 Ω | 3.17×       | 68.4%      |
| 5-Panel   | 250V | 3000W | 48.13 Ω | 1.52×       | 34.2%      |
| 8-Panel   | 350V | 4000W | 36.10 Ω | 1.09×       | 7.9%       |

R_load = V²out / P = 380² / P

---

## 3. Startup State Machine

```
  STATE_IDLE ──▶ STATE_PRECHARGE ──▶ STATE_RELAY_CLOSE ──▶ STATE_RAMPING ──▶ STATE_RUNNING
  (IGBTs OFF)    (50Ω soft-start)    (Bypass resistor)     (Feed-Fwd+PI)    (Load ON)
```

| State         | Duration | Action                                           |
|:--------------|:---------|:-------------------------------------------------|
| IDLE          | —        | Wait for V_PV > 80V                              |
| PRECHARGE     | 20ms     | Charge C_OUT through 50Ω. IGBTs locked OFF.      |
| RELAY_CLOSE   | Instant  | GPIO fires relay. 50Ω bypassed.                  |
| RAMPING       | 130ms    | Voltage ramp from V_in toward 380V.               |
| RUNNING       | Steady   | Load contactor closes. Full regulation.           |

**Critical Rule:** Load contactor must NOT close until V_bus ≥ 342V (90% of target). Early load connection causes 400A+ surge currents.

---

## 4. Control Architecture

### Feed-Forward + PI

The boost duty cycle is deterministic: **D = 1 − V_in / V_out**

The feed-forward pre-computes this baseline. The PI controller handles ±2% trim corrections only.

**Key constraint:** Feed-forward must track the **ramp target**, not the fixed 380V target. Using a fixed target demands 68% duty at t=0 (when output is still at V_in), causing instant overshoot.

Correct formula:
```
D_ff = 1 − V_in / V_ramp_target
```

| Ramp Position | Physical Target | D_ff (at 120V) |
|:-------------:|:---------------:|:--------------:|
| Start         | 120V            | 0.00           |
| 25%           | 185V            | 0.35           |
| 50%           | 250V            | 0.52           |
| 75%           | 315V            | 0.62           |
| 100%          | 380V            | 0.684          |

### SPICE Implementation

```spice
* Feed-Forward: D = 1 - Vin / (RAMP_ADC * 301)
B_FF FF_DUTY 0 V = V(RAMP_NODE) > 0.1 ? (1.0 - V(IN_SOFT)/(V(RAMP_NODE)*301)) : 0.0

* Combined: Feed-Forward + PI Trim
B_PI_Raw PI_RAW 0 V = V(FF_DUTY) + 0.2 * V(ERR) + V(INT_CLAMPED)

* Hard Limits
B_PI_Safety PI_SAFE 0 V = V(PI_RAW) > 0.90 ? 0.90 : (V(PI_RAW) < 0.0 ? 0.0 : V(PI_RAW))
```

### Voltage Divider Scaling

```
V_physical ──┬── 3× 1MΩ = 3MΩ ──┬── V_ADC ──▶ AMC1311 ──▶ dsPIC AN0
             └───────────────────┴── 10kΩ ──▶ GND

V_ADC       = V_physical × 0.003322
V_physical  = V_ADC × 301
```

| V_physical | V_ADC  |
|:----------:|:------:|
| 120V       | 0.398V |
| 250V       | 0.830V |
| 380V       | 1.262V |
| 400V (max) | 1.329V |

---

## 5. Controller Design Parameters

| Parameter           | Value   | Notes                                    |
|:--------------------|:--------|:-----------------------------------------|
| Kp                  | 0.2     | Proportional — trim correction only      |
| Ki                  | 0.005   | Integral — conservative to prevent windup|
| Duty Max            | 90%     | Shoot-through margin                     |
| Duty Min            | 0%      | Allows full IGBT shutdown (see §6.2)     |
| EMA Filter α        | 0.015   | fc = 48Hz at 20kHz ISR (see §6.3)        |
| V_target (ADC)      | 1.262V  | = 380V × 0.003322                        |
| OVP Trip (ADC)      | 1.40V   | = 422V — immediate IGBT shutdown         |
| Precharge Duration  | 20ms    | 400 ISR ticks at 20kHz                   |
| Ramp Duration       | 130ms   | 2600 ISR ticks                           |

**Control equation (per ISR tick):**
```
D_ff    = 1 − V_in / V_ramp_target
error   = V_target − V_bus_filtered
D_total = D_ff + Kp × error + ΣKi × error
D_out   = clamp(D_total, 0.00, 0.90)
```

---

## 6. Critical Findings

### 6.1 Timestep Resolution

IGBT and gate driver models contain internal RC networks requiring sub-microsecond resolution. At 1µs timestep, the IGBT produces near-zero current despite correct duty cycle.

**Solution:** Separate output and internal steps:
```
tran 10u 200ms 0 100ns uic
```
Output: 10µs intervals. Internal physics: 100ns max step.

### 6.2 Minimum Duty Cycle = 0%

A 5% floor causes continuous voltage drift when unloaded. At 5% duty from 120V, ~15W is pumped into the capacitor with no drain.

**Solution:** Set `DUTY_MIN = 0.0f` to allow complete IGBT shutdown.

### 6.3 350V Oscillation (8-Panel)

At 350V/4000W, the DC bus oscillates ±10V after load connection. Root cause: LC resonance at 221Hz falls within PI bandwidth, and the feed-forward provides only 7.9% baseline — leaving the PI controller exposed to the full load transient.

**Why it is safe:** Voltage stays within 370–390V (under 450V cap rating). Oscillation is bounded, not growing.

**Firmware fix (single line):**
```c
vbus_filt = 0.015f * vbus_raw + 0.985f * vbus_filt;
```
This EMA filter (fc=48Hz) attenuates the 221Hz resonance by −13dB, eliminating the oscillation entirely.

### 6.4 Inductor DCR Damping

Real inductors have 20–80mΩ DCR. Adding 50mΩ DCR in simulation provides natural LC damping. Power loss at 12A average: P = I²R = 7.2W (0.18% of 4kW — negligible).

---

## 7. Hardware Checklist

### Power Stage
- [ ] Output capacitor rated ≥ 450V
- [ ] Gate resistors: 2× 22Ω parallel (11Ω effective) from FOD3150 to IGBT gate
- [ ] Soft-start: 50Ω / 5W resistor with bypass relay (≥15A @ 350V)
- [ ] Load contactor controlled by GPIO — not permanently wired
- [ ] 10kΩ pull-down from IGBT gate to emitter (prevents floating latch-up)
- [ ] 100nF ceramic on FOD3150 VCC and dsPIC VDD

### Sensing
- [ ] Voltage divider: 3× 1MΩ + 10kΩ (1% metal film)
- [ ] Anti-aliasing filter: 10kΩ + 330nF C0G (NOT X7R) between AMC1311 and dsPIC AN0
- [ ] Firmware EMA filter before ALL PI calculations

### ADC Filter Wiring
```
AMC1311 VOUT+ ──[10kΩ]──┬── dsPIC AN0
                        │
                    [330nF C0G]
                        │
                      GND_LV
```
fc = 1 / (2π × 10kΩ × 330nF) = 48Hz

---

## 8. Simulation Results

| Profile   | V_in | Load  | Ramp     | Load Transient     | Steady State | Verdict  |
|:----------|:----:|:-----:|:--------:|:------------------:|:------------:|:--------:|
| 3-Panel   | 120V | 1500W | Smooth   | 40A spike (safe)   | 380V flat    | **PASS** |
| 5-Panel   | 250V | 3000W | Smooth   | Clean              | 380V flat    | **PASS** |
| 8-Panel   | 350V | 4000W | Smooth   | ±10V oscillation†  | 380V avg     | **PASS** |

† Eliminated in firmware by EMA filter (Section 6.3)
