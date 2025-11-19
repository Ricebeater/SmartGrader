import streamlit as st
import pandas as pd
import numpy as np
from export import load_data
from transform import transform_quiz_to_answer_format
from io import BytesIO

st.set_page_config(page_title="SmartCheck Grading System", layout="wide")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("📋 SmartCheck Grading System 📋")
    st.write("Upload student answers and answer key to grade responses.")

# Show format examples in expander
with st.expander("📖 View Supported Formats"):
    st.subheader("Student Answer Formats")
    
    tab1, tab2, tab3 = st.tabs(["Google Forms", "Wide Format", "Long Format"])
    
    with tab1:
        st.markdown("**Google Forms Export** *(auto-converts)*")
        st.code("""Timestamp,Score,Student ID,What is the capital...,What is the function...
11/19/2025 23:04:56,,001,Bangkok,Control center
11/19/2025 23:06:10,,002,Paris,Hypothalamus
""", language="csv")
        st.caption("System will automatically map questions to Q1, Q2, Q3...")
    
    with tab2:
        st.markdown("**Wide Format** *(auto-converts)*")
        st.code("""studentID, Q1, Q2, Q3
001, "Bangkok", "Control center", "100C"
002, "Paris", "Hypothalamus", "Boiling"
""", language="csv")
    
    with tab3:
        st.markdown("**Long Format** *(ready to use)*")
        st.code("""studentID, questionID, studentAnswer
001, Q1, "Bangkok"
001, Q2, "Control center"
002, Q1, "Paris"
""", language="csv")
    
    st.subheader("Answer Key Format")
    st.code("""questionID, correctAnswer
Q1, "Bangkok is the capital of Thailand."
Q2, "The hypothalamus acts as the brain's main control center."
Q3, "The boiling point of water is 100 degrees Celsius."
""", language="csv")
    st.caption("⚠️ Question IDs (Q1, Q2, Q3...) must match the order of questions in your student answer file")

# File uploaders
student_answer = st.file_uploader(
    "Upload Student Answers", 
    type=["csv", "xlsx"],
    help="Supports Google Forms export, wide format, or long format"
)

key_answer = st.file_uploader(
    "Upload Answer Key", 
    type=["csv", "xlsx"],
    help="Format: questionID, correctAnswer"
)

# Process files when both are uploaded
if student_answer is not None and key_answer is not None:
    st.divider()
    
    with st.spinner("🔄 Processing files..."):
        try:
            # Transform student answers using transform.py
            st.info("🔄 Transforming student answers...")
            transformed_df = transform_quiz_to_answer_format(student_answer)
            
            if transformed_df is not None:
                # Convert transformed dataframe to file-like object for export.py
                buffer = BytesIO()
                transformed_df.to_csv(buffer, index=False)
                buffer.seek(0)
                
                # Reset key answer file pointer
                key_answer.seek(0)
                
                # Process the data using export.py
                st.info("📊 Grading answers...")
                load_data(buffer, key_answer)
                
                # Read and display results
                df = pd.read_excel("graded_result.xlsx")
                
                st.success("✅ Grading completed!")
                
                # Show summary statistics
                st.subheader("📊 Summary Statistics")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Total Answers", len(df))
                with col_stat2:
                    unique_students = df['studentID'].nunique()
                    st.metric("Students", unique_students)
                with col_stat3:
                    avg_score = df['score'].mean()
                    st.metric("Avg Score", f"{avg_score:.2f}")
                with col_stat4:
                    needs_review = df['need_review'].sum()
                    st.metric("Needs Review", needs_review)
                
                # Display results table
                st.subheader("📋 Grading Results")
                config = {
                    "similarity": st.column_config.ProgressColumn(
                        "Similarity",
                        min_value=0,
                        max_value=1,
                        format="%.2f"
                    ),
                    "score": st.column_config.NumberColumn(
                        "Score",
                        format="%.1f"
                    ),
                    "need_review": st.column_config.CheckboxColumn(
                        "Needs Review"
                    )
                }
                st.dataframe(df, use_container_width=True, height=400, column_config=config)
                
                # Download buttons
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    # Excel download
                    buffer_excel = BytesIO()
                    df.to_excel(buffer_excel, index=False, engine='openpyxl')
                    buffer_excel.seek(0)
                    
                    st.download_button(
                        label="📥 Download Results (Excel)",
                        data=buffer_excel,
                        file_name='grading_results.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                
                with col_dl2:
                    # CSV download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name='grading_results.csv',
                        mime='text/csv'
                    )
            else:
                st.error("❌ Failed to transform file. Please check the format.")
                
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.write("**Troubleshooting:**")
            st.write("- Check that your answer key has columns: `questionID, correctAnswer`")
            st.write("- Ensure question IDs in the key match Q1, Q2, Q3...")
            
            with st.expander("🐛 View Error Details"):
                import traceback
                st.code(traceback.format_exc())