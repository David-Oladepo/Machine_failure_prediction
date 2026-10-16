from pathlib import Path
import json

import joblib
import pandas as pd
import streamlit as st

# --------------------------------------------------

# Page configuration

# --------------------------------------------------

st.set_page_config(
page_title="Predictive Maintenance | AI Analytics",
page_icon="⚙️",
layout="wide",
initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------

# Load model and configuration files

# --------------------------------------------------

@st.cache_resource
def load_model():
    return joblib.load(BASE_DIR / "machine_failure_model.pkl")

@st.cache_data
def load_json(filename):
    with open(BASE_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)

try:
    model = load_model()
    threshold_data = load_json("final_threshold.json")
    training_ranges = load_json("training_ranges.json")
    final_threshold = float(threshold_data["final_threshold"])


    if not 0 <= final_threshold <= 1:
        raise ValueError("The decision threshold must be between 0 and 1.")


except (OSError, ValueError, KeyError, TypeError) as error:
    st.error(
        "The application could not load its model or configuration files. "
        "Check that the required files are present and correctly formatted."
    )
    st.exception(error)
    st.stop()

# --------------------------------------------------

# Header

# --------------------------------------------------

st.title("⚙️ Predictive Maintenance")
st.subheader("Machine Failure Prediction Using Machine Learning")

st.markdown(
"""
Estimate machine-failure probability from operating conditions using a
trained machine-learning model. Explore different sensor inputs and
review the resulting risk classification.
"""
)

st.caption(
"Portfolio project • Random Forest classifier • "
f"Decision threshold: {final_threshold:.2f}"
)

st.divider()

# --------------------------------------------------

# Sidebar: context and guidance

# --------------------------------------------------

with st.sidebar:
    st.header("About this application")

    st.write(
        "This application demonstrates how machine-learning predictions "
        "can support industrial maintenance planning."
    )

    st.markdown("**Input features**")
    st.markdown(
        """
        - Machine type
        - Air temperature
        - Process temperature
        - Rotational speed
        - Torque
        - Tool wear
        """
    )

    st.info(
        "Predictions are estimates from a model trained on a synthetic "
        "dataset. They are not guarantees of future machine performance."
    )


# --------------------------------------------------

# Input form

# --------------------------------------------------

st.header("Machine operating conditions")
st.write("Enter the operating measurements, then run the prediction.")

with st.form("prediction_form"):
    machine_type = st.selectbox(
        "Machine type",
        options=["L", "M", "H"],
        help="Select the machine product-quality type used by the model.",
    )


    col1, col2 = st.columns(2)

    with col1:
        air_temperature = st.number_input(
            "Air temperature (K)",
            min_value=float(training_ranges["Air temperature [K]"]["min"]),
            max_value=float(training_ranges["Air temperature [K]"]["max"]),
            value=300.0,
            step=0.1,
        )

        rotational_speed = st.number_input(
            "Rotational speed (rpm)",
            min_value=float(training_ranges["Rotational speed [rpm]"]["min"]),
            max_value=float(training_ranges["Rotational speed [rpm]"]["max"]),
            value=1500.0,
            step=1.0,
        )

        tool_wear = st.number_input(
            "Tool wear (min)",
            min_value=float(training_ranges["Tool wear [min]"]["min"]),
            max_value=float(training_ranges["Tool wear [min]"]["max"]),
            value=100.0,
            step=1.0,
        )

    with col2:
        process_temperature = st.number_input(
            "Process temperature (K)",
            min_value=float(training_ranges["Process temperature [K]"]["min"]),
            max_value=float(training_ranges["Process temperature [K]"]["max"]),
            value=310.0,
            step=0.1,
        )

        torque = st.number_input(
            "Torque (Nm)",
            min_value=float(training_ranges["Torque [Nm]"]["min"]),
            max_value=float(training_ranges["Torque [Nm]"]["max"]),
            value=40.0,
            step=0.1,
        )

    submitted = st.form_submit_button(
        "Estimate machine-failure risk",
        type="primary",
        use_container_width=True,
    )

# --------------------------------------------------
# Validate inputs and generate prediction
# --------------------------------------------------
if submitted:
    input_data = pd.DataFrame(
        {
            "Type": [machine_type],
            "Air temperature [K]": [air_temperature],
            "Process temperature [K]": [process_temperature],
            "Rotational speed [rpm]": [rotational_speed],
            "Torque [Nm]": [torque],
            "Tool wear [min]": [tool_wear],
        }
    )

    if process_temperature <= air_temperature:
        st.error(
            "Please check the temperatures: process temperature should "
            "be higher than air temperature for this application."
        )
    else:
        try:
            failure_probability = float(
                model.predict_proba(input_data)[0][1]
            )

            if not 0 <= failure_probability <= 1:
                raise ValueError("The model returned an invalid probability.")

            failure_percentage = failure_probability * 100
            prediction = failure_probability >= final_threshold

            st.divider()
            st.header("Prediction results")

            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:
                st.metric(
                    "Estimated failure probability",
                    f"{failure_percentage:.2f}%",
                )

            with metric_col2:
                st.metric(
                    "Decision threshold",
                    f"{final_threshold:.0%}",
                )

            st.progress(failure_probability)

            if prediction:
                st.error(
                    "**Elevated predicted failure risk**\n\n"
                    "The estimated probability meets or exceeds the "
                    "configured decision threshold. Consider reviewing "
                    "the operating conditions and following appropriate "
                    "maintenance procedures."
                )
            else:
                st.success(
                    "**Below the configured risk threshold**\n\n"
                    "The estimated probability is below the configured "
                    "decision threshold. This does not guarantee that "
                    "the machine is free from faults."
                )

            with st.expander("Review submitted operating conditions"):
                st.dataframe(input_data, use_container_width=True)

            st.caption(
                "Interpretation: this classification is based on the "
                "model's estimated probability and the selected threshold. "
                "It is a decision-support output, not a safety certification."
            )

        except (ValueError, TypeError, IndexError) as error:
            st.error(
                "The model could not produce a valid prediction for these "
                "inputs. Please review the values and try again."
            )
            st.exception(error)

# --------------------------------------------------

st.divider()
st.caption(
"Built by David Oladepo | Machine Learning • Data Science • "
"Digital Analytics & AI"
)
