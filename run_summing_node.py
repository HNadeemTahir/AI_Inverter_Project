# =============================================================================
#  run_summing_node.py — MPPT Summing Node 4-Point Duty Cycle Sweep
#  Version 9.0
# =============================================================================
#  Author   : Nadeem Tahir (Embedded Systems & Power Electronics Engineer)
#  Tools    : NgSpice 46, Python 3.x, Matplotlib
#  Date     : 27 April 2026
#  Netlist  : src/Summing_Node_Test.cir
# -----------------------------------------------------------------------------
#  Parametric sweep of the dsPIC30F2010 OC1 PWM duty cycle at 25%, 50%,
#  75%, and 100%. For each sweep point, the script modifies the PULSE
#  source in the SPICE netlist, runs NgSpice in batch mode, and extracts
#  the RC filter output and UC3843 Pin 2 voltage.
#
#  The resulting 4-panel dashboard proves the KCL summing node physics:
#    25% PWM → Pin 2 = 2.33V → Boosting (MAX POWER)
#    50% PWM → Pin 2 = 2.51V → Shut Down
#    75% PWM → Pin 2 = 2.69V → Shut Down
#   100% PWM → Pin 2 = 2.88V → Shut Down
#
#  The netlist is restored to its original state (25% default) after sweep.
# =============================================================================

import os
import subprocess
import matplotlib.pyplot as plt

ngspice_path = r"E:\Project NgSpice\Spice64\bin\ngspice_con.exe"
netlist_path = os.path.join("src", "Summing_Node_Test.cir")

duty_cycles = [25, 50, 75, 100]
high_times = [12.5, 25.0, 37.5, 49.9] # 49.9 instead of 50 to prevent SPICE errors

results = {}

print("Running Multi-Stage NGSpice Simulation...")

for dc, ht in zip(duty_cycles, high_times):
    print(f"--> Simulating {dc}% Duty Cycle...")
    
    # Read the original netlist
    with open(netlist_path, "r") as f:
        lines = f.readlines()
        
    # Modify the PULSE line
    with open(netlist_path, "w") as f:
        for line in lines:
            if "V_DSPIC OC1_PIN 0 PULSE" in line:
                f.write(f"V_DSPIC OC1_PIN 0 PULSE(0 5 0 10n 10n {ht}u 50u)\n")
            else:
                f.write(line)
                
    # Run NGSpice
    subprocess.run([ngspice_path, "-b", netlist_path], check=True, capture_output=True)
    
    # Read the results
    time_ms, v_dspic, v_filter, v_pin2 = [], [], [], []
    with open("summing_node_data.txt", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                time_ms.append(float(parts[0]) * 1000)
                v_dspic.append(float(parts[1]))
                v_filter.append(float(parts[3]))
                v_pin2.append(float(parts[5]))
                
    results[dc] = {"time": time_ms, "filter": v_filter, "pin2": v_pin2}

# Plotting the 4 graphs side-by-side
plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("MPPT Summing Node Physics: Duty Cycle Sweep", fontsize=18, fontweight='bold', color='white')

axs = axs.flatten()

for i, dc in enumerate(duty_cycles):
    ax = axs[i]
    time = results[dc]["time"]
    v_filter = results[dc]["filter"]
    v_pin2 = results[dc]["pin2"]

    ax.plot(time, v_filter, color='cyan', linewidth=2, label="RC Filter (DC Avg)")
    ax.plot(time, v_pin2, color='magenta', linewidth=3, label="Pin 2 Voltage")
    ax.axhline(y=2.50, color='red', linestyle='--', linewidth=2, label="UC3843 Cutoff (2.50V)")

    final_pin2 = v_pin2[-1]

    ax.set_title(f"{dc}% Duty Cycle", fontsize=14, fontweight='bold', color='white')
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Voltage (V)")
    ax.set_ylim(0, 5)
    ax.grid(color='#444444', linestyle='--')
    ax.legend(loc="upper left")

    # Status annotation
    if final_pin2 < 2.49:
        status = "BOOSTING (MAX POWER)"
        scolor = "#00FF00"
    elif final_pin2 > 2.51:
        status = "SHUT DOWN (0 POWER)"
        scolor = "#FF4444"
    else:
        status = "NEUTRAL / BALANCED"
        scolor = "#FFD700"

    ax.text(20, 0.5, f"Final Pin 2: {final_pin2:.2f}V\n{status}",
            fontsize=12, fontweight='bold', color=scolor,
            bbox=dict(facecolor='#1a1a2e', alpha=0.9, edgecolor=scolor))

plt.tight_layout()
plt.subplots_adjust(top=0.92)
if not os.path.exists("results"):
    os.makedirs("results")
plt.savefig("results/21_MPPT_Summing_Node.png", dpi=300)
print("Simulation complete. Graph saved to results/21_MPPT_Summing_Node.png")
plt.show()

# Restore original file state just in case
with open(netlist_path, "r") as f:
    lines = f.readlines()
with open(netlist_path, "w") as f:
    for line in lines:
        if "V_DSPIC OC1_PIN 0 PULSE" in line:
            f.write("V_DSPIC OC1_PIN 0 PULSE(0 5 0 10n 10n 12.5u 50u)\n")
        else:
            f.write(line)
