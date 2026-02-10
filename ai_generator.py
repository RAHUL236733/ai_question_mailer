import os
import requests
import random
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

HISTORY_FILE = "history.txt"


# ------------------ WIKIPEDIA API ------------------

def fetch_wikipedia_context(topic):
    """
    Fetch short summary for any topic using Wikipedia public API
    (limited length to avoid HF failures)
    """
    topic = topic.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            text = data.get("extract", "")
            return text[:600]  # IMPORTANT: limit context
    except Exception as e:
        print("Wikipedia error:", e)

    return ""


# ------------------ HISTORY ------------------

def load_history():
    """
    Load previously generated questions to avoid repetition
    """
    if not os.path.exists(HISTORY_FILE):
        return set()

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_history(questions):
    """
    Save generated questions permanently
    """
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for q in questions:
            f.write(q + "\n")


# ------------------ AI GENERATION ------------------

def generate_questions(topic, count):
    count = int(count)
    variation = random.randint(1, 100000)

    wiki_context = fetch_wikipedia_context(topic)
    previous_questions = load_history()

    prompt = f"""
Generate {count} UNIQUE viva/interview questions on the topic "{topic}".

Context:
{wiki_context}

Focus on:
- Core concepts
- Practical usage
- Project explanation
- Real-world applications

Do not repeat previous questions.
Only list questions.
Variation ID: {variation}
"""

    collected_questions = []

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        print("HF status:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                lines = data[0]["generated_text"].split("\n")
                for line in lines:
                    q = line.strip()
                    if q and q not in previous_questions:
                        collected_questions.append(q)

    except Exception as e:
        print("AI error:", e)

    # Remove duplicates & limit count
    final_questions = list(dict.fromkeys(collected_questions))[:count]

    # ---------- FALLBACK (ONLY IF AI FAILS) ----------
    if not final_questions:
        final_questions = [
            f"What is {topic}?",
            f"Explain the importance of {topic}.",
            f"Where is {topic} used in real-world applications?",
            f"How does {topic} relate to your project?",
            f"What are the limitations of {topic}?"
        ][:count]

    save_history(final_questions)
    return "\n".join(final_questions)
