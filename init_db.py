import mysql.connector
from mysql.connector.constants import ClientFlag

config = {
    'user': "root",
    'password': "test",
    'host': '35.223.209.221',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'secret/server-ca.pem',
    'ssl_cert': 'secret/client-cert.pem',
    'ssl_key': 'secret/client-key.pem'
}

# create DB (run only once)
if False:
    cnxn = mysql.connector.connect(**config) ## unpack config dict in parameters
    cursor = cnxn.cursor()  # initialize connection cursor
    cursor.execute('CREATE DATABASE falldb')  # create a new database
    cnxn.close()  # close connection because we will be reconnecting to testdb

config['database'] = 'falldb'  # add new database to config dict
cnxn = mysql.connector.connect(**config)
cursor = cnxn.cursor()

# clean up database
cursor.execute("DROP TABLE users")
cursor.execute("DROP TABLE subscriptions")

# create tables
cursor.execute("CREATE TABLE users (" \
                "id INT NOT NULL AUTO_INCREMENT, " \
                "email VARCHAR(255) NOT NULL, " \
                "password VARCHAR(255) NOT NULL, " \
                "passphrase VARCHAR(255) NOT NULL, " \
                "confirmation_token VARCHAR(255) NOT NULL, " \
                "activated INT DEFAULT 0, " \
                "PRIMARY KEY (id)"
                ")")

cursor.execute("CREATE TABLE subscriptions (" \
                "id INT NOT NULL AUTO_INCREMENT, " \
                "id_users INT NOT NULL, " \
                "email VARCHAR(255) NOT NULL, " \
                "confirmation_token VARCHAR(255) NOT NULL, " \
                "activated INT DEFAULT 0, " \
                "PRIMARY KEY (id), "
                "FOREIGN KEY (id_users) REFERENCES users(id)" \
                ")")

cnxn.commit()  # this commits changes to the database

# test database
if False:
    cursor.execute("insert into users (email, password, passphrase, confirmation_token) VALUES ('anna@gmail.com','anna','qwerty','1111')")
    cursor.execute("insert into users (email, password, passphrase, confirmation_token) VALUES ('anna@gmail.com','anna','qwerty','1111')")

    cnxn.commit()  # and commit changes

    cursor.execute("select * from users")
    out = cursor.fetchall()
    print([i[0] for i in cursor.description])
    for row in out:
        print(row)