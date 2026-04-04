from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from huggingface_hub import login
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

if hf_token:
    login(token=hf_token)


def load_corpus(file_name: str) -> list:
    corpus_path = Path(__file__).resolve().parent / file_name
    if not corpus_path.exists():
        raise FileNotFoundError(f"{file_name} not found!")

    with corpus_path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def load_model(model_name="all-MiniLM-L6-v2"):
    print("Loading embedding model...")
    return SentenceTransformer(model_name)

def create_embeddings(model, sentences: list):
    print("Generating embeddings...")
    return model.encode(sentences, show_progress_bar=True)


def semantic_search(query, model, corpus, corpus_embeddings, top_k=3, threshold=0.5):
    query_embedding = model.encode([query])

    similarities = cosine_similarity(query_embedding, corpus_embeddings)[0]

    # Get top results
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []

    for idx in top_indices:
        score = similarities[idx]
        if score >= threshold:
            results.append({
                "text": corpus[idx],
                "score": round(float(score), 3)
            })

    return results


def main():
    # Load data
    corpus = load_corpus("corpus.txt")

    # Load model
    model = load_model()

    # Create embeddings
    corpus_embeddings = create_embeddings(model, corpus)

    print("\n Semantic Search Ready!\n")

    while True:
        query = input(" Enter query (or type 'exit'): ").strip()

        if query.lower() == "exit":
            print(" Exiting...")
            break

        if not query:
            print(" Please enter a valid query.\n")
            continue

        results = semantic_search(
            query=query,
            model=model,
            corpus=corpus,
            corpus_embeddings=corpus_embeddings,
            top_k=3,
            threshold=0.5
        )

        print("\n Top Results:\n")

        if not results:
            print(" No relevant results found.\n")
        else:
            for res in results:
                print(f"Score: {res['score']}")
                print(res["text"])
                print("----------------------")

if __name__ == "__main__":
    main()