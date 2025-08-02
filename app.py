from flask import Flask, render_template, request, jsonify
from chatbot_logic import get_chatbot_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    user_input = request.json.get("msg")
    mode = request.json.get("mode")
    response = get_chatbot_response(user_input, mode)
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)