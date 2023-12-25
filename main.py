from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/upload_data", methods=["GET", "POST"])
def upload_data():
    i = request.form["i"]
    j = request.form["j"]
    k = request.form["k"]
    return i
