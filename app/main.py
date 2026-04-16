import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from agent import ResumeAgent
from tools import upload_resume_file

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)
PROMPT_COLOR = "\033[96m"
COLOR_RESET = "\033[0m"

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
    logger.info("upload_received filename=%s save_path=%s", filename, save_path)
    file.save(save_path)
    uploaded_location = upload_resume_file(save_path, filename)
    logger.info("upload_processed filename=%s stored_at=%s", filename, uploaded_location)
    session["latest_resume"] = uploaded_location
    if uploaded_location.startswith("s3://"):
        session["upload_status"] = f"Upload complete: {filename} to {uploaded_location}"
    else:
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
    logger.info("chat_request latest_resume=%s", latest_resume)
    logger.info("chat_request_prompt=%s%s%s", PROMPT_COLOR, prompt, COLOR_RESET)
    output = agent.ask(prompt, latest_resume)
    logger.info("chat_response prompt=%r output_preview=%r", prompt, output[:500])
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
