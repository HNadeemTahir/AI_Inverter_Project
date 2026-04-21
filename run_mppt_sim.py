import os
import subprocess
import matplotlib.pyplot as plt

print("Running 4kW MPPT Boost Converter simulation...")

# Run Ngspice headlessly
netlist_path = r"src\MPPT_Booster.cir"
spice_executable = r"Spice64\bin\ngspice_con.exe"

print("Executing SPICE simulation (this will take a few seconds to process the 20kHz switching)...")
if os.path.exists("results.txt"):
    os.remove("results.txt")

subprocess.run(f'"{spice_executable}" -b "{netlist_path}"', shell=True)

print("Loading simulation data...")
times = []
v_in_soft = []
v_dc_out = []
v_pwm = []
i_l1 = []

if os.path.exists("results.txt"):
    with open("results.txt", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 8:
                times.append(float(parts[0]))
                v_in_soft.append(float(parts[1]))
                v_dc_out.append(float(parts[3]))
                v_pwm.append(float(parts[5]))
                i_l1.append(float(parts[7]))

    # --- Plotting ---
    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # 1. Voltage Graph (Input vs Output)
    vin_label = f"Input PV ({int(round(v_in_soft[0]))}V)"
    ax1.plot(times, v_in_soft, label=vin_label, color="cyan", alpha=0.7)
    ax1.plot(times, v_dc_out, label="DC Bus Output (380V target)", color="magenta", linewidth=2)
    ax1.set_ylabel("Voltage (V)", fontsize=12)
    vin_val = int(round(v_in_soft[0]))
    ax1.set_title(f"MPPT Voltage Regulation ({vin_val}V \u2794 380V)", fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(color='#444444', linestyle='--')

    # 2. PWM Gate Signal
    ax2.plot(times, v_pwm, label="DSP PWM Gate Driver Signal (0 to 3.3V)", color="#FFD700")
    ax2.set_ylabel("Logic Voltage (V)", fontsize=12)
    ax2.legend(loc='upper left')
    ax2.grid(color='#444444', linestyle='--')

    # 3. Inductor Current
    ax3.plot(times, i_l1, label="Inductor Current I(L1)", color="#00FF00")
    ax3.set_ylabel("Current (Amps)", fontsize=12)
    ax3.set_xlabel("Simulation Time (Seconds)", fontsize=12)
    ax3.legend(loc='upper left')
    ax3.grid(color='#444444', linestyle='--')

    plt.tight_layout()
    plt.savefig("results/mppt_closed_loop_analysis.png", dpi=300)
    print("\nSimulation complete. Plot saved to results/mppt_closed_loop_analysis.png")
    plt.show()
else:
    print("Error: results.txt not found. The SPICE simulation failed to compute.")
