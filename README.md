# BankSphere — Banking Management & Transaction Analysis Website

A local portfolio web application built with Python Flask, MySQL, HTML, CSS and JavaScript-free server-rendered pages. It connects to the existing `banking_management` MySQL database.

## Features
- Dashboard totals and recent transaction records
- Customer directory with search
- Add customer form
- Account directory
- Transaction history
- Fraud alert review

## Requirements
- Python 3.10+
- MySQL 8+
- VS Code (recommended)

## 1. Check your MySQL database
Open MySQL Workbench and run:
```sql
USE banking_management;
SHOW TABLES;
```
The app expects the tables and columns from the SQL project:
`customers`, `branches`, `accounts`, `transactions`, `fraud_alerts`.

## 2. Open in VS Code
Extract this ZIP, then in VS Code choose **File → Open Folder** and select `banking_management_website`.

## 3. Create and activate a virtual environment
Windows PowerShell:
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```
If PowerShell blocks activation, use Command Prompt:
```bat
.venv\\Scripts\\activate.bat
```

## 4. Install packages
```bash
python -m pip install -r requirements.txt
```

## 5. Configure MySQL password
Set environment variables in the VS Code terminal (PowerShell example):
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="YOUR_MYSQL_PASSWORD"
$env:DB_NAME="banking_management"
$env:FLASK_SECRET_KEY="change-this-local-secret"
```
Replace `YOUR_MYSQL_PASSWORD` with the password for your local MySQL user. If your MySQL root account has no password, use an empty string.

## 6. Run the website
```bash
python app.py
```
Open this address in your browser:
http://127.0.0.1:5000

Stop the server with `Ctrl + C` in the terminal.

## Troubleshooting
- **Access denied**: check `DB_USER` and `DB_PASSWORD`.
- **Unknown database**: run `CREATE DATABASE banking_management;` and create/import your tables.
- **Table doesn't exist**: check `SHOW TABLES;` in the selected database.
- **Can't connect to MySQL server**: start the MySQL server/service.
- **Module not found**: activate `.venv`, then run `python -m pip install -r requirements.txt`.

## Important limitations
This is a portfolio/demo application, not real online banking software. It has no login/authentication, authorization, CSRF protection, production deployment hardening, or secure payment processing. Use fictional data only. Do not connect real customer or financial data. The displayed total is the sum of stored account balances, not a reconciled ledger.
