import string

# Stopwords list

STOPWORDS = {
    "the", "is", "at", "which", "on", "a", "an", "and", "or", "in", "to", "of",
    "for", "with", "as", "by", "that", "this", "it"
}
# Synonym dictionary (basic)

SYNONYMS = {
    "happy": ["joyful", "glad"],
    "ai": ["artificial", "intelligence"],
    "code": ["programming", "coding"],
    "data": ["information"]
}
# Preprocessing function

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()
    words = [word for word in words if word not in STOPWORDS]
    return set(words)

# Expand query with synonyms

def expand_query(tokens):
    expanded = set(tokens)
    for word in tokens:
        if word in SYNONYMS:
            expanded.update(SYNONYMS[word])
    return expanded

# Jaccard Similarity

def jaccard_similarity(set1, set2):
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0

# Load corpus

def load_corpus(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        sentences = file.readlines()
    return [sentence.strip() for sentence in sentences if sentence.strip()]



# Search function

def search(query, corpus):
    query_tokens = preprocess_text(query)
    query_tokens = expand_query(query_tokens)

    scores = []

    for sentence in corpus:
        sentence_tokens = preprocess_text(sentence)
        score = jaccard_similarity(query_tokens, sentence_tokens)
        scores.append((sentence, score))

    # Sort by score (descending)
    results = sorted(scores, key=lambda x: x[1], reverse=True)

    return results


# Main execution
if __name__ == "__main__":
    corpus = load_corpus("corpus.txt")

    query = input("Enter your search query: ")

    results = search(query, corpus)

    print("\nTop Results:\n")
    for sentence, score in results[:5]:
        print(f"[Score: {score:.2f}] {sentence}")