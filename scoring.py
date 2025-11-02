import pandas as pd

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def answer_similarity(student_answer, correct_answer):
    student_embedding = model.encode(student_answer, convert_to_tensor=True)
    correct_embedding = model.encode(correct_answer, convert_to_tensor=True)
    
    similarity = util.pytorch_cos_sim(student_embedding, correct_embedding)
    return similarity.item()

def scroering(similarity):
    if similarity >= 0.85:
        return 1
    elif similarity >= 0.75:
        return 0.5
    else:
        return 0

def need_review(similarity):
    return similarity < 0.85

