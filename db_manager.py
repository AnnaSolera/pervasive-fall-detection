import mysql.connector
from mysql.connector.constants import ClientFlag

def init_db_connection(db_name: str = None):
    config = {
        'user': "root",
        'password': "test",
        'host': '35.223.209.221',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'server-ca.pem',
        'ssl_cert': 'client-cert.pem',
        'ssl_key': 'client-key.pem'
    }

    if db_name is not None:
        config["database"] = db_name
    
    cnxn = mysql.connector.connect(**config)
    return cnxn

def create_db():
    cnxn = init_db_connection()
    cursor = cnxn.cursor()  # initialize connection cursor
    cursor.execute('CREATE DATABASE falldb')  # create a new database
    cnxn.close()  # close connection because we will be reconnecting to testdb

def create_tables():
    cnxn = init_db_connection(db_name="falldb")

    # clean up database
    cursor = cnxn.cursor()  # initialize connection cursor
    cursor.execute("DROP TABLE subscriptions")
    cursor.execute("DROP TABLE users")

    # create tables
    cursor.execute("CREATE TABLE users (" \
                    "id INT NOT NULL AUTO_INCREMENT, " \
                    "email VARCHAR(255) NOT NULL, " \
                    "password VARCHAR(255) NOT NULL, " \
                    "passphrase VARCHAR(255) NOT NULL, " \
                    "confirmation_token VARCHAR(255) NOT NULL, " \
                    "activated INT DEFAULT 0, " \
                    "PRIMARY KEY (id), " \
                    "UNIQUE (email), " \
                    "UNIQUE (passphrase)" \
                    ")")

    cursor.execute("CREATE TABLE subscriptions (" \
                    "id_users INT NOT NULL, " \
                    "email VARCHAR(255) NOT NULL, " \
                    "confirmation_token VARCHAR(255) NOT NULL, " \
                    "activated INT DEFAULT 0, " \
                    "PRIMARY KEY (id_users, email), "
                    "FOREIGN KEY (id_users) REFERENCES users(id)" \
                    ")")

    cnxn.commit()  # this commits changes to the database

if __name__ == "__main__":
    # create_db()
    # create_tables

    cnxn = init_db_connection(db_name="falldb")
    cursor = cnxn.cursor()

    # cursor.execute("insert into users (email, password, passphrase, confirmation_token) VALUES ('anna@gmail.com','anna','qwerty','1111')")
    # cursor.execute("insert into users (email, password, passphrase, confirmation_token) VALUES ('anna@gmail.com','anna','qwerty','1111')")
    # cnxn.commit()  # and commit changes

    cursor.execute("select * from subscriptions")
    out = cursor.fetchall()
    print([i[0] for i in cursor.description])
    for row in out:
        print(row)
