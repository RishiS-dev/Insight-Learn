import re
from collections import Counter

STOPWORDS = {
    "the","a","an","and","or","but","if","then","else","when","of","at","by","for","with",
    "about","against","between","into","through","during","before","after","above","below",
    "to","from","up","down","in","out","on","off","over","under","again","further","once",
    "here","there","all","any","both","each","few","more","most","other","some","such","no",
    "nor","not","only","own","same","so","than","too","very","can","will","just","don","should"
}

def extract_keywords(text: str, top_k: int = 8, min_len: int = 3):
    if not text:
        return []
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]+", text.lower())
    tokens = [t for t in tokens if len(t) >= min_len and t not in STOPWORDS]
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_k)]