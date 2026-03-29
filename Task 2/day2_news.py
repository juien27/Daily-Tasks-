import requests
import json
import os
import re
from dotenv import load_dotenv

# load API key
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# remove quotes if present
if API_KEY:
    API_KEY = API_KEY.replace('"', '')

# load keywords
with open("keywords.json") as f:
    KEYWORDS = json.load(f)

#  predefined companies (rule-based)
KNOWN_COMPANIES = [
    "Apple", "Tesla", "Google", "Microsoft",
    "Amazon", "Meta", "Sony", "TikTok", "BYD", "Oppo"
]

# API call
url = f"https://newsapi.org/v2/everything?q=global&pageSize=50&apiKey={API_KEY}"
res = requests.get(url)

results = []

if res.status_code == 200:
    articles = res.json().get("articles", [])

    for a in articles:
        title = a.get("title", "")
        desc = title + " " + (a.get("description") or "")

        text = desc.lower()

        #  classification
        category = "GENERAL"
        for key, words in KEYWORDS.items():
            if any(word in text for word in words):
                category = key
                break

        #  correct company extraction
        companies = []
        for company in KNOWN_COMPANIES:
            if company.lower() in text:
                companies.append(company)

        #  currency & percentage
        currency = re.findall(r'[$₹€]\s?\d+', desc)
        percent = re.findall(r'\d+%', desc)

        results.append({
            "title": title,
            "category": category,
            "companies": companies,
            "currency": currency,
            "percentage": percent
        })

else:
    print("API Error:", res.text)

# save output
with open("news_output.json", "w") as f:
    json.dump(results, f, indent=4)

print("✅ Final clean data saved")