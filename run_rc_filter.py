# =============================================================================
#  run_rc_filter.py — LEB Filter Propagation Delay Analysis
#  Version 9.0
# =============================================================================
#  Author   : Nadeem Tahir (Embedded Systems & Power Electronics Engineer)
#  Tools    : NgSpice 46, Python 3.x, Matplotlib, NumPy
#  Date     : 27 April 2026
#  Netlist  : src/RC_Filter_Test.cir
# -----------------------------------------------------------------------------
#  Simulates a dead-short event at the INA181A2 current sense amplifier
#  output and measures the propagation delay through the 1kΩ + 470pF LEB
#  filter before the signal crosses the 1.0V UC3843 ISENSE trip threshold.
#  τ = R × C = 1000 × 470e-12 = 470ns blanking window.
# =============================================================================

import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

def run_rc_simulation():
    ngspice_path = r"E:\Project NgSpice\Spice64\bin\ngspice_con.exe"
    netlist_path = os.path.join("src", "RC_Filter_Test.cir")
    results_file = "rc_delay_results.txt"

    print("Running LEB RC Filter Propagation Delay Simulation...")
    if os.path.exists(results_file):
        os.remove(results_file)

    subprocess.run([ngspice_path, "-b", netlist_path], check=True)

    data = np.loadtxt(results_file)
    time_us = data[:, 0] * 1e6   # Seconds → microseconds
    v_ina   = data[:, 1]          # INA181 output (instantaneous fault signal)
    v_uc    = data[:, 3]          # Filtered signal at UC3843 Pin 3

    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))

    plt.plot(time_us, v_ina, color="#FFD700", linewidth=2,
             label="INA181 Output (Instant Short Circuit)")
    plt.plot(time_us, v_uc, color="cyan", linewidth=2.5,
             label="Filtered Signal at UC3843 Pin 3")
    plt.axhline(1.0, color="red", linestyle="--",
                label="UC3843 Trip Threshold (1.0V)")

    plt.title("RC Filter Propagation Delay (1kΩ + 470pF)", fontsize=14,
              fontweight='bold', color='white')
    plt.xlabel("Time (µs)", fontsize=12)
    plt.ylabel("Voltage (V)", fontsize=12)
    plt.xlim(0.8, 2.5)
    plt.ylim(0, 1.6)
    plt.grid(color='#444444', linestyle='--')
    plt.legend(loc="lower right")

    if not os.path.exists("results"):
        os.makedirs("results")
    plt.savefig("results/20_Rc Filter Propagation Delay.png", dpi=300)
    print("Simulation complete. Graph saved to results/20_Rc Filter Propagation Delay.png")
    plt.show()

if __name__ == "__main__":
    run_rc_simulation()

