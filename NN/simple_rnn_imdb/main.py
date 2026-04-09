'''
This is Simple UI.

# Step 1: Import Libraries and Load the Model
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import load_model

# Load the IMDB dataset word index
word_index = imdb.get_word_index()
reverse_word_index = {value: key for key, value in word_index.items()}

# Load the pre-trained model with ReLU activation
model = load_model('simple_rnn_imdb.keras')

# Step 2: Helper Functions
# Function to decode reviews
def decode_review(encoded_review):
    return ' '.join([reverse_word_index.get(i - 3, '?') for i in encoded_review])

# Function to preprocess user input
def preprocess_text(text):
    words = text.lower().split()
    encoded_review = [word_index.get(word, 2) + 3 for word in words]
    padded_review = sequence.pad_sequences([encoded_review], maxlen=500)
    return padded_review


import streamlit as st
## streamlit app
# Streamlit app
st.title('IMDB Movie Review Sentiment Analysis')
st.write('Enter a movie review to classify it as positive or negative.')

# User input
user_input = st.text_area('Movie Review')

if st.button('Classify'):

    preprocessed_input=preprocess_text(user_input)

    ## MAke prediction
    prediction=model.predict(preprocessed_input)
    sentiment='Positive' if prediction[0][0] > 0.5 else 'Negative'

    # Display the result
    st.write(f'Sentiment: {sentiment}')
    st.write(f'Prediction Score: {prediction[0][0]}')
else:
    st.write('Please enter a movie review.')
'''
# Enhanced UI

import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import load_model
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Sentiment AI",
    page_icon="🎬",
    layout="centered"
)

# --- Custom CSS for Beauty ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .stTextArea textarea {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Model Loading (Cached for Performance) ---
@st.cache_resource
def load_my_model():
    # Load the IMDB dataset word index
    word_index = imdb.get_word_index()
    # Load the pre-trained model
    model = load_model('simple_rnn_imdb.keras')
    return word_index, model

word_index, model = load_my_model()
reverse_word_index = {value: key for key, value in word_index.items()}

# --- Helper Functions ---
def preprocess_text(text):
    words = text.lower().split()
    encoded_review = [word_index.get(word, 2) + 3 for word in words]
    padded_review = sequence.pad_sequences([encoded_review], maxlen=500)
    return padded_review

# --- Main UI ---
st.title('🎬 Movie Review Sentiment Analysis')
st.markdown("---")
st.write('**Analyze your movie reviews instantly.** Type a review below and our AI will determine the sentiment.')

# User input
user_input = st.text_area('Movie Review', placeholder='The cinematography was stunning, but the plot was a bit slow...', height=150)

# Layout columns for the button
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    submit_button = st.button('Analyze Sentiment')

if submit_button:
    if user_input.strip() == "":
        st.warning("Please enter some text before analyzing.")
    else:
        with st.spinner('🤖 AI is thinking...'):
            # Preprocess and Predict
            preprocessed_input = preprocess_text(user_input)
            prediction = model.predict(preprocessed_input)
            score = prediction[0][0]
            sentiment = 'Positive' if score > 0.5 else 'Negative'

        # Result Display
        st.markdown("### Analysis Result")
        
        # Color coding based on sentiment
        if sentiment == 'Positive':
            st.success(f"### This is a **{sentiment}** review!")
        else:
            st.error(f"### This is a **{sentiment}** review.")

        # Progress bar for the score
        st.write(f"**Confidence Score:** {score:.2f}")
        st.progress(float(score))
        
        with st.expander("See Prediction Details"):
            st.write(f"The model outputted a raw value of {score:.4f}.")
            st.write("Values closer to 1.0 are Positive; values closer to 0.0 are Negative.")

else:
    st.info('Waiting for input... Fill out the box above and click "Analyze Sentiment".')
