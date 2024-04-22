# Test Flex
Test Flex provides users with test case management and automation tools. 
Groups of users may work together to create manual and automated tests.
Tests may be left manual until user is ready to build a connected automation. 
Users may create and reuse named xpaths for common site locators. 
Expectations may be set for repeatable, predictable outcomes.

A provided syntax is in development for 'actions' such as:
- Click
- Type
- Route

# Commands
The following commands should only be run inside the application/ directory:
- flask run --starts development server
- sqlite3 test-flex.db --opens database interpreter

# Dependencies
Test Flex uses the following libraries to integrate HTML, JavaScript, Python, and SQL:
- CS50: ^9.3.4
- Flask: ^3.0.2
- Flask-Session: ^0.8.0
- Jinja2: ^3.1.3
- Selenium: ^4.19.0
- Webdriver-Manager: ^4.0.1
- Werkzeug: ^3.0.1

# Products
The following products are available in some version to users:
- Tests: allows users and groups to create test case libraries.
- Automation: allows tests to be automated in a partially-modular syntax.
