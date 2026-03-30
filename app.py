import streamlit as st
import numpy as np
import pandas as pd

st.title("Hello")

st.write("This is Simple text")

df = pd.DataFrame({
    'first column':[1,2,3,4],
    'second column' : [5,6,7,8]
})

st.write(df)

chart_data = pd.DataFrame(
    np.random.rand(20,3),columns=['a','b','c']
)
st.line_chart(chart_data)