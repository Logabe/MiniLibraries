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

from views.auth import auth
app.register_blueprint(auth)
from views.api import api
app.register_blueprint(api)
from views.books import books
app.register_blueprint(books)
import views