import subprocess
import os
import re
import csv
import time

# 1. Configuration
# ---------------------------------------------------------
# Range of DC input voltages to simulate (350V to 450V in 10V steps)
VOLTAGE_STEPS = range(350, 460, 10)

CIRCUIT_ORIGINAL = os.path.join("src", "H_Bridge_Full.cir")
CIRCUIT_TEMP = os.path.join("src", "H_Bridge_Temp.cir")
CSV_OUTPUT = os.path.join("results", "inverter_dataset.csv")

local_ngspice = os.path.join("Spice64", "bin", "ngspice_con.exe")
ngspice = local_ngspice if os.path.exists(local_ngspice) else "ngspice_con.exe" if os.name == "nt" else "ngspice"

# 2. Regex Definitions
# ---------------------------------------------------------
# Hunts for our output measurements
meas_pattern = re.compile(r'^\s*(\w+)\s*=\s*([+-]?\d+\.\d+[eE][+-]?\d+)', re.MULTILINE)

# Hunts for the DC Voltage Source line in the .cir file so we can modify it
# Ex: "V_DC_Link      400_Bus       0               400V"
dc_voltage_pattern = re.compile(r'(V_DC_Link\s+400_Bus\s+0\s+)\d+V', re.IGNORECASE)

# 3. Main Production Loop
# ---------------------------------------------------------
dataset = []

print("🚀 Starting Data Factory AI Extraction...\n")
start_time = time.time()

# Read the "Master Template" circuit
with open(CIRCUIT_ORIGINAL, "r") as file:
    original_spice_code = file.read()

for v_dc in VOLTAGE_STEPS:
    print(f"⚙️ Running simulation for V_DC = {v_dc}V...")
    
    # Modify the text to inject the new voltage
    # Replaces "400V" with the new "350V", "360V", etc.
    modified_spice_code = dc_voltage_pattern.sub(rf'\g<1>{v_dc}V', original_spice_code)
    
    # Save a temporary circuit file for NgSpice to run
    with open(CIRCUIT_TEMP, "w") as file:
        file.write(modified_spice_code)
        
    # Run NgSpice silently on the temporary file
    result = subprocess.run([ngspice, "-b", CIRCUIT_TEMP], capture_output=True, text=True)
    combined_output = result.stdout + "\n" + result.stderr
    
    # Extract the metrics
    metrics = {"V_DC_Link": v_dc} # Start our dictionary with the independent variable
    
    for match in meas_pattern.finditer(combined_output):
        name = match.group(1)
        value = float(match.group(2))
        metrics[name] = value
        
    dataset.append(metrics)
    print(f"   => V_out_rms = {metrics.get('v_out_rms', 0):.2f} V, Efficiency = {(metrics.get('p_load_avg', 0) / abs(metrics.get('p_dc_input', 1))) * 100:.1f}%")

# Clean up temporary file
if os.path.exists(CIRCUIT_TEMP):
    os.remove(CIRCUIT_TEMP)

# 4. Save to CSV
# ---------------------------------------------------------
if dataset:
    # Use keys from the first dictionary to define the CSV column headers
    headers = list(dataset[0].keys())
    
    with open(CSV_OUTPUT, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset)
        
    elapsed = time.time() - start_time
    print(f"\n✅ Data Factory Complete in {elapsed:.1f} seconds!")
    print(f"📊 Dataset saved to: {CSV_OUTPUT}")
else:
    print("\n❌ Error: No datasets were gathered. Check NgSpice execution.")
