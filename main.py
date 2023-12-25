from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/<name>")
def hello_world(name="unknown"):
    return f"<p>Hello, {name}!</p>"
