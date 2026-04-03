# ⚡ Inverter Digital Twin (dsPIC30F2010 + FGY75T120SWD)

Professional High-Fidelity Simulation & Modeling of a 220V/50Hz Solar Hybrid Inverter.

## 🚀 Overview
This repository contains the **Digital Twin** for the **H-Bridge Inverter (Version 3.0)** hardware. The project focuses on bridging the gap between firmware development (dsPIC30F2010) and physical power electronics behavior using advanced NGspice modeling.

### Key Specifications:
- **MCU**: dsPIC30F2010 (16-bit High-Performance DSC)
- **Power Stage**: Transformerless H-Bridge
- **Devices**: onsemi FGY75T120SWD (1200V, 75A IGBTs)
- **Isolated Driver**: Toshiba TLP250H (Optoisolated Bootstrap)
- **Topology**: Unipolar SPWM with Closed-Loop PID Control

---

## 🛠️ Project Structure (Global Standard)
Following modern engineering standards, the project is modularized for clarity and reusability:

- `/models`: External device subcircuits (`FGY75T120SWD.lib`, `TLP250H.sub`).
- `/src`: Main simulation netlists (`h_bridge_v3.cir`).
- `/results`: Waveform captures and switching loss analysis.
- `/docs`: Technical documentation and design notes.

---

## 🔬 Modeling Strategy: Version 3.0 (No-Snubber Optimized)
Based on current workshop hardware constraints, the simulation models the **No-Snubber Phase 1** design. We rely on the **1200V** breakdown voltage of the onsemi IGBTs to absorb inductive spikes from the DC bus and stray PCB inductance.

### TLP250H Behavioral Model logic:
The custom `TLP250H.sub` model includes:
- **LED Threshold**: 5mA input trigger point.
- **Propagation Delay**: $150ns$ typical switching delay.
- **Output Stage**: Totem-pole with $\pm 2.0A$ peak source/sink current limit.
- **Isolation**: $1.5pF$ input-to-output coupling capacitance for CMTI analysis.

---

## 📈 Roadmap & Progress
We are currently in a **14-Day Sprint** to finalize the Digital Twin. Our progress is tracked in [task.md](file:///C:/Users/Zaryab%20Kareem/.gemini/antigravity/brain/2a6ccb8d-4e27-4e8c-acb1-df6ee08449b3/task.md).

### ✅ Completed Milestones (Day 1):
- [x] Initialized "Global Standard" directory structure.
- [x] Developed modular `TLP250H` subcircuit.
- [x] Created baseline `README.md` for GitHub-ready portfolio.
