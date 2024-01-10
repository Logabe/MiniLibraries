from flask import render_template, session

from app import app, db
from helpers import login_required

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
    user_requests = len(db.execute("SELECT request_id FROM requests WHERE user_id = ?", user))

    requested_books = db.execute("SELECT books.id, books.isbn, books.title, users.username FROM books INNER JOIN requests ON books.id = requests.book_id INNER JOIN users ON requests.user_id = users.id WHERE books.owner_id = ? AND books.borrower_id IS NULL", user)
    user_takeouts = db.execute("SELECT id, isbn, title FROM books WHERE borrower_id = ?", user)
    return render_template("index.html",
                           name=name, book_count=book_count, users=user_count, user_books=user_books, user_takeouts=user_takeouts, requested_books=requested_books, user_requests=user_requests
                           )