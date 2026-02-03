from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def calculate_similarity(resume, jd):
    embeddings = model.encode([resume, jd])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
