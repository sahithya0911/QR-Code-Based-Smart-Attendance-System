from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import qrcode as qr_module
import os
from database import init_db
from datetime import date, datetime

app = Flask(__name__)

init_db()

def get_db():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get date from filter or use today
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    cursor.execute('''
        SELECT students.name, students.roll_no, students.class_name, 
               attendance.time, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE attendance.date = ?
    ''', (selected_date,))
    records = cursor.fetchall()
    conn.close()
    return render_template('index.html', records=records, today=selected_date)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        class_name = request.form['class_name']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, roll_no, class_name)
            VALUES (?, ?, ?)
        ''', (name, roll_no, class_name))
        student_id = cursor.lastrowid
        conn.commit()

        qr_data = f"student_{student_id}_{roll_no}"
        qr = qr_module.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_path = f"static/qrcodes/{roll_no}.png"
        os.makedirs("static/qrcodes", exist_ok=True)
        img.save(qr_path)

        cursor.execute('UPDATE students SET qr_path = ? WHERE id = ?', (qr_path, student_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('register.html')

# ─── Sync to Google Sheets ───
@app.route('/sync')
def sync():
    from sheets import sync_to_sheets
    result = sync_to_sheets()
    if result:
        return redirect(url_for('index') + '?sync=success')
    else:
        return redirect(url_for('index') + '?sync=failed')

if __name__ == '__main__':
    app.run(debug=True)