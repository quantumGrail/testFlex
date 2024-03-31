# Import Management
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Configure Application
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test-flex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure appication SQLite database
db = SQLAlchemy(app)

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
        
        rows = db.execute(
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