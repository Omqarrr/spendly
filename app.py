from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import get_db, init_db, seed_db, register_user, get_user_by_email
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-random-key'


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in, redirect to profile
    if "user_id" in session:
        return redirect(url_for("profile"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        error = None

        # Basic validation
        if not name:
            error = "Name is required"
        elif not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"
        elif password != confirm_password:
            error = "Passwords do not match"
        # Simple email format validation
        elif "@" not in email or "." not in email.split("@")[-1]:
            error = "Invalid email format"

        if error is None:
            try:
                user_id = register_user(name, email, password)
                # Registration successful – redirect to login with success flag
                return redirect(url_for("login", registered="1"))
            except ValueError as e:
                error = str(e)

        # On any error, re‑render the form with the error message
        return render_template("register.html", error=error)

    # GET request – render empty registration form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to profile
    if "user_id" in session:
        return redirect(url_for("profile"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        error = None
        if not email or not password:
            error = "Invalid email or password."
        else:
            user = get_user_by_email(email)
            if user is None:
                error = "Invalid email or password."
            else:
                from werkzeug.security import check_password_hash
                if not check_password_hash(user["password_hash"], password):
                    error = "Invalid email or password."
        if error is None:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            return redirect(url_for("profile"))
        # Flash error and fall through to render template
        from flask import flash
        flash(error)
    # GET or POST with error
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    # Fetch user name for greeting
    user = get_user_by_email(session.get("email", ""))
    if user is None:
        # fallback if email not stored; just redirect to login
        return redirect(url_for("login"))
    return render_template("profile.html", name=user.get("name", "User"))


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    # Initialize and seed the database before starting the server
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)