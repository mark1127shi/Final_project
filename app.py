import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import timedelta
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))
app.secret_key = 'secret-key-123'
app.permanent_session_lifetime = timedelta(minutes=30)
DATABASE = os.path.join(current_dir, 'users.db')
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        organisation TEXT DEFAULT '',
        address TEXT DEFAULT '',
        city TEXT DEFAULT '',
        state TEXT DEFAULT '',
        country TEXT DEFAULT '',
        postalcode TEXT DEFAULT ''
    )
    ''')
    conn.commit()
    conn.close()
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                           (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session.permanent = True
                session['loggedin'] = True
                session['id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('index'))
            else:
                msg = 'Username or Password is wrong'
        else:
            msg = 'Please enter username and password！'
    return render_template('login.html', msg=msg)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        country = request.form.get('country', '')
        postalcode = request.form.get('postalcode', '')
        if username and password and email:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                msg = 'Unvilid username'
            else:
                cursor.execute('''
                INSERT INTO users (username, password, email, city, state, country, postalcode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, password, email, city, state, country, postalcode))
                conn.commit()
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id = cursor.fetchone()[0]
                session.permanent = True
                session['loggedin'] = True
                session['id'] = user_id
                session['username'] = username
                conn.close()
                return redirect(url_for('index'))
            conn.close()
        else:
            msg = 'Please enter all below！'
    return render_template('register.html', msg=msg)
@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html',
                               username=session['username'],
                               msg=f'Welcome back，{session["username"]}！')
    return redirect(url_for('login'))
@app.route('/display')
def display():
    if 'loggedin' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['id'],))
        account = cursor.fetchone()
        conn.close()
        if account:
            return render_template('display.html', account=dict(account))
    return redirect(url_for('login'))
@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    msg = ''
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        country = request.form.get('country', '')
        postalcode = request.form.get('postalcode', '')
        cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?',
                       (username, session['id']))
        if cursor.fetchone():
            msg = 'The username is used by others！'
        else:
            cursor.execute('''
            UPDATE users 
            SET username = ?, password = ?, email = ?, 
                city = ?, state = ?, country = ?, postalcode = ?
            WHERE id = ?
            ''', (username, password, email, city, state, country, postalcode, session['id']))
            conn.commit()
            msg = 'Update success！'
            session['username'] = username
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['id'],))
    account = cursor.fetchone()
    conn.close()
    if account:
        return render_template('update.html', msg=msg, account=dict(account))
    return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    init_db()
    print("用户管理系统启动")
    print("访问地址: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)