import subprocess
import os

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

    # Output simulation results
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
        
except FileNotFoundError:
    print(f"Error: '{ngspice}' not found.")
    print("Ensure NgSpice is in your system PATH, or provide the exact path in this script.")
