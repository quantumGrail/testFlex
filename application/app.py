# Import Management
from flask import Flask, redirect, render_template, session
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

@app.route("/")
def index():
    """Application Homepage"""

    return render_template("index.html")