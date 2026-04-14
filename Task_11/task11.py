import os
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import google.generativeai as genai
from dotenv import load_dotenv

# 🔑 Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini model
gemini = genai.GenerativeModel("gemini-flash-latest")

print("🚀 SYSTEM STARTING...")


# 🔷 Load Caption Model (Task 11)
def load_model():
    print("📦 Loading caption model...")

    model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    print("✅ Caption model loaded")
    return model, processor, tokenizer


# 🔷 Image → Caption
def generate_caption(image_path, model, processor, tokenizer):
    image = Image.open(image_path).convert("RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    output_ids = model.generate(pixel_values, max_length=30)

    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption


# 🔷 Ask Gemini (SMART AI)
def ask_gemini(question, caption):
    prompt = f"""
You are an AI assistant.

Image description: {caption}

Answer the user's question based ONLY on this image description.
If question is unrelated, say: "Question not related to image."

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
# 🔥 MAIN UI
if __name__ == "__main__":
    print("🔥 MAIN STARTED")

    folder_path = "images" 
    image_paths = load_images(folder_path)

    if not image_paths:
        print("❌ No images found!")
        exit()


    # Load model
    model, processor, tokenizer = load_model()

    # Generate caption
    caption = generate_caption(folder_path, model, processor, tokenizer)

    print("\n🧠 Caption:", caption)

    # UI Loop
    while True:
        print("\n---------------------------")
        query = input("👉 Ask question (type 'exit'): ").strip()

        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting...")
            break

        if query == "":
            print("⚠️ Enter a question")
            continue

        try:
            answer = ask_gemini(query, caption)
            print("\n✅ Answer:", answer)

        except Exception as e:
            print("❌ Error:", str(e))