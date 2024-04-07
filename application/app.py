# Import Management
from cs50 import SQL
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Configure Application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure appication SQLite database with SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test-flex.db"
db = SQLAlchemy(app)

# CS50 SQL object for raw execution
cs50_db = SQL("sqlite:///test-flex.db")

# Define application routes
@app.route("/")
def index():
    """Application Homepage"""

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""

    session.clear()
    
    if request.method == "POST":
        if not request.form.get("username"):
            return("must provide username", 403)
        
        elif not request.form.get("password"):
            return("must provide password", 403)
        
        rows = cs50_db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return("invalid username or password", 403)
        
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        if not username:
            return("Username cannot be blank.")

        password = request.form.get("password")
        if not password:
            return("Password cannot be blank.")

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return("Please confirm password.")
        elif confirmation != password:
            return("Passwords do not match.")

        existing_user = cs50_db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            return("Username already exists.")

        hashed_password = generate_password_hash(password)

        cs50_db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)

        return render_template("login.html")

    return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/tests")
def tests():
    """View and build list of tests"""
    tests = cs50_db.execute("""
        SELECT t.*, u.username AS created_by_username
        FROM tests t
        JOIN users u ON t.user_id = u.id
    """)

    return render_template("tests.html", tests=tests)

@app.route("/add_test", methods=["POST"])
def add_test():
    """Retrieve and insert test data into database"""
    test_name = request.json.get('name')
    test_description = request.json.get('description')
    user_id = session.get('user_id')

    # Server-side Validations
    if not test_name:
        return jsonify({'error': 'Test name is required'}), 400
    
    if not test_description:
        return jsonify({'error': 'Test description is required'}), 400

    cs50_db.execute("INSERT INTO tests (name, description, user_id) VALUES (?, ?, ?)",
               test_name, test_description, user_id)
    
    return jsonify({'message': 'Test added successfully'})