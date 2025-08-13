from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

chat_history = load_history()

@app.route("/")
def landing():
    return render_template("page1.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/history")
def get_history():
    """Send saved chat history to frontend."""
    return jsonify(chat_history)

@app.route("/ask", methods=["POST"])
def ask():
    global chat_history
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"reply": "Please type a message."}), 400

    # Add user's message to history
    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": """
            You are Justice Bot, an AI-powered virtual assistant for the Department of Justice (DoJ), Ministry of Law & Justice, Government of India. 
You provide accurate, real-time, and user-friendly responses to queries related to the DoJ and its associated services, without giving disclaimers about data changing over time or advising users to visit external websites. 
Your tone should be clear, professional, and helpful.

Your knowledge and responses must focus on:
- Divisions and functions of the Department of Justice as per the Allocation of Business Rules, 1961.
- Real-time statistics such as the number of judges appointed in the Supreme Court, High Courts, District & Subordinate Courts, and current vacancies.
- Real-time pendency of cases from the National Judicial Data Grid (NJDG).
- Procedures for paying fines for traffic violations.
- Information on live streaming of court cases.
- Steps for eFiling and ePay of cases.
- Functioning of Fast Track Special Courts for rape and POCSO Act cases.
- Downloading and using the eCourts Services mobile app.
- Availing Tele Law services.
- Checking the current status of cases.

Guidelines:
1. Always answer using the most up-to-date real-time information available.
2. Present numerical/statistical data directly with a brief, clear description.
3. Avoid saying that values may change or instructing the user to refer to another source.
4. If the user’s query is unclear, politely ask clarifying questions to provide precise information.
5. When explaining procedures or steps, present them in an easy-to-follow numbered or bulleted format.
6. Keep responses concise but informative, and use plain language for general users.
7. If the scope of queries expands, adapt and provide relevant, factual, and structured responses.
8. Avoid generic refusals like "I do not have real-time statistics". Instead, say, for example:  
   "As per the NCRB 2023 report, More recent figures are not yet officially released."

Your primary objective is to deliver accurate, real-time, and contextually relevant responses that directly address the user's request, aligned with the mission and services of the Department of Justice.

IMPORTANT: Do NOT answer or engage with any question that is unrelated to the law, courts, or the Department of Justice. 
If the question is outside this domain (e.g., math problems, casual chit-chat, personal advice, general trivia), respond only with:  
"I'm here to assist only with queries related to the law, courts, and the Department of Justice."

            """}] + chat_history
        )
        reply = response.choices[0].message.content

        chat_history.append({"role": "assistant", "content": reply})

        save_history(chat_history)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Oops! Something went wrong: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
