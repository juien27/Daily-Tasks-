import os
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Memory storage
memory = []

# System Persona
SYSTEM_PROMPT = "You are a Technical Recruiter. You only ask job-related questions and evaluate candidates. Never break character."

MAX_MEMORY = 5

print("🤖 Recruiter Bot Started (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    # Add user message
    memory.append(f"User: {user_input}")

    # Keep only last 5 exchanges (10 messages: user+bot)
    if len(memory) > MAX_MEMORY * 2:
        memory = memory[-MAX_MEMORY * 2:]

    # Build prompt with memory
    full_prompt = SYSTEM_PROMPT + "\n\n" + "\n".join(memory)

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=full_prompt
    )

    bot_reply = response.text

    print("Bot:", bot_reply)

    # Store bot reply
    memory.append(f"Bot: {bot_reply}")



