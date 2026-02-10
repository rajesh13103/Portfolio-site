from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
import cv2
import pandas as pd
import os
from attendance_engine import AttendanceEngine
import data_manager

app = Flask(__name__)
app.secret_key = "attendance_secret_key_123"

# Initialize databases and folders
data_manager.initialize_db()
engine = AttendanceEngine()

def gen_frames():
    camera = cv2.VideoCapture(0) # Use 0 for webcam or "rtsp://..."
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Process recognition
            processed_frame, status_text = engine.process_frame(frame)
            
            # Overlay status text on video
            cv2.putText(processed_frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    users = pd.read_excel('users.xlsx')
    user_row = users[(users['username'] == username) & (users['password'] == password)]
    
    if not user_row.empty:
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid Credentials!')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    logs = data_manager.get_attendance_logs()
    # Summary stats
    present_count = len(logs[logs['Status'] == 'Present'])
    absent_count = len(logs[logs['Status'] == 'Absent'])
    return render_template('dashboard.html', p_count=present_count, a_count=absent_count)

@app.route('/video_feed')
def video_feed():
    if 'user' not in session: return "Unauthorized"
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera')
def camera_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('camera.html')

@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    if 'user' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save('timetable.xlsx')
            flash('Timetable updated successfully!')
    
    df = data_manager.get_timetable()
    return render_template('timetable.html', timetable=df.to_dict('records'))

@app.route('/report')
def report():
    if 'user' not in session: return redirect(url_for('login'))
    logs = data_manager.get_attendance_logs()
    
    # Generate student-wise summary
    summary = []
    students = data_manager.get_all_registered_students()
    for s in students:
        s_logs = logs[logs['Name'] == s]
        total = len(s_logs)
        present = len(s_logs[s_logs['Status'] == 'Present'])
        percent = (present / total * 100) if total > 0 else 0
        summary.append({
            'name': s,
            'total': total,
            'present': present,
            'percent': f"{percent:.2f}%"
        })
        
    return render_template('report.html', logs=logs.to_dict('records'), summary=summary)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
