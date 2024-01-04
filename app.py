from cs50 import SQL
from flask import Flask, render_template, session
from flask_session import Session

from helpers import login_required


app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///library.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, owner_id INTEGER NOT NULL, olid TEXT, isbn TEXT, title TEXT, borrower_id INTEGER, FOREIGN KEY(owner_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS requests (book_id INTEGER UNIQUE NOT NULL, user_id INTEGER NOT NULL, request_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, time INTEGER);")

from auth import auth
app.register_blueprint(auth)
from api import api
app.register_blueprint(api)
from books import books
app.register_blueprint(books)

@app.route("/")
@login_required
def index():
    user = session["user_id"]
    name = db.execute("SELECT username FROM users WHERE id = ?", user)[0][
        "username"
    ]
    book_count = len(db.execute("SELECT id FROM books"))
    user_count = len(db.execute("SELECT id FROM users"))
    user_books = len(db.execute("SELECT id FROM books WHERE owner_id = ?", user))
    user_takeouts = len(db.execute("SELECT request_id FROM requests WHERE user_id = ?", user))

    requested_books = db.execute("SELECT books.id, books.isbn, books.title, users.username FROM books INNER JOIN requests ON books.id = requests.book_id INNER JOIN users ON requests.user_id = users.id WHERE books.owner_id = ? AND books.borrower_id IS NULL", user)
    user_requests = db.execute("SELECT id, isbn, title FROM books WHERE borrower_id = ?", user)
    return render_template("index.html",
                           name=name, book_count=book_count, users=user_count, user_books=user_books, user_takeouts=user_takeouts, requested_books=requested_books, user_requests=user_requests
                           )