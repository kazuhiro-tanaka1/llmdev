from flask import Flask, render_template, request, jsonify, session
from graph import run_chat

app = Flask(__name__)

# 本当はsecret manager等から取得すべき
app.secret_key = 'test_secret_key'

# 初期化
def init_history():
    if "history" not in session:
        session["history"] = []

@app.route("/")
def index():
    init_history()
    return render_template("index.html")

# チャット
@app.route("/chat", methods=["POST"])
def chat():
    init_history()

    user_input = request.json.get("message")

    # LangGraph実行
    response = run_chat(user_input)

    # 履歴追加
    session["history"].append({
        "user": user_input,
        "bot": response
    })

    session.modified = True

    return jsonify({
        "response": response,
        "history": session["history"]
    })

# 履歴削除
@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    session.modified = True

    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)