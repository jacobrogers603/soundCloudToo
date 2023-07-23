from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key

# Database setup
conn = sqlite3.connect('credentials.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS credentials
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL UNIQUE,
                   email TEXT NOT NULL UNIQUE,
                   password TEXT NOT NULL)''')
conn.commit()
conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not password or not email:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('register'))

        hashed_password = hash_password(password)

        try:
            conn = sqlite3.connect('credentials.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO credentials (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            print('Registration done.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'error')
            print('Registration error.')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if (not username and not email) or not password:
            flash('Please fill in username or email and password fields.', 'error')
            return redirect(url_for('login'))

        hashed_password = hash_password(password)

        try:
            conn = sqlite3.connect('credentials.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM credentials WHERE username = ? AND email = ? AND password = ?', (username, email, hashed_password))
            user = cursor.fetchone()

            if user is not None:
                flash('Login successful!', 'success')
                print('Logged in')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password. Please try again.', 'error')
                print('Login error')
                return redirect(url_for('login'))
        finally:
            conn.close()

    return render_template('login/index.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, )