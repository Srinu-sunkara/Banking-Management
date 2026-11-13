import os
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-for-local-development")

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Srinu@123"),
        database=os.getenv("DB_NAME", "banking_management"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

def fetch_all(sql, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def fetch_one(sql, params=()):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@app.route("/")
def dashboard():
    try:
        stats = fetch_one("""
            SELECT
              (SELECT COUNT(*) FROM customers) AS customers,
              (SELECT COUNT(*) FROM accounts) AS accounts,
              (SELECT COALESCE(SUM(balance), 0) FROM accounts) AS total_balance,
              (SELECT COUNT(*) FROM transactions
                WHERE DATE(transaction_date) = CURDATE()) AS today_transactions
        """)
        recent = fetch_all("""
            SELECT t.transaction_id, t.transaction_type, t.amount,
                   t.transaction_status, t.transaction_date,
                   a.account_number, c.first_name, c.last_name
            FROM transactions t
            JOIN accounts a ON a.account_id = t.account_id
            JOIN customers c ON c.customer_id = a.customer_id
            ORDER BY t.transaction_date DESC
            LIMIT 8
        """)
        return render_template("dashboard.html", stats=stats, recent=recent)
    except Error as e:
        return render_template("error.html", message=str(e)), 500

@app.route("/customers")
def customers():
    search = request.args.get("q", "").strip()
    try:
        rows = fetch_all("""
            SELECT c.customer_id, c.first_name, c.last_name, c.email,
                   c.phone, c.city, COUNT(a.account_id) AS account_count
            FROM customers c
            LEFT JOIN accounts a ON a.customer_id = c.customer_id
            WHERE (%s = '' OR CONCAT(c.first_name, ' ', c.last_name) LIKE %s
                   OR c.email LIKE %s OR c.phone LIKE %s)
            GROUP BY c.customer_id, c.first_name, c.last_name,
                     c.email, c.phone, c.city
            ORDER BY c.customer_id
        """, (search, f"%{search}%", f"%{search}%", f"%{search}%"))
        return render_template("customers.html", customers=rows, search=search)
    except Error as e:
        return render_template("error.html", message=str(e)), 500

@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        fields = ("first_name", "last_name", "email", "phone", "date_of_birth",
                  "gender", "city", "address")
        values = [request.form.get(field, "").strip() or None for field in fields]
        if not values[0] or not values[1]:
            flash("First name and last name are required.", "error")
            return render_template("customer_form.html")
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers
                (first_name,last_name,email,phone,date_of_birth,gender,city,address)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, values)
            conn.commit()
            flash("Customer added successfully.", "success")
            return redirect(url_for("customers"))
        except Error as e:
            conn.rollback()
            flash(f"Could not add customer: {e}", "error")
        finally:
            cursor.close()
            conn.close()
    return render_template("customer_form.html")

@app.route("/accounts")
def accounts():
    try:
        rows = fetch_all("""
            SELECT a.account_id, a.account_number, a.account_type, a.balance,
                   a.account_status, a.opening_date,
                   CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
                   b.branch_name
            FROM accounts a
            JOIN customers c ON c.customer_id = a.customer_id
            JOIN branches b ON b.branch_id = a.branch_id
            ORDER BY a.account_id
        """)
        return render_template("accounts.html", accounts=rows)
    except Error as e:
        return render_template("error.html", message=str(e)), 500

@app.route("/transactions")
def transactions():
    try:
        rows = fetch_all("""
            SELECT t.transaction_id, t.transaction_type, t.amount,
                   t.transaction_status, t.transaction_date, t.description,
                   a.account_number, CONCAT(c.first_name, ' ', c.last_name) AS customer_name
            FROM transactions t
            JOIN accounts a ON a.account_id = t.account_id
            JOIN customers c ON c.customer_id = a.customer_id
            ORDER BY t.transaction_date DESC
            LIMIT 200
        """)
        return render_template("transactions.html", transactions=rows)
    except Error as e:
        return render_template("error.html", message=str(e)), 500

@app.route("/fraud-alerts")
def fraud_alerts():
    try:
        rows = fetch_all("""
            SELECT f.alert_id, f.alert_type, f.alert_description, f.alert_date,
                   f.alert_status, a.account_number,
                   CONCAT(c.first_name, ' ', c.last_name) AS customer_name
            FROM fraud_alerts f
            JOIN accounts a ON a.account_id = f.account_id
            JOIN customers c ON c.customer_id = a.customer_id
            ORDER BY f.alert_date DESC
        """)
        return render_template("fraud_alerts.html", alerts=rows)
    except Error as e:
        return render_template("error.html", message=str(e)), 500

@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", message="The page you requested was not found."), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
