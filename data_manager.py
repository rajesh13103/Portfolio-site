import pandas as pd
import os
from datetime import datetime

# Initialize the Excel files if they don't exist
def initialize_db():
    # 1. Attendance File
    if not os.path.exists('attendance.xlsx'):
        df = pd.DataFrame(columns=['Name', 'Date', 'Day', 'Time', 'Slot', 'Subject', 'Status'])
        df.to_excel('attendance.xlsx', index=False)
    
    # 2. Timetable File (Sample)
    if not os.path.exists('timetable.xlsx'):
        data = {
            'Day': ['Monday', 'Monday', 'Tuesday', 'Tuesday', 'Wednesday'],
            'Start_Time': ['09:00', '10:00', '09:00', '11:00', '14:00'],
            'End_Time': ['10:00', '11:00', '10:00', '12:00', '15:30'],
            'Subject': ['Mathematics', 'Physics', 'Digital Electronics', 'Microprocessors', 'Project Lab']
        }
        pd.DataFrame(data).to_excel('timetable.xlsx', index=False)

    # 3. Users File
    if not os.path.exists('users.xlsx'):
        pd.DataFrame([{'username': 'admin', 'password': 'admin123'}]).to_excel('users.xlsx', index=False)

    # 4. Folders
    if not os.path.exists('faces'): os.makedirs('faces')
    if not os.path.exists('unknown_faces'): os.makedirs('unknown_faces')

def get_timetable():
    return pd.read_excel('timetable.xlsx')

def get_attendance_logs():
    return pd.read_excel('attendance.xlsx')

def save_attendance(entry_dict):
    df = pd.read_excel('attendance.xlsx')
    new_row = pd.DataFrame([entry_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel('attendance.xlsx', index=False)

def check_duplicate(name, date, subject):
    df = pd.read_excel('attendance.xlsx')
    exists = df[(df['Name'] == name) & (df['Date'] == date) & (df['Subject'] == subject)]
    return not exists.empty

def get_all_registered_students():
    return [d for d in os.listdir('faces') if os.path.isdir(os.path.join('faces', d))]
