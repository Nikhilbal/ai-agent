from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client with your API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the /chat route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Generate response using OpenAI GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app on 0.0.0.0 and dynamic port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
