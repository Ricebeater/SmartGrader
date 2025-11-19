import pandas as pd
import sys
import streamlit as st

def transform_quiz_to_answer_format(input_file, output_file=None):
    """
    Transform a quiz file to the answer.csv format.
    
    Supports:
    1. Google Forms format: Timestamp, Student ID, question columns
    2. Wide format: studentID, Q1, Q2, Q3, ...
    3. Long format: studentID, questionID, studentAnswer (no transformation needed)
    
    Args:
        input_file: File path (string) or file-like object from Streamlit
        output_file: Output file path (optional, only used in CLI mode)
    
    Returns:
        DataFrame in format: studentID, questionID, studentAnswer
    """
    try:
        # Read the input file
        if isinstance(input_file, str):
            # File path provided (CLI mode)
            df = pd.read_csv(input_file, skipinitialspace=True)
        else:
            # File-like object from Streamlit
            if hasattr(input_file, 'name') and input_file.name.endswith('.xlsx'):
                df = pd.read_excel(input_file)
            else:
                df = pd.read_csv(input_file, skipinitialspace=True)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"Input columns: {list(df.columns)}")
        print(f"Input shape: {df.shape}")
        
        # Check if already in correct format
        required_cols = {'studentID', 'questionID', 'studentAnswer'}
        if required_cols.issubset(df.columns):
            print("✓ File is already in correct format!")
            df_output = df[['studentID', 'questionID', 'studentAnswer']]
        
        # Check for Google Forms format (has a student identifier column)
        else:
            student_id_col = None
            
            # Look for student ID column (case-insensitive)
            for col in df.columns:
                if 'student' in col.lower() and 'id' in col.lower():
                    student_id_col = col
                    break
            
            if student_id_col:
                print(f"✓ Detected Google Forms format with column: '{student_id_col}'")
                
                # Identify metadata columns to exclude
                exclude_cols = [student_id_col]
                for col in df.columns:
                    col_lower = col.lower()
                    if any(x in col_lower for x in ['timestamp', 'score', 'email', 'username', 'name']):
                        exclude_cols.append(col)
                        print(f"  Excluding metadata: {col}")
                
                # Get question columns
                question_cols = [col for col in df.columns if col not in exclude_cols]
                
                if len(question_cols) == 0:
                    print("❌ No question columns found")
                    return None
                
                print(f"✓ Found {len(question_cols)} question columns")
                
                # Create question ID mapping (Q1, Q2, Q3, etc.)
                question_mapping = {col: f"Q{i+1}" for i, col in enumerate(question_cols)}
                
                # Show mapping
                print("\nQuestion Mapping:")
                for orig, qid in question_mapping.items():
                    print(f"  {qid} ← {orig}")
                
                # Transform to long format
                df_output = pd.melt(
                    df,
                    id_vars=[student_id_col],
                    value_vars=question_cols,
                    var_name='questionID',
                    value_name='studentAnswer'
                )
                
                # Rename student ID column
                df_output = df_output.rename(columns={student_id_col: 'studentID'})
                
                # Map question text to Q1, Q2, Q3
                df_output['questionID'] = df_output['questionID'].map(question_mapping)
                
                # Remove rows with missing or empty answers
                df_output = df_output.dropna(subset=['studentAnswer'])
                df_output = df_output[df_output['studentAnswer'].astype(str).str.strip() != '']
                
                # Sort by studentID and questionID
                df_output = df_output.sort_values(['studentID', 'questionID']).reset_index(drop=True)
                
                print(f"✓ Transformed: {len(df)} students × {len(question_cols)} questions = {len(df_output)} answers")
            
            # Check if in simple wide format (studentID + Q1, Q2, Q3...)
            elif 'studentID' in df.columns:
                print("✓ Converting from wide format to long format...")
                
                # Get question columns
                question_cols = [col for col in df.columns if col != 'studentID']
                
                # Transform to long format
                df_output = pd.melt(
                    df,
                    id_vars=['studentID'],
                    value_vars=question_cols,
                    var_name='questionID',
                    value_name='studentAnswer'
                )
                
                # Remove rows with missing answers
                df_output = df_output.dropna(subset=['studentAnswer'])
                
                # Sort by studentID and questionID
                df_output = df_output.sort_values(['studentID', 'questionID']).reset_index(drop=True)
                
                print(f"✓ Transformed: {len(df)} students × {len(question_cols)} questions = {len(df_output)} answers")
            
            else:
                print("❌ Error: Could not identify format")
                print("Expected one of:")
                print("1. Google Forms: Timestamp, Student ID, Question1, Question2, ...")
                print("2. Wide format: studentID, Q1, Q2, Q3, ...")
                print("3. Long format: studentID, questionID, studentAnswer")
                print(f"\nFound columns: {list(df.columns)}")
                return None
        
        # Save to output file if specified (CLI mode)
        if output_file:
            df_output.to_csv(output_file, index=False)
            print(f"✓ Saved to {output_file}")
        
        print(f"Output shape: {df_output.shape}")
        print("\nFirst few rows:")
        print(df_output.head(10))
        
        return df_output
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def create_sample_quiz():
    """Create a sample quiz file for testing"""
    sample_data = {
        'studentID': ['001', '002', '003'],
        'Q1': [
            'Bangkok is the capital city of Thailand.',
            'Bangkok',
            'Samut Prakan is near Bangkok.'
        ],
        'Q2': [
            "Brain's main control center.",
            "main control center of the brain.",
            "control center."
        ],
        'Q3': [
            'Water boils at 100 C.',
            '100 degrees Celsius is the boiling point of water.',
            'The boiling point of water is 100 degrees Celsius.'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('simple_quiz.csv', index=False)
    print("✓ Created sample file: simple_quiz.csv")
    return df


if __name__ == "__main__":
    # Check if input file is provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'answer.csv'
        transform_quiz_to_answer_format(input_file, output_file)
    else:
        print("Usage: python transform.py <input_file> [output_file]")
        print("\nExample:")
        print("  python transform.py simple_quiz.csv answer.csv")
        print("\nCreating sample file for demonstration...")
        create_sample_quiz()
        print("\nNow transforming sample file...")
        transform_quiz_to_answer_format('simple_quiz.csv', 'answer_output.csv')
