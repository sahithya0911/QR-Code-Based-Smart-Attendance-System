import gspread
from google.oauth2.service_account import Credentials
import sqlite3
from datetime import date

# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SHEET_ID = '1xA52_QFXk9IRac3FgUcoGNvckrDYGWo-8ecizY8ZTJ4'
CREDENTIALS_FILE = 'credentials.json'

def get_sheet():
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet

def sync_to_sheets():
    try:
        sheet = get_sheet()

        # Clear existing data
        sheet.clear()

        # Add headers
        sheet.append_row(['Name', 'Roll No', 'Class', 'Date', 'Time', 'Status'])

        # Get data from SQLite
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT students.name, students.roll_no, students.class_name,
                   attendance.date, attendance.time, attendance.status
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            ORDER BY attendance.date DESC
        ''')
        records = cursor.fetchall()
        conn.close()

        # Push to Google Sheets
        for record in records:
            sheet.append_row(list(record))

        print(f"✅ Synced {len(records)} records to Google Sheets!")
        return True

    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return False

if __name__ == "__main__":
    sync_to_sheets()