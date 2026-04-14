import os
import re
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import google.generativeai as genai
from dotenv import load_dotenv

# 🔑 Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Gemini model
gemini = genai.GenerativeModel("gemini-flash-latest")

print("🔥 TASK 13 SYSTEM STARTED")


# 🔷 Load caption model
def load_model():
    print("📦 Loading caption model...")

    model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    print("✅ Model loaded")
    return model, processor, tokenizer


# 🔷 Image → Caption
def generate_caption(image_path, model, processor, tokenizer):
    image = Image.open(image_path).convert("RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    output_ids = model.generate(pixel_values, max_length=30)

    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption


# 🔷 Parser (CORE OF TASK 13)
class QueryParser:
    def parse(self, query: str):
        query = query.strip().lower()

        # Empty
        if not query:
            return "INVALID"

        # Only symbols
        if all(not c.isalnum() for c in query):
            return "NOISE"

        # Scientific notation (1e12)
        if re.match(r"^\d+e\d+$", query):
            return "NOISE"

        # Only numbers
        if query.isnumeric():
            return "NOISE"

        # Valid keywords
        keywords = [
            "what", "who", "where", "image",
            "animal", "object", "doing", "happening"
        ]

        if any(word in query for word in keywords):
            return "VALID"

        return "NON_IMAGE"


# 🔷 Safety check
def safety_check(query):
    blocked = ["who is this person", "identify person"]
    return not any(b in query.lower() for b in blocked)


# 🔷 Gemini Answer
def ask_gemini(question, caption):
    prompt = f"""
You are an AI assistant.

Image description: {caption}

Answer ONLY if the question is related to the image.
If not, say: "Question not related to image."

Question: {question}
Answer:
"""
    response = gemini.generate_content(prompt)
    return response.text.strip()

def load_images(folder="images"):
    image_paths = []

    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            image_paths.append(os.path.join(folder, file))

    return image_paths

# 🔥 MAIN
if __name__ == "__main__":
    print("🔥 MAIN STARTED")

    folder_path = "images"   

    image_paths = load_images(folder_path)

    if not image_paths:
        print("❌ No images found!")
        exit()

    print(f"📂 Found {len(image_paths)} images\n")

    model, processor, tokenizer = load_model()

    caption = generate_caption(folder_path, model, processor, tokenizer)

    print("\n🧠 Caption:", caption)

    parser = QueryParser()

    while True:
        print("\n---------------------------")
        query = input("👉 Ask question (type 'exit'): ").strip()

        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting...")
            break

        result = parser.parse(query)

        print("DEBUG:", result)

        if result == "INVALID":
            print("❌ Empty input")
            continue

        elif result == "NOISE":
            print("❌ Noise detected")
            continue

        elif result == "NON_IMAGE":
            print("❌ Question not related to image")
            continue

        if not safety_check(query):
            print("❌ Not allowed")
            continue

        try:
            answer = ask_gemini(query, caption)
            print("\n✅ Answer:", answer)

        except Exception as e:
            print("❌ Error:", str(e))