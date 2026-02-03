import re

def extract_average_score(report):
    scores = re.findall(r'(\d(?:\.\d)?)/5', report)
    scores = [float(s) for s in scores]
    return sum(scores) / len(scores) if scores else 0
