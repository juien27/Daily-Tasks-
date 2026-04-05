import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from dotenv import load_dotenv

load_dotenv()

def load_document(file_name):
    base_path = Path(__file__).resolve().parent
    file_path = base_path / file_name

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()

def split_text(text, chunk_size=100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

def create_embeddings(chunks):
    model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2")
    embeddings = model.encode(chunks)
    return embeddings, model


def search(query, chunks, embeddings, model, top_k=3):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    top_indices = similarities.argsort()[-top_k:][::-1]
    results = [chunks[i] for i in top_indices]

    return results


def generate_answer(context, query):

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    Answer the question based only on the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

if __name__ == "__main__":
    print("🔄 Loading document...")

    document = load_document("document.txt")

    print("✂️ Splitting text...")
    chunks = split_text(document)

    print("🧠 Creating embeddings...")
    embeddings, model = create_embeddings(chunks)

    print("✅ System Ready!\n")

    while True:
        query = input("💬 Ask a question (or type 'exit'): ")

        if query.lower() == "exit":
            break

        results = search(query, chunks, embeddings, model)

        context = "\n".join(results)

        answer = generate_answer(context, query)

        print("\n🤖 Answer:\n", answer)
        print("\n" + "-"*50 + "\n")