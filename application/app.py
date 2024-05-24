# Import Management
from cs50 import SQL
from datetime import datetime, timedelta
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from werkzeug.security import check_password_hash, generate_password_hash

# Configure Application
app = Flask(__name__, static_folder='templates/static')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# CS50 SQL object for raw execution
cs50_db = SQL("sqlite:///test-flex.db")

# Initialize Selenium for Chrome
def initialize_selenium():
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        return driver
    except Exception as e:
        print("Error initializing webdriver:", e)
        return None

# Define application routes
@app.route("/")
def index():
    """Application Homepage"""
    user_id = session.get('user_id')

    if not user_id:
        return redirect("/login")

    result = cs50_db.execute("SELECT username FROM users WHERE id = ?", user_id)

    if result:
        username = result[0]['username'].title()
    else:
        username = "Guest"

    transactions = cs50_db.execute("SELECT *, CASE WHEN trans_type = 0 THEN 'added' ELSE trans_type END AS trans_type_label FROM tests_transactions WHERE user = ?", user_id)

    num_tests = cs50_db.execute("SELECT COUNT(user_id) FROM tests WHERE user_id = ?", user_id)
    count = num_tests[0]['COUNT(user_id)']
    count_str = str(count)

    steps = cs50_db.execute("SELECT COUNT(*) AS step_count FROM test_steps WHERE test_id IN (SELECT id FROM tests WHERE user_id = ?)", user_id)
    step_count = steps[0]['step_count']
    step_str = str(step_count)

    # Get current date
    now = datetime.now()

    # Define date ranges for the past 3 months, current month, and next 3 months 
    # Credit: ChatGPT used for dynamic date formula
    date_ranges = [(now - timedelta(days=30 * i)).strftime('%Y-%m-01') for i in range(-3, 4)]

    # Initialize a dictionary to store the counts
    test_counts = {}

    for date in date_ranges:
        start_date = date
        # Credit: ChatGPT used for time formulas on end dates
        end_date = (datetime.strptime(date, '%Y-%m-01') + timedelta(days=31)).strftime('%Y-%m-01')
        count = cs50_db.execute("SELECT COUNT(*) AS count FROM tests WHERE user_id = ? AND created_at >= ? AND created_at < ?", user_id, start_date, end_date)
        month = datetime.strptime(date, '%Y-%m-01').strftime('%B')
        test_counts[month] = count[0]['count']

    # Convert test_counts values to a list of counts
    test_data = list(test_counts.values())
    test_labels = list(test_counts.keys())

    return render_template(
        "index.html",
        user_id=username,
        transactions=transactions,
        count_str=count_str,
        step_str=step_str,
        test_labels=test_labels,
        test_data=test_data
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""

    session.clear()
    
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("empty_credentials.html")
        
        elif not request.form.get("password"):
            return render_template("empty_credentials.html")
        
        rows = cs50_db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("invalid.html")
        
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
            return render_template("empty_credentials.html")

        password = request.form.get("password")
        if not password:
            return render_template("empty_credentials.html")

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return render_template("bad_password.html")
        elif confirmation != password:
            return render_template("bad_password.html")

        existing_user = cs50_db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            return render_template("reused_username.html")

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

    # Get the current user's ID from the session
    user_id = session.get('user_id')

    # Fetch tests created by the current user
    tests = cs50_db.execute("""
        SELECT t.*, u.username AS created_by_username
        FROM tests t
        JOIN users u ON t.user_id = u.id
        WHERE t.user_id = ?
    """, user_id)

    if not tests:
        return render_template("no_tests.html")

    # Fetch test steps for each test
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
        
        # Mark transaction as 0 to represent an add
        trans_type = 0

        cs50_db.execute("INSERT INTO tests_transactions (user, trans_type, name) VALUES (?, ?, ?)",
                user_id, trans_type, name)
    
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
        test_id = request.form.get("test_id")
    
        cs50_db.execute(
            "UPDATE test_steps SET action = ?, location = ?, result = ? WHERE id = ?",
            action, location, result, step_id
        )
        return redirect(f"/edit_test/{test_id}")