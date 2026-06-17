# Hardware Design Guide: INA181A2 Current Sense Amplifier

This document provides the exact pinout, electrical requirements, and PCB layout rules for integrating the **Texas Instruments INA181A2IDBVR** into the 4kW MPPT Booster.

## 1. Pin Diagram (SOT-23-6 Package)

The INA181 comes in a tiny 6-pin surface mount package. Looking at the top of the chip (with the text `1AED` readable and the dot indicating Pin 1 in the bottom left):

```text
         +---+--+---+
   OUT --| 1      6 |-- REF
         |          |
   GND --| 2      5 |-- IN-
         |          |
    VS --| 3      4 |-- IN+
         +----------+
```

## 2. Pin-by-Pin Wiring Configuration

| Pin | Name | Connection in Your Circuit | Important Notes |
| :--- | :--- | :--- | :--- |
| **1** | **OUT** | To **Pin 3 (ISENSE)** of UC3843 | **CRITICAL:** Do not connect directly! You must use an RC filter (1kΩ resistor in series, 470pF capacitor to ground) to filter out the IGBT turn-on spike. |
| **2** | **GND** | **Analog Ground** | Tie to the clean analog ground. Do not tie to the noisy high-power IGBT ground plane. |
| **3** | **VS** | **+5V DC Supply** | **WARNING:** The INA181 has a maximum supply of 5.5V. **Do NOT connect this to the 15V UC3843 supply.** You must connect this to the clean 5V rail (the same rail powering your dsPIC). Must have a `0.1µF` ceramic capacitor placed right next to Pin 3 and Pin 2. |
| **4** | **IN+** | **Shunt (High Side)** | Connect to the side of the 0.4mΩ shunt facing the **IGBT Emitters**. |
| **5** | **IN-** | **Shunt (Low Side)** | Connect to the side of the 0.4mΩ shunt facing **Main Power Ground**. |
| **6** | **REF** | **Ground (GND)** | **CRITICAL:** Because current only flows in one direction (unidirectional), tie this pin directly to **Pin 2 (GND)**. This tells the chip that 0 Amps = 0 Volts output. |

## 3. The Schematic (ASCII Representation)

```text
                      +5V Supply
                           │
                           │
                        +--+--+                 R_Filter
                        |     |                  (1kΩ)
               +--------|VS   |        +-------[WWWWWW]--------+---> To UC3843 Pin 3
               |        |     |        |                       |
              ===       |  OUT|--------+                      ===  C_Filter
             0.1µF      |     |                              470pF
               |        |     |                                |
               +--------|GND  |                                |
               |        |     |                                |
              GND       |  REF|--------------------------------+---> GND
                        |     |               
               +--------|IN+  |              
               |        |     |
               |   +----|IN-  |
               |   |    +-----+
               |   |
IGBT Emitters  |   |
  (Main High)  |   |
     │         │   │
     +----[ 5x 2mΩ SMD Resistors ]----+
                                      │
                                  Main Power Ground
```

## 4. The Leading Edge Spike Filter (Pin 1 OUT)

When the IGBT turns ON, the reverse recovery of the diode and parasitic capacitances cause a massive, invisible 100ns current spike. If this spike reaches the UC3843, it will falsely shut down the PWM.

To prevent this, you **must** place an RC Low-Pass Filter between the INA181 output and the UC3843 Pin 3:
1.  **Series Resistor:** `1 kΩ`
2.  **Capacitor to Ground:** `470 pF` (Place this ceramic capacitor as close to Pin 3 of the UC3843 as physically possible).
This creates a ~470ns delay filter—enough to hide the turn-on noise, but fast enough to protect against a real short circuit.

## 5. Critical PCB Layout Rules (Kelvin Connection)

When you design the PCB, the way you connect Pin 4 (`IN+`) and Pin 5 (`IN-`) to the SMD resistors is the difference between success and failure.

1. **Kelvin Sensing:** Do NOT just connect `IN-` to the nearest ground plane. You must draw a dedicated, thin copper trace directly from the inner edge of the copper pad of the SMD resistors directly to the `IN-` pin. Do the same for `IN+`. 
2. **Differential Pair:** Route the `IN+` and `IN-` traces right next to each other (parallel) all the way from the resistors to the IC. This ensures that any EMI from the IGBTs hits both traces equally, allowing the INA181's 100dB Common-Mode Rejection to perfectly cancel out the noise.
3. **Trace Length:** Place the INA181 chip as physically close to the 5 SMD resistors as possible. The traces should be very short.

## 5. Electrical Summary for this Design
*   **Shunt Value:** 0.4 mΩ (Five 2mΩ resistors in parallel)
*   **Amplifier Gain:** 50 V/V (Fixed internally in the INA181A2)
*   **Output Equation:** `V_out = (Current × 0.0004) × 50`
*   **Result:** 10A = 0.2V | 25A = 0.5V | 50A = 1.0V (Hardware Shutdown Threshold)
