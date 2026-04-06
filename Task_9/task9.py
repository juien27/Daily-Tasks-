import time
import re
import logging
import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


logging.basicConfig(
    filename="performance.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


class InputValidator:
    def validate(self, query: str):
        if len(query) > 300:
            raise ValueError("Query too long (Max 300 characters allowed).")

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if re.match(r'^[^a-zA-Z0-9]+$', query):
            raise ValueError("Query contains only special characters.")

        return True


class RAGPipeline:
    def __init__(self):
        print("🧠 Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.validator = InputValidator()
        self.memory = []  # Dynamic memory (no file, no static data)

        print("🤖 Loading Gemini model...")
        self.llm = genai.GenerativeModel("gemini-2.5-flash")

    def retrieve(self, query, top_k=3):
        start_time = time.time()

        if not self.memory:
            return [], 0

        query_embedding = self.model.encode([query])
        memory_embeddings = self.model.encode(self.memory)

        scores = cosine_similarity(query_embedding, memory_embeddings)[0]
        top_indices = np.argsort(scores)[-top_k:][::-1]

        contexts = [self.memory[i] for i in top_indices]

        retrieval_time = (time.time() - start_time) * 1000
        return contexts, retrieval_time

    
    def generate(self, contexts, query):
        start_time = time.time()

        try:
            context_text = "\n".join(contexts) if contexts else "No prior context."

            prompt = f"""
You are a helpful AI assistant.

Context (if useful):
{context_text}

User Question:
{query}

Instructions:
- Use context if relevant
- Otherwise answer using your own knowledge
- Give clear, accurate, and complete answer
"""

            response = self.llm.generate_content(prompt)

            generation_time = (time.time() - start_time) * 1000
            return response.text, generation_time

        except Exception as e:
            return f"API Error: {str(e)}", 0

    def run(self, query):
        try:
            # Step 1: Validate
            self.validator.validate(query)

            # Step 2: Retrieve
            contexts, retrieval_time = self.retrieve(query)

            # Step 3: Generate
            answer, generation_time = self.generate(contexts, query)

            # Step 4: Store memory
            self.memory.append(query)
            self.memory.append(answer)

            # Step 5: Log
            logging.info(
                f"retrieval_time_ms={retrieval_time:.2f}, generation_time_ms={generation_time:.2f}"
            )

            return answer

        except ValueError as ve:
            return f"Input Error: {str(ve)}"

        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    rag = RAGPipeline()

    while True:
        query = input("\n💬 Ask your question (type 'exit' to quit): ")

        if query.lower() == "exit":
            print("👋 Exiting...")
            break

        response = rag.run(query)
        print("\n🤖 Response:\n", response)