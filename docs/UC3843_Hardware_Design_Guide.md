# Hardware Design Guide: UC3843 Analog Controller

This document provides the exact pinout, electrical requirements, and external supporting component list for integrating the **UC3843** into the 4kW MPPT Booster. 

This circuit configures the UC3843 as a "Hardware Slave" to the dsPIC30F2010. The dsPIC commands the target voltage, but the UC3843 handles all the nanosecond-level switching, dead-time, and peak current protection.

## 1. Pin Diagram (DIP-8 / SOIC-8)

```text
            +---+--+---+
       COMP | 1      8 | VREF (5.0V)
            |          |
 VFB (from) | 2      7 | VCC (15V)
   (dsPIC)  |          |
     ISENSE | 3      6 | OUT (to Gate Driver)
            |          |
      RT/CT | 4      5 | GND
            +----------+
```

## 2. Pin-by-Pin Wiring & External Components

| Pin | Name | External Components Required | Purpose & Connection |
| :--- | :--- | :--- | :--- |
| **1** | **COMP** | `100kΩ` Resistor + `10nF` Capacitor in series to Pin 2 | **Error Amplifier Compensation.** Stabilizes the internal op-amp so it doesn't oscillate when the dsPIC changes the voltage. |
| **2** | **VFB** | RC Filter from dsPIC `OC1` pin + `10kΩ` Pull-Up to VREF | **Voltage Feedback.** The dsPIC feeds a filtered DC voltage here. **CRITICAL:** You must add a 10kΩ pull-up to Pin 8 (VREF) for boot safety. |
| **3** | **ISENSE** | `1kΩ` + `470pF` (LEB Filter) + Slope Comp Resistor | **Current Protection.** Receives the 0-1V signal from the INA181. Shuts off the IGBT instantly if it hits 1.0V (50A). |
| **4** | **RT/CT** | `Rt = 8.6kΩ` to Pin 8.<br>`Ct = 10nF` to GND. | **Oscillator (20 kHz).** These two components set the main switching frequency. |
| **5** | **GND** | None | **Ground.** Tie to the main clean analog ground. |
| **6** | **OUT** | `1.3kΩ` Resistor to FOD3150 Pin 2 | **PWM Output.** Drives the LED inside the isolated FOD3150. (15V output - 1.5V LED = 13.5V. 13.5V / 1.3kΩ = ~10mA). |
| **7** | **VCC** | `10µF` Electrolytic + `0.1µF` Ceramic to GND | **Power Supply (15V).** Must be stable. The UC3843 turns on at 8.4V and turns off at 7.6V (UVLO). |
| **8** | **VREF** | `0.1µF` Ceramic to GND | **5.0V Reference.** Internal highly accurate 5V supply used to power the `Rt` resistor. |

---

## 3. The Complete Hardware Schematic (Modular View)

To make the layout perfectly clear for PCB design, the schematic is broken down into three functional modules.

```text
                 +-----------------------+
                 |                       |
      (COMP) 1 --|      UC3843           |-- 8 (VREF)
                 |                       |
       (VFB) 2 --|  PWM CONTROLLER       |-- 7 (VCC)
                 |                       |
    (ISENSE) 3 --|                       |-- 6 (OUT)
                 |                       |
     (RT/CT) 4 --|                       |-- 5 (GND)
                 +-----------------------+
```

### Module A: The MPPT Summing Node (Pin 1 & 2)
This module handles the 380V hardware regulation and the dsPIC MPPT injection logic.
```text
                            +---> To Pin 1 (COMP)
                            |
                     [10nF + 100kΩ]
                            |
[ 380V DC Bus ]---[ 1.5MΩ ]-+---> To Pin 2 (VFB)
                            |
    [ Ground ]----[ 10kΩ ]--+
                            |
                     [47kΩ Injection]
                            |
                         (Node A) --- [ 1µF Cap ] --- GND
                            |
                     [10kΩ Filter]
                            |
   [ dsPIC OC1 ]------------+-------- [ 10kΩ Pull-Up ] --- +5V
```

### Module B: Current Sense & Slope Compensation (Pin 3 & 4)
This module handles the nanosecond current protection and cures sub-harmonic oscillation.
```text
[ INA181 OUT ]---[ 1kΩ ]----+-------> To Pin 3 (ISENSE)
                            |
    [ Ground ]---[ 470pF ]--+
                            |
                     [10kΩ Slope Res]
                            |
                         [Emitter]
                           2N3904 NPN
                         [Base]   [Collector] ------> To Pin 8 (VREF)
                            |
                            +-----------------------> To Pin 4 (RT/CT)
                            |
                         [Rt 8.6kΩ] ----------------> To Pin 8 (VREF)
                            |
                         [Ct 10nF ] ----------------> Ground
```

### Module C: Power & Output (Pins 5, 6, 7, 8)
This module provides power and drives the isolated gate driver.
```text
        [ Ground ] <------------------------- Pin 5 (GND)

[ FOD3150 Pin 2 ] <-------[ 1.3kΩ ]---------- Pin 6 (OUT)

  [ +15V Power ] ---+------------------------ Pin 7 (VCC)
                    |
      [ Ground ] ---+---[ 10µF + 0.1µF ]

      [ Ground ] ---+---[ 0.1µF ]------------ Pin 8 (VREF)
```

### **Schematic Breakdown & Final Physics:**
*   **Pin 1 & 2 Loop:** The `10nF` capacitor and `100kΩ` resistor connect Pin 1 and Pin 2 together to stabilize the internal amplifier.
*   **Pin 2 (The Summing Node):** This relies on Kirchhoff's Current Law (KCL).
    1.  **380V Hardware Regulation:** A `1.5MΩ` resistor connects to the 380V DC Bus, and a `10kΩ` resistor connects to Ground. If the dsPIC is at 50% PWM, it becomes invisible, and this divider clamps the hardware at exactly 377V.
    2.  **dsPIC RC Filter:** The OC1 PWM signal first passes through a **`10kΩ` Filter Resistor** and a **`1µF` Filter Capacitor** to Ground. This flattens the 20kHz PWM into a perfectly smooth DC voltage.
    3.  **dsPIC Injection:** This smooth DC voltage connects to Pin 2 via a **`47kΩ` injection resistor**. By changing PWM from 0% to 100%, the dsPIC slides the hardware target voltage anywhere between 443V and 311V.
    4.  **Boot-Up Safety:** A **`10kΩ` Pull-Up resistor** is attached directly to the dsPIC OC1 pin to the +5V MCU power. If the dsPIC is booting (floating), this forces 5V through the filter, regulating the bus safely to 321V and keeping the system shut down.
*   **Pin 3 Input:** The INA181 current signal passes through a `1kΩ` resistor and `470pF` capacitor to ground to filter out 100ns Leading Edge Noise.
*   **Pin 3 & 4 (Slope Comp):** The `2N3904 NPN` transistor's Base connects to Pin 4 to read the 20kHz sawtooth wave without stealing current. Its Collector connects to Pin 8 (VREF) for muscle. Its Emitter connects through a `10kΩ` slope resistor to Pin 3 to cure sub-harmonic oscillation at >50% duty cycles.
*   **Pin 4 Timing:** An `8.6kΩ` resistor connects to Pin 8. A `10nF` capacitor connects to Ground. This guarantees exactly 20kHz switching.
*   **Pin 6 Output:** A `1.3kΩ` resistor connects directly to the LED input of the FOD3150. Since the UC3843 outputs 15V, this resistor safely limits the LED current to ~10mA.

## 4. The Slope Compensation Circuit (Deep Dive)
As discussed in Section 14.8, because you are boosting 150V to 380V (a duty cycle greater than 50%), you must add slope compensation to Pin 3 to prevent sub-harmonic oscillation.

**How to wire it:**
1.  **NPN Transistor:** Use a standard cheap NPN like a `2N3904`.
2.  **Base:** Connect to **Pin 4 (RT/CT)**. This picks up the 20kHz sawtooth wave.
3.  **Collector:** Connect to **Pin 8 (VREF)** or **Pin 7 (VCC)** for power.
4.  **Emitter:** Connect a `10kΩ` resistor from the Emitter to **Pin 3 (ISENSE)**.

*How it works:* It takes the oscillator's rising ramp and mixes a tiny bit of it into the current sensor's signal. This mathematically tricks the UC3843's internal comparators into remaining perfectly stable, even when the duty cycle climbs up to 90% during a cold start!

## 5. The "Dead-Boot" Explosion Risk (CRITICAL PCB FIX)
When reviewing Advanced Chinese inverter architectures (like Voltronic Axpert), they all implement a safety mechanism to prevent a "Dead-Boot Explosion."

**The Flaw:** When you turn the inverter on, the 15V supply wakes up the UC3843 instantly. However, the dsPIC30F2010 takes several milliseconds to boot up its software and output a signal on the OC1 pin. During these milliseconds, the `VFB` (Pin 2) is floating at `0V`. 
If `VFB` is `0V`, the UC3843 thinks the solar voltage has crashed, and it instantly goes to **100% MAXIMUM Duty Cycle**. Turning on a boost converter at 100% duty cycle is a dead short circuit across the solar panels. The IGBTs will explode before the dsPIC even finishes booting.

**The Tier-1 Solution:**
You **MUST** place a `10kΩ` Pull-Up resistor on the dsPIC OC1 PWM line (connected to your 5V MCU power). 
*   *Why this works:* Before the dsPIC boots, this resistor pulls the injection line to `5.0V`. This 5V feeds through the `47kΩ` injection resistor into Pin 2 (VFB), pushing the VFB node slightly above 2.5V. The UC3843 defaults to **0% Duty Cycle** (safely disabled). 
*   Once the dsPIC boots up, it drives the OC1 pin low or high, overpowering the pull-up resistor and taking proper control of the voltage.
