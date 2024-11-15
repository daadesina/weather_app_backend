from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)


conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password_hash TEXT)''')
conn.commit()
conn.close()



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
    conn.commit()
    conn.close()
    return jsonify(message="User registered successfully"), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[3], password):  # assuming password_hash is at index 3
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401

if __name__ == '__main__':
    app.run(debug=True)