# Import Management
from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure Application
app = Flask(__name__, static_folder='templates/static')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

    for test in tests:
        test['steps'] = cs50_db.execute("""
            SELECT * FROM test_steps WHERE test_id = ?
            """, test['id'])

    return render_template("tests.html", tests=tests)

@app.route("/add_test", methods=["POST", "GET"])
def add_test():
    """Retrieve and insert test data into database"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        user_id = session.get('user_id')

        # Server-side Validations
        if not name:
            return jsonify({'error': 'Test name is required'}), 400
    
        if not description:
            return jsonify({'error': 'Test description is required'}), 400

        cs50_db.execute("INSERT INTO tests (name, description, user_id) VALUES (?, ?, ?)",
               name, description, user_id)
    
        return redirect("/tests")
    
    else:
        return render_template("add_test.html")


@app.route("/edit_test/<int:test_id>", methods=["GET", "POST"])
def edit_test(test_id):
    """Edit test detail and step"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        cs50_db.execute(
            "UPDATE tests SET name = ?, description = ? WHERE id = ?",
            name, description, test_id
        )

        # Add new test step, if data is present 
        if request.form.get("action") and request.form.get("location") and request.form.get("result"):
            action = request.form.get("action")
            location = request.form.get("location")
            result = request.form.get("result")
            cs50_db.execute(
                "INSERT INTO test_steps (test_id, action, location, result) VALUES (?, ?, ?, ?)",
                (test_id, action, location, result)
            )

            return redirect("/tests")
    
    else:
        test = cs50_db.execute(
            "SELECT * FROM tests WHERE id = ?", test_id
        )

        if not test:
            return jsonify({'error': 'Test not found'}), 400
        
        test_steps = cs50_db.execute(
            "SELECT * FROM test_steps WHERE test_id = ?", test_id
        )
    
        return render_template("edit_test.html", test=test[0], test_steps=test_steps)
   
@app.route("/delete_test/<int:test_id>", methods=["POST"])
def delete_test(test_id):
    """Delete Test"""
    cs50_db.execute(
        "DELETE FROM tests WHERE id = ?", test_id
    )
    return redirect("/tests")

@app.route("/automation", methods=["GET", "POST"])
def automation():
    """View and configure automation settings"""

    return render_template("automation.html")

@app.route("/results", methods=["GET", "POST"])
def results():
    """View and report on test runs"""

    return render_template("results.html")

@app.route("/add_step", methods=["POST"])
def add_step():
    """Add a step to a test"""

    action = request.form.get("action")
    location = request.form.get("location")
    result = request.form.get("result")
    test_id = request.form.get("test_id")

    # Server-side Validations
    if not action:
        return jsonify({'error': 'Test action is required'}), 400
    
    if not test_id:
        return jsonify({'error': 'Faileed to find related test'}), 400

    cs50_db.execute(
        "INSERT INTO test_steps (action, location, result, test_id) VALUES (?, ?, ?, ?)",
        action, location, result, test_id)
    
    return redirect(f"/edit_test/{test_id}")

@app.route("/edit_step/<int:step_id>", methods=["POST"])
def edit_step(step_id):
    """Edit a test step"""
    if request.method == "POST":
        action = request.form.get("action")
        location = request.form.get("location")
        result = request.form.get("result")
    
        cs50_db.execute(
            "UPDATE test_steps SET action = ?, location = ?, result = ? WHERE id = ?",
            action, location, result, step_id
        )
        return redirect("/tests")