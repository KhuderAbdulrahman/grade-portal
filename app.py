from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'
DB_NAME = 'students.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'excel_file' not in request.files:
        flash("يرجى اختيار ملف Excel")
        return redirect('/admin_login')

    file = request.files['excel_file']
    if file.filename == '':
        flash("اسم الملف غير صالح")
        return redirect('/admin_login')

    df = pd.read_excel(file)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS students")
    columns = df.columns.tolist()
    sql_cols = [f'"{col}" TEXT' for col in columns]
    c.execute(f'CREATE TABLE students ({", ".join(sql_cols)})')
    for _, row in df.iterrows():
        values = tuple(str(val) for val in row)
        placeholders = ','.join('?' * len(values))
        c.execute(f'INSERT INTO students VALUES ({placeholders})', values)
    conn.commit()
    conn.close()
    flash("تم تحميل البيانات بنجاح")
    return redirect('/admin_login')

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        return render_template('student_login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        query = 'SELECT * FROM students WHERE "اسم المستخدم"=? AND "كلمة المرور"=?'
        c.execute(query, (username, password))
        row = c.fetchone()
        conn.close()
        if row:
            student = dict(row)
            grades = {k: v for k, v in student.items() if k not in ["الاسم", "اسم المستخدم", "كلمة المرور"]}
            return render_template("student_result.html", student=student, grades=grades)
        else:
            flash("بيانات الدخول غير صحيحة")
            return redirect('/student_login')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))