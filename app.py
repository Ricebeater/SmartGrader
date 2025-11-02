import streamlit as st
import pandas as pd
import numpy as np
import runpy
from pathlib import Path
from export import export_to_excel

export_to_excel()

student_answer = st.file_uploader(
    "Upload your respond", type=["csv"]
    )

key_answer = st.file_uploader(
    "Upload your key", type=["csv"]
    )


df = pd.read_excel("graded_result.xlsx")

config = {
    "similarity": st.column_config.ProgressColumn()
}

st.set_page_config(page_title="SmartCheck Grading System", layout="wide")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("📋 SmartCheck Grading System 📋")
    st.write("Upload student answers and answer key to grade responses.")

st.dataframe(df, width="stretch", height=400, column_config=config)