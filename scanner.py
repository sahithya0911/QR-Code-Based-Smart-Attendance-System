import cv2
import sqlite3
from datetime import date, datetime

def get_db():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

def mark_attendance(student_id):
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    time_now = datetime.now().strftime('%H:%M:%S')

    cursor.execute('''
        SELECT * FROM attendance 
        WHERE student_id = ? AND date = ?
    ''', (student_id, today))
    
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "already_marked"
    else:
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
        ''', (student_id, today, time_now, 'Present'))
        conn.commit()
        conn.close()
        return "success"

def start_scanner():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    
    print("Scanner started! Show QR code to camera...")
    print("Press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect QR code
        data, bbox, _ = detector.detectAndDecode(frame)

        if data:
            print(f"QR Detected: {data}")
            parts = data.split('_')
            if len(parts) >= 2:
                student_id = parts[1]
                result = mark_attendance(student_id)

                if result == "success":
                    print(f"✅ Attendance marked!")
                    cv2.putText(frame, "PRESENT!", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    print(f"❌ Already marked!")
                    cv2.putText(frame, "ALREADY MARKED!", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("QR Scanner - Press Q to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_scanner()