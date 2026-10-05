from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE ---------------- #
def get_db():
    return sqlite3.connect("database.db")


def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        status TEXT
    )''')

    conn.commit()
    conn.close()


create_tables()


# ---------------- HOME ---------------- #
@app.route('/')
def home():
    return render_template("index.html")


# ---------------- REGISTER ---------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (user, pwd))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")


# ---------------- LOGIN ---------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        data = cur.fetchone()
        conn.close()

        if data:
            session['user'] = user
            return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", books=books)


# ---------------- ADD BOOK ---------------- #
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO books (title,author,status) VALUES (?,?,?)",
                    (title, author, "Available"))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template("add_book.html")


# ---------------- BORROW ---------------- #
@app.route('/borrow/<int:id>')
def borrow(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE books SET status='Borrowed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# ---------------- RETURN ---------------- #
@app.route('/return/<int:id>')
def return_book(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE books SET status='Available' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# ---------------- DELETE ---------------- #
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# ---------------- EDIT ---------------- #
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        cur.execute("UPDATE books SET title=?, author=? WHERE id=?",
                    (title, author, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cur.execute("SELECT * FROM books WHERE id=?", (id,))
    book = cur.fetchone()
    conn.close()

    return render_template("edit_book.html", book=book)


# ---------------- LOGOUT ---------------- #
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)