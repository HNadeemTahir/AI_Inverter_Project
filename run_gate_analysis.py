# =============================================================================
#  run_gate_analysis.py — IGBT Gate Capacitance Charge/Discharge Dashboard
#  Version 9.0
# =============================================================================
#  Author   : Nadeem Tahir (Embedded Systems & Power Electronics Engineer)
#  Tools    : NgSpice 46, Python 3.x, Matplotlib, NumPy
#  Date     : 27 April 2026
#  Netlist  : src/Gate_Analysis.cir
# -----------------------------------------------------------------------------
#  500µs high-resolution (10ns step) transient analysis of the asymmetric
#  gate drive network on parallel STGW60H65DFB IGBTs. Generates a 5-panel
#  dashboard characterizing:
#    - Full switching overview (500µs)
#    - Zoomed turn-on/turn-off transitions with Miller Plateau markers
#    - Individual turn-ON detail: τ = R_ON × Cge = 15Ω × 20nF = 300ns
#    - Individual turn-OFF detail: τ = R_OFF × Cge = 5.6Ω × 20nF = 112ns
#    - Engineering specifications summary table
# =============================================================================

import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def run_gate_analysis():
    ngspice_path = r"E:\Project NgSpice\Spice64\bin\ngspice_con.exe"
    netlist_path = os.path.join("src", "Gate_Analysis.cir")
    results_file = "gate_analysis_results.txt"

    print("Running Gate Capacitance Charge/Discharge Analysis...")
    try:
        if os.path.exists(results_file):
            os.remove(results_file)
        subprocess.run([ngspice_path, "-b", netlist_path], check=True)
    except Exception as e:
        print(f"Error running NgSpice: {e}")
        return

    if not os.path.exists(results_file):
        print(f"Error: Results file '{results_file}' not found.")
        return

    print("Loading gate analysis data...")
    data = np.loadtxt(results_file)
    time_s  = data[:, 0]
    v_g1    = data[:, 1]   # IGBT Q1 Gate Voltage
    v_g2    = data[:, 3]   # IGBT Q2 Gate Voltage
    v_drv   = data[:, 5]   # FOD3150 Driver Output
    v_pwm   = data[:, 7]   # PWM Logic Signal
    v_emit  = data[:, 9]   # Emitter (Reference)

    time_us = time_s * 1e6  # Convert to microseconds

    # ── Find the first rising edge of DRV for zoom window ──
    drv_thresh = 7.5
    rise_idx = np.where(np.diff((v_drv > drv_thresh).astype(int)) > 0)[0]
    fall_idx = np.where(np.diff((v_drv > drv_thresh).astype(int)) < 0)[0]

    if len(rise_idx) == 0:
        print("Warning: No gate switching edges found. Check simulation.")
        zoom_start_us, zoom_end_us = 40.0, 70.0
    else:
        # Zoom window: 5us before first rise to 10us after first fall
        zoom_start_us = time_us[rise_idx[0]] - 3.0
        if len(fall_idx) > 0 and fall_idx[0] > rise_idx[0]:
            zoom_end_us = time_us[fall_idx[0]] + 5.0
        else:
            zoom_end_us = zoom_start_us + 20.0

    zoom_mask = (time_us >= zoom_start_us) & (time_us <= zoom_end_us)
    t_zoom    = time_us[zoom_mask]
    g1_zoom   = v_g1[zoom_mask]
    g2_zoom   = v_g2[zoom_mask]
    drv_zoom  = v_drv[zoom_mask]

    # ── IGBT Gate Threshold & Miller Plateau Reference Lines ──
    VGE_TH  = 6.0   # STGW60H65DFB threshold voltage (Vgs_th)
    VGE_MIL = 9.0   # Approximate Miller plateau voltage
    VGE_MAX = 15.0  # Full saturation voltage

    # ─────────────────────────────────────────────────────────
    # DASHBOARD LAYOUT
    # ─────────────────────────────────────────────────────────
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(20, 13))
    fig.suptitle(
        "4kW MPPT Booster — Gate Capacitance Charge/Discharge Analysis\n"
        "Asymmetric Gate Drive: 15Ω Turn-ON  |  5.6Ω + 1N4148 Turn-OFF",
        fontsize=14, fontweight='bold', color='white', y=0.98
    )
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.65, wspace=0.35)

    # ── PLOT 1: Full 500us Overview (top-left) ──
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(time_us, v_drv, color='#FFD700', linewidth=1.0, label='FOD3150 Driver Output (DRV)')
    ax1.plot(time_us, v_g1,  color='cyan',    linewidth=1.2, label='Q1 Gate Voltage (Vge1)', alpha=0.9)
    ax1.plot(time_us, v_g2,  color='#FF6B6B', linewidth=1.0, label='Q2 Gate Voltage (Vge2)', alpha=0.7, linestyle='--')
    ax1.axhline(VGE_TH,  color='orange', linestyle=':', linewidth=1.0, label=f'Vge Threshold ({VGE_TH}V)')
    ax1.axhline(VGE_MAX, color='gray',   linestyle=':', linewidth=0.8, label=f'Full Saturation ({VGE_MAX}V)')
    ax1.set_ylabel("Gate Voltage (V)", fontsize=10)
    ax1.set_xlabel("Time (µs)", fontsize=10)
    ax1.set_title("Full Overview: Gate Drive vs. Q1 & Q2 Gate Voltage (500µs)", fontsize=11)
    ax1.legend(loc='lower right', fontsize=7, framealpha=0.6)
    ax1.grid(color='#333333', linestyle='--', linewidth=0.6)
    ax1.set_ylim(-2, 18)

    # ── PLOT 2: Zoomed Turn-ON (bottom-left) ──
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t_zoom, drv_zoom, color='#FFD700', linewidth=1.5, label='DRV Signal')
    ax2.plot(t_zoom, g1_zoom,  color='cyan',    linewidth=2.0, label='Q1 Gate (Vge1)')
    ax2.axhline(VGE_TH,  color='orange', linestyle='--', linewidth=1.2, label=f'Threshold ({VGE_TH}V)')
    ax2.axhline(VGE_MIL, color='#9B59B6', linestyle='--', linewidth=1.2, label=f'Miller Plateau (~{VGE_MIL}V)')
    ax2.axhline(VGE_MAX, color='gray',   linestyle=':', linewidth=0.8, label=f'Saturation ({VGE_MAX}V)')
    ax2.fill_between(t_zoom, 0, g1_zoom,
                     where=(g1_zoom >= VGE_TH),
                     alpha=0.15, color='cyan',
                     label='IGBT Conducting Zone')
    ax2.set_ylabel("Gate Voltage (V)", fontsize=10)
    ax2.set_xlabel("Time (µs)", fontsize=10)
    ax2.set_title("Zoomed: Turn-ON & Turn-OFF Transition\n(15Ω charge vs 5.6Ω discharge)", fontsize=10)
    ax2.legend(loc='lower center', fontsize=7.5, framealpha=0.85, ncol=2)
    ax2.grid(color='#333333', linestyle='--', linewidth=0.6)
    ax2.set_ylim(-2, 18)

    # ── PLOT 3: Turn-ON only (very tight zoom) ──
    if len(rise_idx) > 0:
        ton_start = time_us[rise_idx[0]] - 0.5
        ton_end   = time_us[rise_idx[0]] + 2.5
        ton_mask  = (time_us >= ton_start) & (time_us <= ton_end)
        t_on  = time_us[ton_mask]
        g1_on = v_g1[ton_mask]
        drv_on = v_drv[ton_mask]
    else:
        t_on, g1_on, drv_on = t_zoom[:50], g1_zoom[:50], drv_zoom[:50]

    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(t_on, drv_on,  color='#FFD700', linewidth=1.5, label='DRV (Driver Out)')
    ax3.plot(t_on, g1_on,   color='cyan',    linewidth=2.5, label='Q1 Vge (Turn-ON)')
    ax3.axhline(VGE_TH,  color='orange',  linestyle='--', linewidth=1.2, label=f'Vge_th = {VGE_TH}V')
    ax3.axhline(VGE_MIL, color='#9B59B6', linestyle='--', linewidth=1.2, label=f'Miller Plateau ≈ {VGE_MIL}V')
    ax3.set_ylabel("Gate Voltage (V)", fontsize=10)
    ax3.set_xlabel("Time (µs)", fontsize=10)
    ax3.set_title(f"Turn-ON Detail: R_ON = 15Ω\nτ = R × Cge ≈ 15 × 20nF = 300ns", fontsize=10)
    ax3.legend(loc='lower right', fontsize=7.5, framealpha=0.85)
    ax3.grid(color='#333333', linestyle='--', linewidth=0.6)
    ax3.set_ylim(-2, 18)

    # ── PLOT 4: Turn-OFF only ──
    if len(fall_idx) > 0 and fall_idx[0] > (rise_idx[0] if len(rise_idx) > 0 else 0):
        toff_start = time_us[fall_idx[0]] - 0.5
        toff_end   = time_us[fall_idx[0]] + 2.5
        toff_mask  = (time_us >= toff_start) & (time_us <= toff_end)
        t_off  = time_us[toff_mask]
        g1_off = v_g1[toff_mask]
        drv_off = v_drv[toff_mask]
    else:
        t_off, g1_off, drv_off = t_zoom[:50], g1_zoom[:50], drv_zoom[:50]

    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(t_off, drv_off,  color='#FFD700', linewidth=1.5, label='DRV (Driver Out)')
    ax4.plot(t_off, g1_off,   color='#FF6B6B', linewidth=2.5, label='Q1 Vge (Turn-OFF)')
    ax4.axhline(VGE_TH,  color='orange', linestyle='--', linewidth=1.2, label=f'Vge_th = {VGE_TH}V')
    ax4.axhline(0,        color='gray',   linestyle=':', linewidth=0.8)
    ax4.set_ylabel("Gate Voltage (V)", fontsize=10)
    ax4.set_xlabel("Time (µs)", fontsize=10)
    ax4.set_title(f"Turn-OFF Detail: R_OFF = 5.6Ω + 1N4148  |  τ ≈ 112ns", fontsize=9)
    ax4.legend(loc='upper right', fontsize=7.5, framealpha=0.85)
    ax4.grid(color='#333333', linestyle='--', linewidth=0.6)
    ax4.set_ylim(-2, 18)

    # ── PLOT 5: Engineering Summary Table ──
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    table_data = [
        ["Parameter",           "Turn-ON",         "Turn-OFF"],
        ["Gate Resistor",       "15 Ω",            "5.6 Ω + 1N4148"],
        ["Time Constant (τ)",   "~300 ns",         "~112 ns"],
        ["Speed",               "Controlled",      "Fast"],
        ["Purpose",             "Limit di/dt",     "Suppress Miller Effect"],
        ["IGBT Threshold (Vth)","6.0 V",           "6.0 V"],
        ["Miller Plateau",      "~9 V",            "~9 V"],
        ["Full Saturation",     "15 V",            "—"],
        ["Protection Target",   "EMI / Diode Rec.","Shoot-Through"],
    ]
    col_colors = [['#1a1a2e']*3] + \
                 [['#16213e', '#0f3460', '#533483']] * (len(table_data)-1)
    tbl = ax5.table(
        cellText=table_data[1:],
        colLabels=table_data[0],
        cellLoc='center',
        loc='center',
        cellColours=col_colors[1:]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.0, 1.6)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_text_props(color='white')
        cell.set_edgecolor('#444444')
        if r == 0:
            cell.set_text_props(color='#FFD700', fontweight='bold')
    ax5.set_title("Asymmetric Gate Drive Specifications", fontsize=10, color='white')

    # ── Save & Show ──
    if not os.path.exists("results"):
        os.makedirs("results")
    plt.savefig("results/gate_analysis_dashboard.png", dpi=300, bbox_inches='tight')
    print("Gate analysis simulation complete. Output saved to results/gate_analysis_dashboard.png")
    plt.show()

if __name__ == "__main__":
    run_gate_analysis()
