import os
import re
import time
import cv2
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import numpy as np

# 🔑 Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Model
model = genai.GenerativeModel("gemini-flash-latest")

# 🔷 Logging setup
logging.basicConfig(
    filename="ai_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# 🔷 Parser
class QueryParser:
    def parse(self, query: str):
        query = query.strip().lower()

        if not query:
            return "INVALID"

        if all(not c.isalnum() for c in query):
            return "NOISE"

        if re.match(r"^\d+e\d+$", query):
            return "NOISE"

        if query.isnumeric():
            return "NOISE"

        keywords = [
            "image", "picture", "photo", "show", "see",
            "animal", "person", "object", "car", "dog", "cat",
            "what", "describe", "who", "where", "color", "happening"
        ]
        
        greetings = ["hi", "hello", "hey", "morning", "evening", "how are you", "help", "who are you", "exit", "quit"]

        if any(word in query for word in keywords):
            return "VALID"
            
        if any(word in query for word in greetings):
            return "GREETING"

        return "NON_IMAGE"

parser = QueryParser()

app = FastAPI()

# 🔷 CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔷 Safety
def safety_check(query):
    blocked = ["who is this person", "identify person"]
    return not any(b in query.lower() for b in blocked)

# 🔷 Blur Detection (Optimized for bytes)
def is_blurry(image_bytes, threshold=100):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        return variance < threshold
    except Exception as e:
        print(f"Error in blur detection: {e}")
        return False

# 🔷 Gemini
async def ask_gemini(question, images_data):
    images = []

    for img_data in images_data:
        images.append({
            "mime_type": "image/jpeg",
            "data": img_data
        })

    prompt = [
        "You are VisionAI, a helpful assistant. "
        "If images are provided, answer the user's question based on the images. "
        "If NO images are provided, reply to the user's greeting or conversation politely. "
        "If the user says 'exit' or 'quit', say goodbye and suggest they use the 'Reset' button to clear the session. "
        "If the question is completely unrelated to images AND not a greeting, say: 'Please upload an image or ask a vision-related question.'",
        f"User Question: {question}"
    ]

    response = model.generate_content(prompt + images)
    return response.text.strip()

# 🔷 Safety
def safety_check(query):
    blocked = ["who is this person", "identify person"]
    return not any(b in query.lower() for b in blocked)

@app.post("/ask")
async def ask_endpoint(
    question: str = Form(...),
    images: List[UploadFile] = File(default=[])
):
    # 🔷 Parse input
    result = parser.parse(question)

    if result == "INVALID":
        return {"answer": "❌ Empty question"}
    elif result == "NOISE":
        return {"answer": "❌ Noise detected (invalid input)"}
    elif result == "NON_IMAGE" and not images:
        return {"answer": "❌ Please upload an image or ask a vision-related question."}

    # 🔒 Safety
    if not safety_check(question):
        return {"answer": "❌ Safety check failed: Not allowed"}

    try:
        start = time.time()
        
        valid_images_data = []
        if images and len(images) > 0:
            for img in images:
                # Check if file is empty
                if img.size == 0: continue
                
                content = await img.read()
                if is_blurry(content):
                    logging.warning(f"Rejected blurry image: {img.filename}")
                    return {
                        "answer": f"❌ The image '{img.filename}' appears to be blurry. Please provide a clearer image for accurate analysis.",
                        "status": "error"
                    }
                valid_images_data.append(content)

        # Gemini handles both images and chat automatically
        answer = await ask_gemini(question, valid_images_data)
        
        end = time.time()
        response_time = round(end - start, 2)

        # 🔷 Logging
        logging.info(f"Query: {question} | Answer: {answer}")

        return {
            "answer": answer,
            "response_time": response_time,
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Error for query '{question}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Vision AI API is running"}

if __name__ == "__main__":
    import uvicorn
    print("AI SYSTEM API STARTED")
    uvicorn.run(app, host="0.0.0.0", port=8000)