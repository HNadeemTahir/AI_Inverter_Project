import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt

CSV_FILE = os.path.join("results", "inverter_dataset.csv")
MODEL_FILE = "inverter_ai_model.pkl"
OUTPUT_IMAGE = os.path.join("results", "14_ai_surrogate_accuracy.png")

def evaluate_and_plot():
    print("Loading data for AI evaluation...")
    if not os.path.exists(CSV_FILE) or not os.path.exists(MODEL_FILE):
        print("Error: Missing dataset or model file.")
        return

    # Load dataset
    df = pd.read_csv(CSV_FILE)
    X = df[['V_DC_Link', 'THI', 'DT_COMP']]
    y_actual = df[['v_out_rms', 'i_load_peak', 'tj_max', 'p_dc_input', 'p_load_avg']]

    # Load AI model
    with open(MODEL_FILE, 'rb') as f:
        model = pickle.load(f)

    # Make predictions for the whole dataset
    y_pred = model.predict(X)

    # Extract specific values for plotting
    v_actual = y_actual['v_out_rms'].values
    v_pred = y_pred[:, 0]

    i_actual = y_actual['i_load_peak'].values
    i_pred = y_pred[:, 1]

    tj_actual = y_actual['tj_max'].values
    tj_pred = y_pred[:, 2]

    # Calculate efficiency
    eff_actual = (y_actual['p_load_avg'].values / abs(y_actual['p_dc_input'].values)) * 100
    p_in_pred = abs(y_pred[:, 3])
    p_out_pred = y_pred[:, 4]
    eff_pred = (p_out_pred / p_in_pred) * 100

    print("Generating Professional Parity Plots...")
    
    # Configure Matplotlib styling
    plt.style.use('dark_background')
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('AI Surrogate Model Accuracy vs Physical SPICE Simulation', fontsize=16, fontweight='bold', color='white')

    # Helper function to plot individual graphs
    def plot_parity(ax, actual, pred, title, unit):
        ax.scatter(actual, pred, color='#00ffcc', alpha=0.6, edgecolors='white', linewidth=0.5)
        
        # Draw the perfect 45-degree parity line
        min_val = min(min(actual), min(pred))
        max_val = max(max(actual), max(pred))
        ax.plot([min_val, max_val], [min_val, max_val], color='#ff003c', linestyle='--', linewidth=2, label='Perfect Prediction')
        
        ax.set_title(title, fontsize=12, color='white')
        ax.set_xlabel(f'NgSpice Physical Value ({unit})', fontsize=10, color='lightgray')
        ax.set_ylabel(f'AI Predicted Value ({unit})', fontsize=10, color='lightgray')
        ax.grid(color='#333333', linestyle=':', linewidth=1)
        ax.legend(loc='upper left', frameon=False, labelcolor='white')

    # Plot 1: Voltage
    plot_parity(axs[0, 0], v_actual, v_pred, 'Output Voltage (RMS)', 'V')
    
    # Plot 2: Peak Current
    plot_parity(axs[0, 1], i_actual, i_pred, 'Peak Load Current', 'A')
    
    # Plot 3: Junction Temp
    plot_parity(axs[1, 0], tj_actual, tj_pred, 'IGBT Junction Temp (Tj_max)', '°C')
    
    # Plot 4: Efficiency
    plot_parity(axs[1, 1], eff_actual, eff_pred, 'System Efficiency', '%')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save the image to the results folder
    plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
    print(f"Success! Professional graph saved to: {OUTPUT_IMAGE}")
    
    # Also show it on screen
    plt.show()

if __name__ == "__main__":
    evaluate_and_plot()
