import streamlit as st

def apply_custom_style():
    """Applies custom CSS for a modern look."""
    st.markdown("""
        <style>
        .main { background-color: #f5f7f9; }
        [data-testid="stMetricValue"] { font-size: 2rem; color: #007BFF; }
        .prediction-card {
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #007BFF;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    st.title('🛡️ Customer Churn Analytics')
    st.markdown("Predict the likelihood of customer attrition using our Deep Learning model.")
    st.divider()

def get_user_inputs(geo_options, gender_options):
    """Renders the input grid and returns the data as a dictionary."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Demographics")
        geography = st.selectbox('Geography', geo_options)
        gender = st.radio('Gender', gender_options, horizontal=True)
        age = st.slider('Age', 18, 92, 35)

    with col2:
        st.subheader("💰 Financials")
        balance = st.number_input('Account Balance ($)', min_value=0.0, value=10000.0)
        salary = st.number_input('Estimated Salary ($)', min_value=0.0, value=50000.0)
        credit = st.number_input('Credit Score',value=500)

    with col3:
        st.subheader("📊 Engagement")
        tenure = st.slider('Tenure (Years)', 0, 10, 5)
        products = st.select_slider('Products', options=[1, 2, 3, 4])
        has_card = st.checkbox('Has Credit Card', value=False)
        is_active = st.checkbox('Is Active Member', value=False)
        
    return {
        'geography': geography, 'gender': gender, 'age': age,
        'balance': balance, 'salary': salary, 'credit': credit,
        'tenure': tenure, 'products': products, 
        'has_card': has_card, 'is_active': is_active
    }