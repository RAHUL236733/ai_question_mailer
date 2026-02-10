from flask import Flask, render_template, request
from ai_generator import generate_questions
from email_sender import send_email

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic")

    try:
        count = int(request.form.get("count"))
    except:
        count = 10

    email = request.form.get("email")

    # Debug: form data
    print("Topic:", topic)
    print("Count:", count)
    print("Email:", email)

    # Generate questions
    questions = generate_questions(topic, count)

    # Debug: AI output
    print("Generated Questions:\n", questions)

    # Send email
    send_email(email, topic, questions)

    message = f"AI questions generated and sent to {email}"

    return render_template(
        "index.html",
        message=message,
        questions=questions
    )


if __name__ == "__main__":
    app.run(debug=True)
