# 🏗️ Phase 1: Subcircuit Engineering (Weeks 1-4)
Goal: Master the physics and behavioral logic of power electronic components.

- [x] **Week 3: The Isolated Gate Driver (TLP250H)**
    - [x] Manually write the Subcircuit Header (`.SUBCKT`).
    - [x] Implement the Input LED Stage with Behavioral Current Sensing.
    - [x] Model the **Propagation Delay** using an RC Time Constant ($150ns$).
    - [x] Design the High-Speed Totem-Pole Output Stage.
    - [x] Measure $I_{peak}$ to verify $\pm 2.0A$ limit.

---

- [ ] **Week 4: Physical Transistor Modeling (FGY75T120SWD)**
    - [ ] Translate a datasheet into SPICE primitives.
    - [ ] Model Gate Capacitance ($C_{ies}$) and its change with $V_{ce}$.
    - [ ] Simulate the Miller Effect ($C_{res}$) during a 400V transition.

---

## ⚡ Phase 2: Power Electronic Building Blocks (Weeks 5-8)
Goal: Build the H-Bridge "Digital Twin" from the ground up.

- [ ] **Week 5: The Inverter Leg**
    - [ ] Create a reusable `half_bridge.sub` module.
    - [ ] Validate high-side floating node reference.
- [ ] **Week 6: Bootstrap & Parasitics**
    - [ ] Model real-world inductor ESR and capacitor ESL.
- [ ] **Week 7: Dead-Time & Interlocks**
    - [ ] Prove ZERO shoot-through using cross-conduction analysis.
