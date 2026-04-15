import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from agent import ResumeAgent

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "local-demo-secret")

agent = ResumeAgent()


def get_chat_messages():
    messages = session.get("chat_messages")
    if not messages:
        messages = [
            {
                "role": "assistant",
                "content": "Hello. I am your AI agent. How can I help today?",
            }
        ]
        session["chat_messages"] = messages
    return messages


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", messages=get_chat_messages())


@app.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if request.method == "GET":
        return render_template("upload.html", upload_status=session.get("upload_status", ""))

    file = request.files.get("resume")
    if not file or not file.filename:
        session["upload_status"] = "No file selected."
        return redirect(url_for("upload_resume"))

    filename = secure_filename(file.filename)
    save_path = UPLOAD_DIR / filename
    file.save(save_path)
    session["latest_resume"] = str(save_path)
    session["upload_status"] = f"Upload complete: {filename}"
    return redirect(url_for("upload_resume"))


@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.form.get("prompt", "").strip()
    messages = get_chat_messages()

    if not prompt:
        messages.append({"role": "assistant", "content": "Please enter a message."})
        session["chat_messages"] = messages[-12:]
        return redirect(url_for("index"))

    latest_resume = session.get("latest_resume")
    output = agent.ask(prompt, latest_resume)
    messages.extend(
        [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": output},
        ]
    )
    session["chat_messages"] = messages[-12:]
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
