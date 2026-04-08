import streamlit as st
import pandas as pd
import pickle
import tensorflow as tf
from ui_components import apply_custom_style, render_header, get_user_inputs

# Page Config
st.set_page_config(page_title="ChurnGuard AI", page_icon="📊", layout="wide")

# Load Assets
@st.cache_resource
def load_resources():
    model = tf.keras.models.load_model('model.h5')
    with open('label_encoder_gender.pkl', 'rb') as f: le_gender = pickle.load(f)
    with open('onehot_encoder_geo.pkl', 'rb') as f: ohe_geo = pickle.load(f)
    with open('scaler.pkl', 'rb') as f: sc = pickle.load(f)
    return model, le_gender, ohe_geo, sc

model, le_gender, ohe_geo, scaler = load_resources()

# Render UI
apply_custom_style()
render_header()
data = get_user_inputs(ohe_geo.categories_[0], le_gender.classes_)

# Prediction Logic
if st.button('Run Prediction Analysis', type='primary', use_container_width=True):
    # Prepare DataFrame
    input_df = pd.DataFrame({
        'CreditScore': [data['credit']],
        'Gender': [le_gender.transform([data['gender']])[0]],
        'Age': [data['age']],
        'Tenure': [data['tenure']],
        'Balance': [data['balance']],
        'NumOfProducts': [data['products']],
        'HasCrCard': [int(data['has_card'])],
        'IsActiveMember': [int(data['is_active'])],
        'EstimatedSalary': [data['salary']]
    })

    # Encoding & Scaling
    geo_enc = ohe_geo.transform([[data['geography']]]).toarray()
    geo_df = pd.DataFrame(geo_enc, columns=ohe_geo.get_feature_names_out(['Geography']))
    final_input = pd.concat([input_df.reset_index(drop=True), geo_df], axis=1)
    scaled_input = scaler.transform(final_input)

    # Predict
    prob = float(model.predict(scaled_input)[0][0])
    
    # Show Results
    st.divider()
    c1, c2 = st.columns([1, 2])
    c1.metric("Churn Risk", f"{prob:.1%}")
    
    if prob > 0.5:
        c2.error(f"### High Risk: Customer likely to churn.")
    else:
        c2.success(f"### Low Risk: Customer likely to stay.")
    st.progress(prob)