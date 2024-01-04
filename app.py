from __future__ import print_function
from datetime import datetime
import sys

from cs50 import SQL
from flask import Flask, render_template, redirect, request, session, url_for, make_response
from flask_session import Session
import requests
from werkzeug.security import check_password_hash, generate_password_hash

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

@app.route("/books")
@login_required
def books():
    books = db.execute("SELECT id, isbn, title, borrower_id FROM books")

    return render_template("books.html", books=books)

@app.route("/api/book/add", methods=["POST"])
@login_required
def add_book():
    owner_id = session["user_id"]
    isbn = request.form.get("isbn")

    if len(isbn) != 13 and len(isbn) != 10:
        return "The ISBN provided is the wrong length (should be either 10 or 13)"

    r = requests.get(f'http://openlibrary.org/api/volumes/brief/isbn/{isbn}.json')
    book = r.json()["records"][list(r.json()["records"])[0]]
    print(book, file=sys.stderr)
    olid = book["olids"][0]
    title = book["data"]["title"]

    db.execute("INSERT INTO books (owner_id, olid, isbn, title) VALUES (?, ?, ?, ?)", owner_id, olid, isbn, title )

    return redirect(url_for("books"))

@app.route("/api/book/delete", methods=["POST"])
@login_required
def delete_book():
    owner_id = session["user_id"]
    book_id = request.form.get("book_id")

    if len(db.execute("SELECT id FROM books WHERE id = ? AND owner_id = ?", book_id, owner_id)) != 0:
        db.execute("DELETE FROM books WHERE id = ? AND owner_id = ?", book_id, owner_id)
        db.execute("DELETE FROM requests WHERE book_id = ?", book_id)

    return redirect(url_for("books"))

@app.route("/api/book/request", methods=["POST"])
@login_required
def request_book():
    values = {
        "book_id": request.form.get("book_id"),
        "user_id": session["user_id"],
        "time": datetime.now()
    }

    db.execute("INSERT INTO requests (book_id, user_id, time) VALUES (?, ?, ?)", *values.values())
    return values

@app.route("/api/book/cancel_request", methods=["POST"])
@login_required
def cancel_request():
    book_id = request.form.get("book_id")
    db.execute("DELETE FROM requests WHERE user_id = ? AND book_id = ?", session["user_id"], book_id)
    return redirect(url_for("book_details", book_id=book_id))

@app.route("/api/book/fulfill_request", methods=["POST"])
@login_required
def fulfill_request():
    book_id = request.form.get("book_id")
    user_id = session["user_id"]
    db.execute("DELETE FROM requests WHERE user_id = ? AND book_id = ?", user_id, book_id)
    db.execute("UPDATE books SET borrower_id = ? WHERE id = ?", user_id, book_id)
    return make_response(None, 204)

@app.route("/api/book/return", methods=["POST"])
@login_required
def return_book():
    db.execute("UPDATE books SET borrower_id = NULL WHERE id = ? AND borrower_id = ?", request.form.get("book_id"), session["user_id"])
    return redirect("/")

@app.route("/books/<string:book_id>")
@login_required
def book_details(book_id):
    details = db.execute("SELECT * FROM books WHERE id = ?", book_id)
    if not details:
        return redirect("/books")
    details = details[0]
    request = db.execute("SELECT request_id FROM requests WHERE book_id = ?", book_id)
    has_book = details["borrower_id"] == session["user_id"]
    is_owner = details["owner_id"] == session["user_id"]

    olid = details["olid"]

    r = requests.get(f'http://openlibrary.org/books/{olid}.json')
    book = r.json()
    work_id = book["works"][0]["key"]

    work = requests.get(f'http://openlibrary.org{work_id}.json').json()
    desc = work.get("description")
    text = []
    if desc:
        desc = desc["value"]
        text = desc.split('\n')

    return render_template("book_details.html", id=book_id, olid=olid, title=details["title"], subtitle=book.get("subtitle"), description=text, request=request, has_book=has_book, is_owner=is_owner)