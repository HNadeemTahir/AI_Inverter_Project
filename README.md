# ⚡ Inverter Digital Twin (dsPIC30F2010 + FGY75T120SWD)

Professional High-Fidelity Simulation & Modeling of a 220V/50Hz Solar Hybrid Inverter. This project serves as a **Digital Twin** for hardware validation, bridging the gap between firmware (dsPIC) and physical power silicon behavior.

## 🚀 Phase 1 Successfully Validated: High-Voltage Half-Bridge
We have successfully constructed and validated the **"Inverter Leg" (Half-Bridge)** under full 400V DC Bus conditions. This Digital Twin mirrors the physical hardware bench used by Nadeem Tahir for solar inverter R&D.

### Key Technical Achievements:
-   ✅ **400V Power Stage**: Verified stable switching under full bus voltage with 10A test load.
-   ✅ **Asymmetric Gate Drive**: Implemented the physical 15$\Omega$ (Turn-ON) and 4.1$\Omega$ (Turn-OFF) network to suppress the **Miller Effect** and ensure fast discharge.
-   ✅ **2.0$\mu$s Dead-Time**: Hard-coded and verified switching gaps between High-Side and Low-Side signals to prevent destructive **Shoot-Through**.
-   ✅ **Bootstrap Lifecycle**: Successfully validated the "Floating Supply" logic for the High-Side TLP250H driver using UF4007 fast-recovery diode and 47$\mu$F bulk storage.

---

## 🛠️ Project Structure (Global Standard)
Following modern engineering standards, the project is modularized for clarity and reusability:

-   `/models`: External device subcircuits (`FGY75T120SWD.lib`, `TLP250H.sub`).
-   `/src`: Professional Netlists (`Inverter_half_leg.cir`).
-   `/results`: Waveform captures proving Dead-Time and Power Stability.
-   `/docs`: Technical design notes on Miller suppression and isolation.

---

## 🔬 Component Level Modeling
### TLP250H Isolated Gate Driver
- **Custom 8-Pin Subcircuit**: Includes behavioral LED sensing, 150ns propagation delay, and a totem-pole output stage.
- **Protection**: Integrated 15V Zener (BZT52C15) and 10k$\Omega$ safety pull-down resistors matching hardware parity.

### FGY75T120SWD IGBT (onsemi)
- **High-Fidelity Model**: Accurately simulates Miller Plateau, saturation resistance, and switching capacitances for 1200V operation.

---

## 📈 Verification Results (Day 4 Milestone)
The simulation has been audited for the following professional metrics:

1.  **V(Phase_Node)**: Clean 400V square wave switching at 16kHz.
2.  **I(V_DC_Link)**: Monitored for current spikes; verified zero shoot-through during the 2.0$\mu$s dead-time gap.
3.  **V(HS_Gate)**: Verified successful "Floating" to 412V (400V Bus + 12V Bootstrap).

---

## 🚀 How to Run locally
1.  Navigate to the `src/` folder.
2.  Launch NgSpice and source the master file:
    `source "e:\Google Anti Gravity NgSpice\src\Inverter_half_leg.cir"`
3.  Run the transient analysis:
    `run`
4.  View the power stage transitions:
    `plot v(LS_Gate) v(HS_Gate) v(Phase_Node)`

---

## 🏁 Roadmap
- [x] TLP250H 8-Pin Behavioral Subcircuit.
- [x] FGY75T120SWD IGBT Modeling.
- [x] **400V Half-Bridge Verification (Success).**
- [ ] Closed-Loop SPWM Control (dsPIC logic integration).
- [ ] Full H-Bridge Hade-to-Transformer Coupling.
