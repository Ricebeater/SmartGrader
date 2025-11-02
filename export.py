import pandas as pd

from scoring import answer_similarity, need_review, scroering

# Read CSV files and strip whitespace from column names
df_answer = pd.read_csv("answer.csv", skipinitialspace=True)
df_key = pd.read_csv("answer_key.csv", skipinitialspace=True)

# Clean column names by stripping whitespace
df_answer.columns = df_answer.columns.str.strip()
df_key.columns = df_key.columns.str.strip()

key_dict = dict(
    zip(
        df_key["questionID"],
        df_key["correctAnswer"]
        )
    )
results = []

for _, row in df_answer.iterrows():
    student_id = row["studentID"]
    question_id = row["questionID"]
    student_answer = row["studentAnswer"]
    correct_answer = key_dict.get(question_id, "")
    
    similarity = answer_similarity(student_answer, correct_answer)
    score = scroering(similarity)
    review = need_review(similarity)
    
    results.append
    (
        {
            "studentID": student_id,
            "questionID": question_id,
            "studentAnswer": student_answer,
            "correctAnswer": correct_answer,
            "similarity": round(similarity, 2),
            "score": score,
            "need_review": review
        }
    )

df_results = pd.DataFrame(results)
df_results.to_csv("results.csv", index=False)

def export_to_excel():
    df_results.to_excel("graded_result.xlsx", index=False)

export_to_excel()