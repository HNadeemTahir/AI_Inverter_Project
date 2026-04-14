import subprocess
import os
import re

# By default, assumes ngspice is in the system PATH.
# We also check for a local portable install in the repository directory.
local_ngspice = os.path.join("Spice64", "bin", "ngspice_con.exe")
if os.path.exists(local_ngspice):
    ngspice = local_ngspice
else:
    ngspice = "ngspice" if os.name != "nt" else "ngspice_con.exe"

# Relative path to the simulation file from the repository root
circuit = os.path.join("src", "H_Bridge_Full.cir")

try:
    # Run NgSpice in batch mode
    result = subprocess.run(
        [ngspice, "-b", circuit],
        capture_output=True,
        text=True
    )

    # Dictionary to hold our parsed metrics
    metrics = {}
    
    # Regex pattern to match ".meas" output lines
    # Example: v_out_rms     =   1.92116e+02 from= ...
    pattern = re.compile(r'^\s*(\w+)\s*=\s*([+-]?\d+\.\d+[eE][+-]?\d+)', re.MULTILINE)
    
    # .meas results usually go to stderr in batch mode, but we scan both
    combined_output = result.stdout + "\n" + result.stderr
    
    for match in pattern.finditer(combined_output):
        name = match.group(1)
        value = float(match.group(2))
        metrics[name] = value

    print("\n✅ Simulation Complete!")
    print("-" * 35)
    print("      EXTRACTED METRICS")
    print("-" * 35)
    
    if not metrics:
        print("No measurements found! Dumping raw output for debug:")
        print(result.stderr)
    else:
        for key, val in metrics.items():
            print(f"{key:15s} {val:12.3f}")
        print("-" * 35)
        
except FileNotFoundError:
    print(f"Error: '{ngspice}' not found.")
    print("Ensure NgSpice is in your system PATH, or provide the exact path in this script.")
