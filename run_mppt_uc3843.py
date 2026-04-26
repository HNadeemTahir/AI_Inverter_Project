# =============================================================================
#  run_mppt_uc3843.py — UC3843 Closed-Loop Boost Converter Dashboard
#  Version 9.0
# =============================================================================
#  Author   : Nadeem Tahir (Embedded Systems & Power Electronics Engineer)
#  Tools    : NgSpice 46, Python 3.x, Matplotlib, NumPy
#  Date     : 27 April 2026
#  Netlist  : src/MPPT_Booster_UC3843.cir
# -----------------------------------------------------------------------------
#  Runs a 60ms transient simulation of the UC3843 peak-current-mode boost
#  converter. Generates a 3-panel dashboard showing:
#    Panel 1: DC bus output voltage vs 380V regulation target
#    Panel 2: 20kHz gate drive signal (FOD3150 output)
#    Panel 3: Boost inductor L1 current waveform
# =============================================================================

import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

def run_simulation():
    ngspice_path = r"E:\Project NgSpice\Spice64\bin\ngspice_con.exe"
    netlist_path = os.path.join("src", "MPPT_Booster_UC3843.cir")
    results_file = "uc3843_results.txt"

    print("Running UC3843 Closed-Loop Boost Converter Simulation...")
    try:
        if os.path.exists(results_file):
            os.remove(results_file)
        subprocess.run([ngspice_path, "-b", netlist_path], check=True)
    except Exception as e:
        print(f"NgSpice error: {e}")
        return

    if not os.path.exists(results_file):
        print(f"Results file '{results_file}' not found. Check NgSpice wrdata directive.")
        return

    data = np.loadtxt(results_file)
    time  = data[:, 0]   # Time axis (seconds)
    v_out = data[:, 1]   # DC bus output voltage
    i_ind = data[:, 3]   # Inductor L1 current
    v_pwm = data[:, 5]   # Gate drive signal

    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Panel 1: DC Bus Voltage Regulation
    ax1.plot(time * 1000, v_out, color="magenta", linewidth=2, label="DC Bus Output (380V)")
    ax1.axhline(y=380, color='r', linestyle='--', label="380V Setpoint")
    ax1.set_ylabel("Voltage (V)", fontsize=10)
    ax1.set_title("4kW MPPT DC-DC Boost Converter Analysis", fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(color='#444444', linestyle='--')

    # Panel 2: Gate Drive Signal (20kHz switching)
    ax2.plot(time * 1000, v_pwm, color="#FFD700", label="Gate Drive Signal (0-15V)")
    ax2.set_ylabel("Gate (V)", fontsize=10)
    ax2.legend(loc='upper right')
    ax2.grid(color='#444444', linestyle='--')

    # Panel 3: Inductor Current
    ax3.plot(time * 1000, i_ind, color="#00FF00", label="L1 Coil Current")
    ax3.set_ylabel("Current (A)", fontsize=10)
    ax3.set_xlabel("Time (ms)", fontsize=12)
    ax3.legend(loc='upper right')
    ax3.grid(color='#444444', linestyle='--')

    plt.tight_layout()
    if not os.path.exists("results"):
        os.makedirs("results")
    plt.savefig("results/22_MPPT_Dc-Dc_UC3843.png", dpi=300)
    print("Simulation complete. Graph saved to results/22_MPPT_Dc-Dc_UC3843.png")
    plt.show()

if __name__ == "__main__":
    run_simulation()

