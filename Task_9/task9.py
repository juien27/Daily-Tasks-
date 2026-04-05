import time
import re
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

logging.basicConfig(
    filename="performance.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

class InputValidator:
    def validate(self, query: str):
        # Rule 1: Length check
        if len(query) > 300:
            raise ValueError("Query too long (Max 300 characters allowed).")

        # Rule 2: Empty or special characters only
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if re.match(r'^[^a-zA-Z0-9]+$', query):
            raise ValueError("Query contains only special characters.")

        return True


def load_corpus(file_name="corpus.txt"):
    path = Path(file_name)
    if not path.exists():
        raise FileNotFoundError("Corpus file not found!")

    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

def split_chunks(text, chunk_size=300):
    chunks = []
    for line in text:
        for i in range(0, len(line), chunk_size):
            chunks.append(line[i:i+chunk_size])
    return chunks


class RAGPipeline:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.validator = InputValidator()

        print("🔄 Loading corpus...")
        corpus = load_corpus()

        print("✂️ Splitting chunks...")
        self.chunks = split_chunks(corpus)

        print("🧠 Creating embeddings...")
        self.embeddings = self.model.encode(self.chunks)

    def retrieve(self, query):
        start_time = time.time()

        query_embedding = self.model.encode([query])
        scores = cosine_similarity(query_embedding, self.embeddings)[0]
        best_idx = scores.argmax()

        retrieval_time = (time.time() - start_time) * 1000  # ms

        return self.chunks[best_idx], retrieval_time

  
    def generate(self, context, query):
        start_time = time.time()

        try:
            # Simulated LLM response
            response = f"Answer based on context:\n{context}"

            generation_time = (time.time() - start_time) * 1000

            return response, generation_time

        except Exception:
            return "Service temporarily unavailable. Please try again in 30 seconds.", 0

    def run(self, query):
        try:
            # Step 1: Validate Input
            self.validator.validate(query)

            # Step 2: Retrieve
            context, retrieval_time = self.retrieve(query)

            # Step 3: Generate
            answer, generation_time = self.generate(context, query)

            # Step 4: Log Performance
            logging.info(
                f"retrieval_time_ms={retrieval_time:.2f}, generation_time_ms={generation_time:.2f}"
            )

            return answer

        except ValueError as ve:
            return f"Input Error: {str(ve)}"

        except Exception:
            return "Service temporarily unavailable. Please try again in 30 seconds."

if __name__ == "__main__":
    rag = RAGPipeline()

    while True:
        query = input("\n💬 Ask your question (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        response = rag.run(query)
        print("\n🤖 Response:\n", response)