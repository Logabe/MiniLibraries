from .app import app

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Return a version of the page with an error message
        def error(error):
            nonlocal username
            nonlocal password
            return render_template("register.html", username=username, password=password, error=error)

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return error("Empty username")

        if not password:
            return error("Empty password")

        if len(db.execute("SELECT id FROM users WHERE username = ?", username)) != 0:
            return error("Username already in use")

        if password != confirmation:
            return error("Password and confirmation do not match")

        hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
        )

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Return a version of the page with an error message
        def error(error):
            nonlocal username
            nonlocal password
            return render_template("login.html", username=username, password=password, error=error)

        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            return error("must provide username")

        # Ensure password was submitted
        elif not password:
            return error("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            return error("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
