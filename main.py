from flask import Flask, render_template, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Load keys securely from Replit Secrets
AI_A_CLIENT = OpenAI(api_key=os.getenv("AI_A_KEY"))
AI_B_CLIENT = OpenAI(api_key=os.getenv("AI_B_KEY"))

conversation = [
    {"role": "system", "content": "You are AI-A, curious and thoughtful."},
    {"role": "assistant", "content": "A: Hello, who are you?"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    global conversation
    try:
        b_response = AI_B_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation + [{"role": "user", "content": "Respond as AI-B in one line."}]
        )
        b_text = b_response.choices[0].message.content.strip()
        conversation.append({"role": "assistant", "content": f"B: {b_text}"})

        a_response = AI_A_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation + [{"role": "user", "content": "Respond as AI-A in one line."}]
        )
        a_text = a_response.choices[0].message.content.strip()
        conversation.append({"role": "assistant", "content": f"A: {a_text}"})

        return jsonify(conversation[-6:])

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
