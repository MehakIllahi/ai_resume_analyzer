from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity_bert(text1, text2):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings1 = model.encode([text1])
    embeddings2 = model.encode([text2])
    similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
    return similarity
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
def calculate_similarity(resume, jd):
    emb1 = model.encode([resume])
    emb2 = model.encode([jd])
    return cosine_similarity(emb1, emb2)[0][0]
