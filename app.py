import streamlit as st
import pandas as zai
import numpy as np
from export import load_data

st.set_page_config(page_title="SmartCheck Grading System", layout="wide")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("📋 SmartCheck Grading System 📋")
    st.write("Upload student answers and answer key to grade responses.")


student_answer = st.file_uploader(
    "Upload your respond", type=["csv", "xlsx"]
    )

key_answer = st.file_uploader(
    "Upload your key", type=["csv", "xlsx"]
    )

if student_answer is not None and key_answer is not None:
    load_data(student_answer, key_answer)
    df = zai.read_excel("graded_result.xlsx")
    config = {
        "similarity": st.column_config.ProgressColumn()
        }
    st.dataframe(df, width="stretch", height=400, column_config=config)

