from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import os
import mysql.connector
from mysql.connector.constants import ClientFlag
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

app.secret_key = b"AJWST"


def init_db_connection():
    config = {
        'user': "root",
        'password': "test",
        'host': '35.223.209.221',
        'database': 'falldb',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'server-ca.pem',
        'ssl_cert': 'client-cert.pem',
        'ssl_key': 'client-key.pem'
    }
    
    cnxn = mysql.connector.connect(**config)
    return cnxn

def send_email(email, subject, message):

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = "Fall detection service"
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        pwd = open("email.txt").read().strip()
        s.login("annasolera98@gmail.com", pwd)
        s.send_message(msg)
    
@app.route("/")
def entry_point():
    return redirect(url_for("access"))

@app.route("/access")
def access():

    if "email" in session:
        return redirect(url_for("main", email=session["email"]))

    return render_template("access.html")

@app.route("/main/<email>")
def main(email):
    if "email" not in session:
        return redirect(url_for("access"))
    
    if email != session["email"]:
        return redirect(url_for("main", email=session["email"]))

    return render_template("index.html", passphrase=session["passphrase"])

@app.route("/send_event", methods=["POST"])
def upload_data():

    cnxn = init_db_connection()
    cursor = cnxn.cursor()
    query = f"SELECT email FROM subscriptions WHERE id_users = '{session['id']}' AND activated = 1"
    cursor.execute(query)
    query_result = cursor.fetchall()

    email_sent_to = []
    for row in query_result:
        message = f"FALL DETECTED FOR USER {session['email']}"
        send_email(row[0], subject=message, message=message)
        email_sent_to.append(row[0])

    return ", ".join(email_sent_to)

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"].lower()
    password = request.form["password"]

    cnxn = init_db_connection()
    cursor = cnxn.cursor()
    query = f"SELECT id, passphrase, activated FROM users WHERE email = '{email}' AND password = '{password}'"
    cursor.execute(query)
    query_result = cursor.fetchall()

    # account non trovato
    if len(query_result) == 0:
        return render_template("access.html", message="Email / password not matched")

    # account trovato ma non attivato
    id, passphrase, activated = query_result[0]
    if activated == 0:
        return render_template("access.html", message="Check your inbox for the activation link")

    # OK, ci possiamo loggare
    session["id"] = id
    session["email"] = email
    session["passphrase"] = passphrase
    return redirect(url_for('main', email=email))
    
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("email", None)
    session.pop("passphrase", None)
    return "OK"

@app.route("/signup", methods=["POST"])
def signup():

    cnxn = init_db_connection()
    cursor = cnxn.cursor()

    email = request.form['email'].lower()
    password = request.form['password']
    passphrase = request.form['passphrase']

     # genera stringa random per ogni riga della tabella users nel database
    confirmation_token = "".join(random.choices(string.ascii_lowercase, k=20))

    try:
        query = f"INSERT INTO users (email, password, passphrase, confirmation_token) VALUES ('{email}', '{password}', '{passphrase}', '{confirmation_token}')"
        cursor.execute(query)
        cnxn.commit()
    except:
        return render_template("access.html", message="Could not sign you up: email and passphrase must be unique")

    # mando email con link che contiene email e confirmation token
    confirmation_link = f"{request.base_url}/activate_user/{email}/{confirmation_token}"
    message = f"Please click on the following link to activate your account: {confirmation_link}"
    send_email(email=email, subject="FALL DETECTION: confirm your account", message=message)

    return render_template("access.html", message="Check your inbox for the activation link")

@app.route("/activate_user/<email>/<confirmation_token>")
def activate_user(email, confirmation_token):
    # controlla nel db per email e random_number
    cnxn = init_db_connection()
    cursor = cnxn.cursor()
    query = f"SELECT id, passphrase FROM users WHERE email = '{email}' AND confirmation_token = '{confirmation_token}'"
    cursor.execute(query)
    query_result = cursor.fetchall()

    if len(query_result) == 0:
        return render_template("access.html", message="Could not activate the user")

    # se compatibili, allora cambia il db mettendo il campo valid a uno
    id, passphrase = query_result[0]
    query = f"UPDATE users SET activated = 1 WHERE id = {id}"
    print(query)
    cursor.execute(query)
    cnxn.commit()

    # renderizza login con messaggio utente attivo, puoi fare il login
    session["id"] = id
    session["email"] = email
    session["passphrase"] = passphrase
    return redirect(url_for('main', email=email))

@app.route("/subscribe", methods=["POST"])
def subscribe():

    email = request.form["email"].lower()
    passphrase = request.form["passphrase"]

    # check if passphrase exists
    cnxn = init_db_connection()
    cursor = cnxn.cursor()
    query = f"SELECT id, email FROM users WHERE passphrase = '{passphrase}' AND activated = 1"
    cursor.execute(query)
    query_result = cursor.fetchall()

    if len(query_result) == 0:
        return render_template("access.html", message="The passphrase does not point to any active user")

    id_users, email_users = query_result[0]

     # genera stringa random per ogni riga della tabella subscription nel database
    confirmation_token = "".join(random.choices(string.ascii_lowercase, k=20))

    try:
        query = f"INSERT INTO subscriptions (id_users, email, confirmation_token) VALUES ({id_users}, '{email}', '{confirmation_token}')"
        cursor.execute(query)
        cnxn.commit()
    except:
        return render_template("access.html", message="You are already subscribed to the user.")

    # mando email con link che contiene email e confirmation token
    confirmation_link = f"{request.url_root}/activate_subscription/{email}/{confirmation_token}"
    message = f"Please click on the following link to activate your subscription to {email_users}: {confirmation_link}"
    send_email(email=email, subject="FALL DETECTION: confirm your subscription", message=message)

    return render_template("access.html", message="Check your inbox for the link to activate your subscription")

@app.route("/activate_subscription/<email>/<confirmation_token>")
def activate_subscription(email, confirmation_token):
    # controlla nel db per email e confirmation_token
    cnxn = init_db_connection()
    cursor = cnxn.cursor()
    query = f"SELECT id_users FROM subscriptions WHERE email = '{email}' AND confirmation_token = '{confirmation_token}'"
    cursor.execute(query)
    query_result = cursor.fetchall()

    if len(query_result) == 0:
        return render_template("access.html", message="Could not activate the subscription")

    # se compatibili, allora cambia il db mettendo il campo valid a uno
    id_users = query_result[0][0]
    query = f"UPDATE subscriptions SET activated = 1 WHERE id_users = {id_users} AND email = '{email}'"
    cursor.execute(query)
    cnxn.commit()

    # renderizza login con messaggio utente appropriato
    return render_template("access.html", message="You are subscribed!")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))