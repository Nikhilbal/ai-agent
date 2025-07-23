from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # ✅ Use the PORT Render provides
    port = int(os.environ.get("PORT", 10000))  # fallback if PORT isn't set
    app.run(host="0.0.0.0", port=port)
# This is a simple Flask application that integrates with OpenAI's API to provide chat functionality.
# It listens for POST requests at the /chat endpoint, processes the user's message,
# and returns a response from the OpenAI model.
# Make sure to set the OPENAI_API_KEY in your environment variables.