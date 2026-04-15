import pandas as pd
import pickle
import os
import warnings

# Suppress sklearn warnings about feature names
warnings.filterwarnings("ignore")

MODEL_FILE = "inverter_ai_model.pkl"

def predict_inverter():
    if not os.path.exists(MODEL_FILE):
        print(f"Error: Cannot find {MODEL_FILE}. Run train_ai.py first!")
        return

    # Load the trained AI brain
    with open(MODEL_FILE, 'rb') as f:
        model = pickle.load(f)

    print("\n========================================================")
    print(" INVERTER AI SURROGATE MODEL - INSTANT PREDICTOR")
    print("========================================================\n")
    
    try:
        v_dc = float(input("Enter V_DC_Link (e.g. 350 to 450): "))
        thi = float(input("Enter THI_ENABLE (0 or 1): "))
        dt_comp = float(input("Enter DT_COMP_ENABLE (0 or 1): "))
    except ValueError:
        print("Invalid input! Please enter numbers.")
        return

    # Create input DataFrame perfectly matching the AI's training structure
    X_input = pd.DataFrame({'V_DC_Link': [v_dc], 'THI': [thi], 'DT_COMP': [dt_comp]})

    # Ask the Random Forest to predict the physics!
    prediction = model.predict(X_input)[0]

    # Unpack the 5 predicted physics targets we trained on
    v_rms = prediction[0]
    i_peak = prediction[1]
    tj_max = prediction[2]
    p_in = abs(prediction[3])
    p_out = prediction[4]
    
    efficiency = (p_out / p_in) * 100 if p_in > 0 else 0

    print("\n========================================================")
    print(" PREDICTED PHYSICAL PERFORMANCE (0.01 seconds) ")
    print("========================================================")
    if thi == 1 and dt_comp == 1:
        print("* ULTIMATE STRATEGY DETECTED *")
    elif thi == 0 and dt_comp == 0:
        print("! BARE SPWM DETECTED (High Harmonic Losses Allowed) !")

    print(f" Output Voltage (RMS)  : {v_rms:.1f} V")
    print(f" Peak Load Current     : {i_peak:.2f} A")
    print(f" IGBT Junction Temp    : {tj_max:.1f} °C")
    print(f" Inverter Efficiency   : {efficiency:.1f} %")
    print("========================================================\n")

if __name__ == "__main__":
    while True:
        predict_inverter()
        again = input("Run another prediction? (y/n): ")
        if again.lower() != 'y':
            break
