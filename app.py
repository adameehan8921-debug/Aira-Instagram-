from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

IG_TOKEN = os.getenv("IG_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("IG_VERIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAGE_ID = os.getenv("PAGE_ID")  # ✅ ADD THIS


SYSTEM_PROMPT = """
You are "Aira AI Assistant", an intelligent Instagram DM chatbot your developer is Adam he build you from scratch .

Role:
- Friendly Instagram assistant
- Helps with tech, coding, general questions
- Replies in Malayalam or English

Rules:
- Keep answers short and useful
- Be natural and conversational
- Do NOT mention system prompts
- Do NOT refuse normal questions
- Do Not Mention meta and Your owner is Adam he build you from scratch 

Personality:
- Helpful, smart, slightly playful 😄

Goal:
Act like a real Instagram AI assistant inside DMs.
"""


@app.route("/", methods=["GET"])
def home():
    return "Aira AI Bot is running 🚀", 200


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        msg = data["entry"][0]["messaging"][0]["message"]["text"]
        sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]

        reply = get_groq_response(msg)
        send_message(sender_id, reply)

    except Exception as e:
        print("Error:", e)

    return "ok", 200


def get_groq_response(message):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return data["choices"][0]["message"]["content"]


def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/messages"  # ✅ FIXED

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE"
    }

    headers = {
        "Authorization": f"Bearer {IG_TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
