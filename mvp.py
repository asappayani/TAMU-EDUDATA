import requests
from pymongo import MongoClient
import json

# === Config ===
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
VALID_ACTIONS = ["query_best_professor", "average_gpa"]

# === Connect MongoDB ===
client = MongoClient("mongodb://localhost:27017/")
db = client["tamu_gpa"]
collection = db["gpa_distribution"]

def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]

while True:
    # === Get user prompt ===
    user_prompt = input("\nAsk me about GPA stuff (or type 'exit' to quit): ")
    if user_prompt.lower() == "exit":
        break

    # === Step 1: Send prompt to Ollama for intent ===
    intent_prompt = f"""
You are an AI that extracts actions for querying a GPA database.

ONLY respond in this strict JSON format:
{{
  "action": one of {VALID_ACTIONS},
  "course": "...",
  "professor": "...",  // optional
  "semester": "..."    // optional
}}

Prompt: "{user_prompt}"
"""

    intent_response = call_ollama(intent_prompt)
    print("\n[Raw Ollama Response]:", intent_response)

    # === Step 2: Parse intent JSON ===
    try:
        intent_data = json.loads(intent_response)
        action = intent_data["action"]
        if action not in VALID_ACTIONS:
            print(f"[Error] Invalid action: {action}")
            continue
        course = intent_data.get("course")
        professor = intent_data.get("professor")
        semester = intent_data.get("semester")
    except json.JSONDecodeError:
        print("[Error] Failed to parse JSON from Ollama")
        continue

    # === Step 3: Query MongoDB based on action ===
    result_data = None

    # Fetch the document for Mays Business School
    school_doc = collection.find_one({"college": "MAYS BUSINESS SCHOOL"})
    if not school_doc:
        print("[Error] No document found for Mays Business School")
        continue

    # Filter for matching course entries inside the courses array
    course_entries = [entry for entry in school_doc["courses"] if entry["course"] == course]

    print("\n[Debug] Matching entries:")
    for entry in course_entries:
        print(entry)

    if not course_entries:
        print(f"[Error] No data found for course {course}")
        continue

    if action == "query_best_professor":
    # Compute avg GPA and store rating per professor
        prof_data = {}
        for entry in course_entries:
            prof = entry["professor"]
            gpa = entry["gpa"]
            rating = entry.get("rating", "N/A")
            if prof not in prof_data:
                prof_data[prof] = {"gpas": [], "rating": rating}
            prof_data[prof]["gpas"].append(gpa)

        # Calculate average GPA for each professor
        avg_per_prof = {
            prof: sum(data["gpas"]) / len(data["gpas"])
            for prof, data in prof_data.items()
        }

        # Find the best professor by highest average GPA
        best_prof = max(avg_per_prof.items(), key=lambda x: x[1])[0]
        best_avg = avg_per_prof[best_prof]
        best_rating = prof_data[best_prof]["rating"]

        result_data = {
            "professor": best_prof,
            "avg_gpa": round(best_avg, 2),
            "Rate_My_Professor_rating": best_rating
        }

    elif action == "average_gpa":
        filtered_entries = course_entries
        if semester:
            filtered_entries = [e for e in course_entries if e["semester"] == semester]

        if filtered_entries:
            avg_gpa = sum(e["gpa"] for e in filtered_entries) / len(filtered_entries)
            result_data = {"avg_gpa": round(avg_gpa, 2)}
        else:
            result_data = None

    print("\n[MongoDB Result]:", result_data)

    # === Step 4: Use Ollama to make a human response ===
    if result_data:
        final_prompt = f"""
            You are a helpful college course registration assistant, keep the answer concise and don't state any uncertainties or concerns. Based on this data that has been queried from a database: {result_data},
            answer the user’s original question: "{user_prompt}"
        """
        human_response = call_ollama(final_prompt)
        print("\n[Final Answer]:", human_response)
    else:
        print("\nNo data found for that query.")
