from datetime import datetime
import sys

from flask import Blueprint, redirect, request, session, url_for, make_response
import requests

from app import db
from helpers import login_required

api = Blueprint('api', __name__, url_prefix='/api/book')

@api.route("/add", methods=["POST"])
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

@api.route("/delete", methods=["POST"])
@login_required
def delete_book():
    owner_id = session["user_id"]
    book_id = request.form.get("book_id")

    if len(db.execute("SELECT id FROM books WHERE id = ? AND owner_id = ?", book_id, owner_id)) != 0:
        db.execute("DELETE FROM books WHERE id = ? AND owner_id = ?", book_id, owner_id)
        db.execute("DELETE FROM requests WHERE book_id = ?", book_id)

    return redirect(url_for("books"))

@api.route("/request", methods=["POST"])
@login_required
def request_book():
    values = {
        "book_id": request.form.get("book_id"),
        "user_id": session["user_id"],
        "time": datetime.now()
    }

    db.execute("INSERT INTO requests (book_id, user_id, time) VALUES (?, ?, ?)", *values.values())
    return values

@api.route("/cancel_request", methods=["POST"])
@login_required
def cancel_request():
    book_id = request.form.get("book_id")
    db.execute("DELETE FROM requests WHERE user_id = ? AND book_id = ?", session["user_id"], book_id)
    return redirect(url_for("book_details", book_id=book_id))

@api.route("/fulfill_request", methods=["POST"])
@login_required
def fulfill_request():
    book_id = request.form.get("book_id")
    user_id = session["user_id"]
    db.execute("DELETE FROM requests WHERE user_id = ? AND book_id = ?", user_id, book_id)
    db.execute("UPDATE books SET borrower_id = ? WHERE id = ?", user_id, book_id)
    return make_response(None, 204)

@api.route("/return", methods=["POST"])
@login_required
def return_book():
    db.execute("UPDATE books SET borrower_id = NULL WHERE id = ? AND borrower_id = ?", request.form.get("book_id"), session["user_id"])
    return redirect("/")