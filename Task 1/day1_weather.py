import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# load env
load_dotenv()

API_KEY = os.getenv("API_KEY")

cities = [
    "Mumbai", "London", "New York", "Tokyo", "Delhi",
    "Sydney", "Paris", "Dubai", "Singapore", "Berlin"
]

results = []

for city in cities:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        temp_c = data["main"]["temp"] - 273.15
        temp_c = str(round(temp_c, 2)) + " C"
        humidity = data["main"]["humidity"]
        weather = data["weather"][0]["main"]
        time = datetime.utcfromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M:%S')
        
        city_data = {
            "city": city,
            "temperature_c": temp_c,
            "humidity": humidity,
            "weather": weather,
            "time": time
        }

        results.append(city_data)

        print("\nCity:", city)

    else:
        print("\nError for", city, ":", response.text)

# save to json
with open("keywords.json", "w") as file:
    json.dump(results, file, indent=4)

print("\n✅ Data saved to keywords.json")