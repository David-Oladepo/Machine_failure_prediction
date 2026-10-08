import warnings

import streamlit as st 
import pandas as pd 
import joblib 
import json


model = joblib.load("machine_failure_model.pkl")
print("Model loaded successfully.")

# Page configuration 
st.set_page_config( 
    page_title="Machine Failure Prediction", 
    page_icon="⚙️", 
    layout="centered" 
) 
# Title 
st.title("Predictive Maintenance: Machine Failure Prediction") 

st.write( 
"Enter the machine operating parameters below " 
"to estimate the probability of machine failure." 
) 
# Load model 
model = joblib.load("machine_failure_model.pkl") 

# Load final threshold 
with open("final_threshold.json", "r") as file: 
    threshold_data = json.load(file) 

final_threshold = threshold_data["final_threshold"] 

# Load training ranges
with open("training_ranges.json", "r") as file:
    training_ranges = json.load(file)

# Machine inputs 
machine_type = st.selectbox( 
    "Machine Type", 
    ["L", "M", "H"] 
) 

air_temperature = st.number_input( 
    "Air Temperature [K]", 
    min_value=float(training_ranges["Air temperature [K]"]["min"]),
    max_value=float(training_ranges["Air temperature [K]"]["max"]),
    value=300.0 
) 

process_temperature = st.number_input( 
    "Process Temperature [K]", 
    min_value=float(training_ranges["Process temperature [K]"]["min"]),
    max_value=float(training_ranges["Process temperature [K]"]["max"]),
    value=310.0 
) 

rotational_speed = st.number_input( 
    "Rotational Speed [rpm]", 
    min_value=float(training_ranges["Rotational speed [rpm]"]["min"]),
    max_value=float(training_ranges["Rotational speed [rpm]"]["max"]),
    value=1500.0 
) 

torque = st.number_input( 
    "Torque [Nm]", 
    min_value=float(training_ranges["Torque [Nm]"]["min"]),
    max_value=float(training_ranges["Torque [Nm]"]["max"]),
    value=40.0 
) 

tool_wear = st.number_input( 
    "Tool Wear [min]", 
    min_value=float(training_ranges["Tool wear [min]"]["min"]),
    max_value=float(training_ranges["Tool wear [min]"]["max"]),
    value=100.0 
) 

# Prediction 
warnings = []

if st.button("Predict Machine Failure"): 

    # check if inputs are within training ranges
    if not (
        training_ranges["Air temperature [K]"]["min"] 
        <= air_temperature 
        <= training_ranges["Air temperature [K]"]["max"]):

        warnings.append(
            f"Air Temperature must be between" 
            f"{training_ranges['Air temperature [K]']['min']} K and"  
            f"{training_ranges['Air temperature [K]']['max']} K."
        )

    if not (
        training_ranges["Process temperature [K]"]["min"] 
        <= process_temperature 
        <= training_ranges["Process temperature [K]"]["max"]):
    
        warnings.append(
            f"Process Temperature must be between" 
            f"{training_ranges['Process temperature [K]']['min']} K and"  
            f"{training_ranges['Process temperature [K]']['max']} K."
       )

    if not (
            training_ranges["Rotational speed [rpm]"]["min"] 
            <= rotational_speed 
            <= training_ranges["Rotational speed [rpm]"]["max"]):
        
            warnings.append(
                f"Rotational Speed must be between" 
                f"{training_ranges['Rotational speed [rpm]']['min']} rpm and"  
                f"{training_ranges['Rotational speed [rpm]']['max']} rpm."
           )

    if not (
            training_ranges["Torque [Nm]"]["min"] 
            <= torque 
            <= training_ranges["Torque [Nm]"]["max"]):
        
            warnings.append(
                f"Torque must be between" 
                f"{training_ranges['Torque [Nm]']['min']} Nm and"  
                f"{training_ranges['Torque [Nm]']['max']} Nm."
          )

    if not (
            training_ranges["Tool wear [min]"]["min"] 
            <= tool_wear 
            <= training_ranges["Tool wear [min]"]["max"]):
        
            warnings.append(
                f"Tool Wear must be between" 
                f"{training_ranges['Tool wear [min]']['min']} min and"  
                f"{training_ranges['Tool wear [min]']['max']} min."
           )

    # Display warnings and stop prediction
    if warnings:
        st.warning("⚠️ Some input values are outside the model's training range:")

        
        for warning in warnings:
            st.warning(warning)

        st.info(
            "Please adjust the input values to fall within the training ranges "
            "before making a prediction."
        )

    else:


        # Create input dataframe
        input_data = pd.DataFrame({ 
        "Type": [machine_type], 
        "Air temperature [K]": [air_temperature], 
        "Process temperature [K]": [process_temperature], 
        "Rotational speed [rpm]": [rotational_speed], 
        "Torque [Nm]": [torque], 
        "Tool wear [min]": [tool_wear] 
         }) 

        # predict probability of failure
        failure_probability = model.predict_proba(input_data)[0][1]
        failure_percentage = failure_probability * 100 

        # Apply final threshold 
        prediction = int(failure_probability >= final_threshold) 

        # Display probability 
        st.write( 
            f"Estimated Failure Probability: " 
            f"{failure_percentage:.2f}%" 
        ) 
        # Display result 
        if prediction == 1: 
            st.error("Machine Failure Risk Detected") 
        else: 
            st.success("No Machine Failure Risk Detected") 

        st.write(f"Decision Threshold: {final_threshold:.2f}")