from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

@app.route("/")
def access():
    return render_template("access.html")

@app.route("/main/<email>")
def main(email):
    return render_template("index.html")

@app.route("/upload_data", methods=["GET", "POST"])
def upload_data():
    i = request.form["i"]
    j = request.form["j"]
    k = request.form["k"]
    return i

@app.route("/login", methods=["POST"])
def login():

    # dovremo gestirlo tramite database
    if request.form["email"] == "anna" and request.form["password"] == "anna":
        # controlla se attivo
        if True:
            return redirect(url_for('main', email="anna"))
        else:
            return render_template("access.html", message="Check your inbox for the activation link")

    else:
        return render_template("access.html", message="Email / password not matched")

@app.route("/signup", methods=["POST"])
def signup():

    # controllo che email non sia già presente
    if request.form["email"] == "annasolera98@gmail.com":
        return render_template("access.html", message="Email address already in use")
        
    # controllo che passphrase non sia già usata
    if request.form["passphrase"] == "accelerometro anna":
        return render_template("access.html", message="Passphrase already in use")

    # inserire nel database email, password, passphrase, numero random e valid a zero
    random_number = str(random.randint(0, 20000))

    # mando email con link che contiene email e random_number
    # esempio: 127.0.0.1/activate_user/email/random_number
    # https://docs.python.org/3/library/email.examples.html

    return render_template("access.html", message="Check your inbox for the activation link")

@app.route("/activate_user/<email>/<random_number>")
def activate_user(email, random_number):
    # controlla nel db per email e random_number
    # ritorna errore

    # se compatibili, allora cambia il db mettendo il campo valid a uno

    # renderizza login con messaggio utente attivo, puoi fare il login
    return redirect(url_for('main', email=email))

@app.route("/recover_password")
def recover_password():
    pass

@app.route("/subscribe")
def subscribe():
    # check if passphrase exists

    # check if not already subscribed

    # c'è da aggiungere un campo random anche qui

    # send email with activation link to email

    return render_template("access.html", message="Check your inbox for the activation link")

@app.route("/activate_user/<email>/<random_number>")
def activate_subscriber(email, random_number):
    # controlla nel db per email e random_number
    # ritorna errore

    # se compatibili, allora cambia il db mettendo il campo valid a uno

    # renderizza login con messaggio utente attivo, puoi fare il login
    return render_template("access.html", message="You are subscribed!")