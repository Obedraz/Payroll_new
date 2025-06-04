import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)

DATABASE = 'payroll.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # To access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                rate REAL NOT NULL
            )
        ''')
        db.commit()

@app.route('/')
def home():
    return redirect(url_for('employee_list'))

@app.route('/employees')
def employee_list():
    db = get_db()
    cursor = db.execute('SELECT * FROM employees')
    employees = cursor.fetchall()
    return render_template('employees.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        rate = float(request.form['rate'])

        db = get_db()
        db.execute('INSERT INTO employees (name, position, rate) VALUES (?, ?, ?)', (name, position, rate))
        db.commit()

        return redirect(url_for('employee_list'))
    return render_template('add_employee.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate_salary():
    salary = None
    error = None
    if request.method == 'POST':
        try:
            emp_id = int(request.form['emp_id'])
            hours = float(request.form['hours'])
            db = get_db()
            cursor = db.execute('SELECT rate FROM employees WHERE id = ?', (emp_id,))
            employee = cursor.fetchone()
            if employee:
                rate = employee['rate']
                salary = rate * hours
            else:
                error = "Employee ID not found."
        except ValueError:
            error = "Invalid input."
    return render_template('calculate.html', salary=salary, error=error)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
