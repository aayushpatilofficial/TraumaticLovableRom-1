from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")  # change for production

# Email configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "aayushpatilofficial@gmail.com")  # your email
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "hvuo jrps fvfn bgvc")   # app password
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME", "aayushpatilofficial@gmail.com")

mail = Mail(app)

# Paths
DATA_DIR = "data"
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize files if missing
if not os.path.exists(CONTACTS_FILE):
    with open(CONTACTS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(PORTFOLIO_FILE):
    sample = [
        {
            "id": 1,
            "title": "Math Quiz App",
            "desc": "Interactive advanced math quizzes.",
            "tags": ["Flask", "AI", "Quiz"]
        },
        {
            "id": 2,
            "title": "HopePulse Prototype",
            "desc": "Wearable mental health demo.",
            "tags": ["Hardware", "ML"]
        }
    ]
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(sample, f, indent=2)

# Helpers
def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Inject datetime globally into templates
@app.context_processor
def inject_now():
    return {"datetime": datetime}

# Routes
@app.route("/")
def index():
    portfolio = read_json(PORTFOLIO_FILE)
    return render_template("index.html", portfolio=portfolio)

@app.route("/api/portfolio")
def api_portfolio():
    return jsonify(read_json(PORTFOLIO_FILE))

@app.route("/contact", methods=["POST"])
def contact():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    message = form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("index") + "#contact")

    entry = {
        "name": name,
        "email": email,
        "message": message,
        "time": datetime.utcnow().isoformat() + "Z"
    }

    # Save to contacts.json
    contacts = read_json(CONTACTS_FILE)
    contacts.insert(0, entry)
    write_json(CONTACTS_FILE, contacts)

    # Send email
    try:
        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=[os.getenv("EMAIL_USER", "aayushpatilofficial@gmail.com")],  # your email
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
        )
        mail.send(msg)
        flash("Thanks! Your message has been sent successfully.", "success")
    except Exception as e:
        print("Email send failed:", e)
        flash("Message saved, but email could not be sent.", "warning")

    return redirect(url_for("index") + "#contact")

# Simple contacts viewer (not protected) — remove or protect in prod
@app.route("/_contacts")
def _contacts():
    return jsonify(read_json(CONTACTS_FILE))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
