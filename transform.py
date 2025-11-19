import pandas as pd
import sys

def transform_quiz_to_answer_format(input_file, output_file='answer.csv'):
    """
    Transform a simple quiz CSV to the answer.csv format.
    
    Expected input format options:
    1. Wide format: studentID, Q1, Q2, Q3, ...
    2. Already in correct format: studentID, questionID, studentAnswer
    
    Output format: studentID, questionID, studentAnswer
    """
    try:
        # Read the input file
        df = pd.read_csv(input_file, skipinitialspace=True)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"Input columns: {list(df.columns)}")
        print(f"Input shape: {df.shape}")
        
        # Check if already in correct format
        if set(['studentID', 'questionID', 'studentAnswer']).issubset(df.columns):
            print("✓ File is already in correct format!")
            df_output = df[['studentID', 'questionID', 'studentAnswer']]
        
        # Check if in wide format (studentID + question columns)
        elif 'studentID' in df.columns:
            print("Converting from wide format to long format...")
            
            # Get question columns (all columns except studentID)
            question_cols = [col for col in df.columns if col != 'studentID']
            
            # Melt the dataframe
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
            
            print(f"✓ Converted {len(df)} students with {len(question_cols)} questions each")
        
        else:
            print("❌ Error: Could not identify format. Expected 'studentID' column.")
            print("Supported formats:")
            print("1. Wide: studentID, Q1, Q2, Q3, ...")
            print("2. Long: studentID, questionID, studentAnswer")
            return None
        
        # Save to output file
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