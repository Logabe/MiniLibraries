from flask import Blueprint, redirect, render_template, session, url_for

from app import db
from helpers import login_required
import requests


books = Blueprint('books', __name__, url_prefix='/books')

@books.route("/")
@login_required
def books_listing():
    books = db.execute("SELECT id, isbn, title, borrower_id FROM books")

    return render_template("books.html", books=books)

@books.route("/<string:book_id>")
@login_required
def book_details(book_id):
    details = db.execute("SELECT * FROM books WHERE id = ?", book_id)
    if not details:
        return redirect(url_for('books.book_listing'))
    details = details[0]
    request = db.execute("SELECT request_id FROM requests WHERE book_id = ?", book_id)
    has_book = details["borrower_id"] == session["user_id"]
    is_owner = details["owner_id"] == session["user_id"]

    olid = details["olid"]

    book = requests.get(f'http://openlibrary.org/books/{olid}.json').json()
    work_id = book["works"][0]["key"]

    work = requests.get(f'http://openlibrary.org{work_id}.json').json()
    desc = work.get("description")
    text = []
    if desc:
        desc = desc["value"]
        text = desc.split('\n')

    return render_template("book_details.html", id=book_id, olid=olid, title=details["title"], subtitle=book.get("subtitle"), description=text, request=request, has_book=has_book, is_owner=is_owner)