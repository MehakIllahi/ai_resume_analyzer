import re

def extract_scores(text):
    pattern = r'(\d+(?:\.\d+)?)/5'
    matches = re.findall(pattern, text)
    scores = [float(match) for match in matches]
    return scores

def extract_average_score(report):
    scores = re.findall(r'(\d+(?:\.\d+)?)/5', report)
    if not scores:
        return 0
    scores = [float(s) for s in scores]
    return sum(scores) / (5 * len(scores))
