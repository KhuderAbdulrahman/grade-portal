
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# قاعدة البيانات
DATABASE = 'students.db'

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة دخول الطالب
@app.route('/student_login', methods=['POST'])
def student_login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    query = 'SELECT * FROM students WHERE "اسم المستخدم"=? AND "كلمة المرور"=?'
    cursor.execute(query, (username, password))
    student = cursor.fetchone()
    conn.close()

    if student:
        name = student[0]
        subjects = student[3:]
        subject_names = get_subject_names()
        return render_template('student_result.html', name=name, subjects=zip(subject_names, subjects))
    else:
        return render_template('index.html', error='اسم المستخدم أو كلمة المرور غير صحيح')

# رفع ملف Excel وتحديث قاعدة البيانات
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        df = pd.read_excel(file)
        conn = sqlite3.connect(DATABASE)
        df.to_sql('students', conn, if_exists='replace', index=False)
        conn.close()
        return render_template('admin.html', message='تم تحميل البيانات بنجاح')
    return render_template('admin.html', message='فشل في تحميل الملف')

# صفحة دخول المشرف
@app.route('/admin')
def admin():
    return render_template('admin.html')

# دالة للحصول على أسماء المواد من قاعدة البيانات
def get_subject_names():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(students)')
    columns = cursor.fetchall()
    conn.close()
    return [col[1] for col in columns[3:]]

# ✅ التعديل هنا للتوافق مع Railway أو Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
