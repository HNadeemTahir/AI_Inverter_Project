import subprocess
import os
import re
import csv
import time

# 1. Configuration (3D Grid Search)
# ---------------------------------------------------------
THI_STATES = [0, 1]              # 0=Pure Sine, 1=150Hz Flat Top
DT_COMP_STATES = [0, 1]          # 0=Standard, 1=Current-Direction active
VOLTAGE_STEPS = range(350, 460, 10)  # 350V to 450V in 10V steps

CIRCUIT_ORIGINAL = os.path.join("src", "H_Bridge_Full.cir")
CIRCUIT_TEMP = os.path.join("src", "H_Bridge_Temp.cir")
CSV_OUTPUT = os.path.join("results", "inverter_dataset.csv")

local_ngspice = os.path.join("Spice64", "bin", "ngspice_con.exe")
ngspice = local_ngspice if os.path.exists(local_ngspice) else "ngspice_con.exe" if os.name == "nt" else "ngspice"

# 2. Regex Definitions
# ---------------------------------------------------------
# Extracts .meas results
meas_pattern = re.compile(r'^\s*(\w+)\s*=\s*([+-]?\d+\.\d+[eE][+-]?\d+)', re.MULTILINE)

# Finds the DC link voltage line: "V_DC_Link      400_Bus       0               400V"
dc_voltage_pattern = re.compile(r'(V_DC_Link\s+400_Bus\s+0\s+)\d+V', re.IGNORECASE)

# Finds the parameter toggles
thi_pattern = re.compile(r'(\.PARAM\s+THI_ENABLE\s*=\s*)\d+', re.IGNORECASE)
dt_comp_pattern = re.compile(r'(\.PARAM\s+DT_COMP_ENABLE\s*=\s*)\d+', re.IGNORECASE)

# 3. Main Production Loop
# ---------------------------------------------------------
dataset = []

print("🚀 Starting 3D Data Factory Grid Search (44 Simulations)...\n")
start_time = time.time()

# Read the "Master Template" circuit
with open(CIRCUIT_ORIGINAL, "r") as file:
    original_spice_code = file.read()

# 3D Nested Loop
for dt_state in DT_COMP_STATES:
    for thi_state in THI_STATES:
        for v_dc in VOLTAGE_STEPS:
            print(f"⚙️ Simulating: DT_COMP={dt_state} | THI={thi_state} | V_DC={v_dc}V")
            
            # Mutate the netlist
            mod_code = original_spice_code
            mod_code = dc_voltage_pattern.sub(rf'\g<1>{v_dc}V', mod_code)
            mod_code = thi_pattern.sub(rf'\g<1>{thi_state}', mod_code)
            mod_code = dt_comp_pattern.sub(rf'\g<1>{dt_state}', mod_code)
            
            # Save a temporary circuit file for NgSpice to run
            with open(CIRCUIT_TEMP, "w") as file:
                file.write(mod_code)
                
            # Run NgSpice silently on the temporary file
            result = subprocess.run([ngspice, "-b", CIRCUIT_TEMP], capture_output=True, text=True)
            combined_output = result.stdout + "\n" + result.stderr
            
            # Start metrics dictionary with our 3 independent variables
            metrics = {
                "THI": thi_state,
                "DT_COMP": dt_state,
                "V_DC_Link": v_dc
            }
            
            # Extract dependent measurements
            for match in meas_pattern.finditer(combined_output):
                name = match.group(1)
                value = float(match.group(2))
                metrics[name] = value
                
            dataset.append(metrics)
            
            eff = (metrics.get('p_load_avg', 0) / abs(metrics.get('p_dc_input', 1))) * 100 if metrics.get('p_dc_input') else 0
            print(f"   => V_out_rms: {metrics.get('v_out_rms', 0):.1f}V | Efficiency: {eff:.1f}%")

# Clean up temporary file
if os.path.exists(CIRCUIT_TEMP):
    os.remove(CIRCUIT_TEMP)

# 4. Save to CSV
# ---------------------------------------------------------
if dataset:
    headers = list(dataset[0].keys())
    
    with open(CSV_OUTPUT, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset)
        
    elapsed = time.time() - start_time
    print(f"\n✅ Grid Search Complete: {len(dataset)} simulations in {elapsed:.1f} seconds!")
    print(f"📊 Dataset saved to: {CSV_OUTPUT}")
else:
    print("\n❌ Error: No datasets were gathered. Check NgSpice execution.")
