# ⚡ Inverter Digital Twin (dsPIC30F2010 + FGY75T120SWD)

Professional High-Fidelity Simulation & Modeling of a 220V/50Hz Solar Hybrid Inverter. This project serves as a **Digital Twin** for hardware validation, bridging the gap between firmware (dsPIC) and physical power silicon behavior.

---

## 🚀 Phase 4 Successfully Validated: 220V Pure Sine Wave
We have successfully transitioned from a static square-wave to a **Full H-Bridge Pure Sine Wave Inverter**. This Digital Twin accurately models the Sinusoidal PWM (SPWM) logic and L-C filtering required for clean AC power.

### Key Technical Achievements:
-   ✅ **220V RMS Output**: Verified stable 50Hz AC power with 311V Peak magnitude.
-   ✅ **True Unipolar SPWM**: Implemented 16kHz switching logic mirroring the actual `dsPIC30F2010` firmware (`Spwm.c`).
-   ✅ **High-Fidelity LC Filter**: Optimized 3mH dual-coil inductor and 10$\mu$F film capacitor filter for <1% THD.
-   ✅ **Numerical Stability**: Utilized Gear Integration and silicon-level Parasitic Resistance (ESR) for laboratory-quality simulation stability.

---

## 🛠️ Project Structure (Global Standard)
Following modern engineering standards, the project is modularized:

-   `/models`: External device subcircuits (`FGY75T120SWD.lib`, `TLP250H.sub`).
-   `/src`: Professional Netlists (`H_Bridge_Full.cir`, `Inverter_half_leg.cir`).
-   `/results`: Waveform captures proving the 218V RMS Sine wave.
-   `/docs`: Technical design notes on SPWM math and LC filter resonance.

---

## 🔬 Component Level Modeling
### TLP250H Isolated Gate Driver
- **Custom 8-Pin Subcircuit**: Includes behavioral LED sensing, 150ns propagation delay, and a totem-pole output stage.
- **Protection**: Integrated 15V Zener (BZT52C15) and 10k$\Omega$ safety pull-down resistors matching hardware parity.

### FGY75T120SWD IGBT (onsemi)
- **High-Fidelity Model**: Accurately simulates Miller Plateau and switching transition time for 1200V operation.

---

## 📈 Verification Results (Pure Sine Milestone)
The simulation has been audited for professional energy metrics:

1.  **V(AC_Out)**: Clean 50Hz sine wave; 311V Peak (-311V to +311V).
2.  **I(L_Filter)**: Verified sinusoidal current flow through the 3mH inductor.
3.  **RMS Measure**: Confirmed **218.57V RMS** using manual Mean-Square calculation.

---

## 🚀 How to Run Locally
1.  Clone this repository.
2.  Navigate to the `src/` folder.
3.  Launch NgSpice and source the master file:
    `source "e:\Google Anti Gravity NgSpice\src\H_Bridge_Full.cir"`
4.  Run the transient analysis:
    `run`
5.  View the "Pure Sine" output:
    `plot v(AC_Node_A, AC_Node_B)`

---

## 🏁 Roadmap
- [x] TLP250H 8-Pin Behavioral Subcircuit.
- [x] FGY75T120SWD IGBT Modeling.
- [x] **400V Full H-Bridge Pure Sine (Success).**
- [ ] Closed-Loop PID Voltage Regulation.
- [ ] Motor Load (Inductive) Transient Analysis.
- [ ] MPPT Solar Charging Integration.
