import os
import json
from dotenv import load_dotenv
from google import genai

# ================= SETUP =================
def initialize_client():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY1")
    return genai.Client(api_key=key)

# ================= INPUT HANDLER =================
def fetch_resume_input():
    option = input("Enter 1 for text input or 2 for file input: ")

    if option == "1":
        return input("Enter your resume text:\n")

    elif option == "2":
        file_path = input("Enter file name (example: resume.txt): ")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except:
            print("File not found")
            exit()

    else:
        print("Invalid choice")
        exit()

# ================= PROMPT BUILDER =================
def build_prompt(resume_content):
    return f"""
You are an AI Resume Screening System.

STRICT RULES:
- Do NOT assume anything
- Do NOT add explanation outside JSON
- Do NOT guess missing data
- Output ONLY valid JSON

OUTPUT FORMAT:
{{
    "name": "string",
    "skills": ["list of skills"],
    "eligibility": "Eligible / Not Eligible"
}}

LOGIC:
- Extract candidate name
- Extract skills from resume
- If candidate has relevant skills → "Eligible"
- If no skills → "Not Eligible"

FEW-SHOT EXAMPLES:

Input:
Name: A
Skills: Python, SQL
Output:
{{"name": "A", "skills": ["Python", "SQL"], "eligibility": "Eligible"}}

Input:
Name: B
Skills: Communication
Output:
{{"name": "B", "skills": ["Communication"], "eligibility": "Eligible"}}

Input:
Name: C
Skills: None
Output:
{{"name": "C", "skills": [], "eligibility": "Not Eligible"}}

ANTI-PROMPT:
- Do NOT explain reasoning
- Do NOT add extra text
- Do NOT assume skills not mentioned

Now analyze this resume:

{resume_content}
"""

# ================= AI CALL =================
def generate_result(ai_client, final_prompt):
    return ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=final_prompt,
        config={"response_mime_type": "application/json"}
    )

# ================= RESPONSE PARSER =================
def parse_output(response_obj):
    try:
        return response_obj.parsed if response_obj.parsed else json.loads(response_obj.text)
    except:
        print("Error: Invalid JSON response")
        exit()

# ================= MAIN =================
def run_pipeline():
    client = initialize_client()
    resume = fetch_resume_input()
    prompt = build_prompt(resume)

    response = generate_result(client, prompt)
    result = parse_output(response)

    print("\nOutput:\n")
    print(json.dumps(result, indent=4))


# ================= EXECUTION =================
if __name__ == "__main__":
    run_pipeline()