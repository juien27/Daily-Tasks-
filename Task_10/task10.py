from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader

print("🚀 Loading model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("✅ Model loaded")


# 🔷 Step 1: Read PDF
def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "

    return text


# 🔷 Step 2: Chunk text (600)
def chunk_text(text, chunk_size=600):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks


# 🔷 Step 3: Get best chunk (same output style)
def get_best_answer(query, chunks):
    query_embedding = model.encode([query])
    chunk_embeddings = model.encode(chunks)

    scores = cosine_similarity(query_embedding, chunk_embeddings)[0]

    best_index = scores.argmax()

    return chunks[best_index]


# 🔥 MAIN
if __name__ == "__main__":
    print("🔥 PDF RAG (SAME OUTPUT) STARTED")

    pdf_path = "document.pdf"   

    text = load_pdf(pdf_path)

    chunks = chunk_text(text, chunk_size=600)

    print(f"📦 Total Chunks: {len(chunks)}")

    while True:
        print("\n---------------------------")
        query = input("👉 Ask question (type 'exit'): ").strip()

        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting...")
            break

        if query == "":
            print("⚠️ Enter a question")
            continue

        answer = get_best_answer(query, chunks)

        print("\n✅ Answer:", answer)