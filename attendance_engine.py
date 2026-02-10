import cv2
import face_recognition
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import data_manager

class AttendanceEngine:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.grace_period_minutes = 10
        self.load_registered_faces()

    def load_registered_faces(self):
        """Loads images from faces/ folder and generates encodings."""
        self.known_face_encodings = []
        self.known_face_names = []
        
        faces_dir = 'faces'
        if not os.path.exists(faces_dir):
            return

        for student_name in os.listdir(faces_dir):
            student_path = os.path.join(faces_dir, student_name)
            if os.path.isdir(student_path):
                for img_name in os.listdir(student_path):
                    try:
                        img_path = os.path.join(student_path, img_name)
                        image = face_recognition.load_image_file(img_path)
                        encoding = face_recognition.face_encodings(image)[0]
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(student_name)
                    except Exception as e:
                        print(f"Error loading {img_name}: {e}")

    def get_current_slot(self):
        """Dynamic Timetable Logic: Maps current time to a lecture."""
        now = datetime.now()
        current_day = now.strftime('%A')
        current_time = now.time()

        timetable = data_manager.get_timetable()
        # Filter by day
        today_schedule = timetable[timetable['Day'] == current_day]

        for _, row in today_schedule.iterrows():
            start = datetime.strptime(row['Start_Time'], '%H:%M').time()
            end = datetime.strptime(row['End_Time'], '%H:%M').time()
            
            if start <= current_time <= end:
                return {
                    'subject': row['Subject'],
                    'start_time': row['Start_Time'],
                    'end_time': row['End_Time'],
                    'slot_str': f"{row['Start_Time']}-{row['End_Time']}"
                }
        return None

    def mark_absentees(self, slot_info):
        """Auto-Absent Logic: Marks registered students missing after grace period."""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        start_dt = datetime.strptime(f"{date_str} {slot_info['start_time']}", '%Y-%m-%d %H:%M')
        grace_limit = start_dt + timedelta(minutes=self.grace_period_minutes)

        # Check if grace period has passed
        if now > grace_limit:
            registered_students = data_manager.get_all_registered_students()
            attendance_df = data_manager.get_attendance_logs()
            
            # Find students not marked for this slot today
            marked_today = attendance_df[
                (attendance_df['Date'] == date_str) & 
                (attendance_df['Subject'] == slot_info['subject'])
            ]['Name'].tolist()

            for student in registered_students:
                if student not in marked_today:
                    data_manager.save_attendance({
                        'Name': student,
                        'Date': date_str,
                        'Day': now.strftime('%A'),
                        'Time': now.strftime('%H:%M:%S'),
                        'Slot': slot_info['slot_str'],
                        'Subject': slot_info['subject'],
                        'Status': 'Absent'
                    })

    def process_frame(self, frame):
        """Real-time Recognition and Attendance Trigger."""
        slot = self.get_current_slot()
        if not slot:
            return frame, "No active lecture slot found."

        # Scale down for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        start_dt = datetime.strptime(f"{date_str} {slot['start_time']}", '%Y-%m-%d %H:%M')
        grace_limit = start_dt + timedelta(minutes=self.grace_period_minutes)

        status_msg = f"Subject: {slot['subject']} | Slot: {slot['slot_str']}"

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]

                # Grace Period Check
                if now <= grace_limit:
                    # Prevent Duplicates
                    if not data_manager.check_duplicate(name, date_str, slot['subject']):
                        data_manager.save_attendance({
                            'Name': name,
                            'Date': date_str,
                            'Day': now.strftime('%A'),
                            'Time': now.strftime('%H:%M:%S'),
                            'Slot': slot['slot_str'],
                            'Subject': slot['subject'],
                            'Status': 'Present'
                        })
                else:
                    status_msg = "Grace period ended. No more attendance for this slot."

            # Snapshot for unknown faces
            if name == "Unknown":
                snap_path = f"unknown_faces/unknown_{now.strftime('%H%M%S')}.jpg"
                cv2.imwrite(snap_path, frame)

            # Draw UI
            top *= 4; right *= 4; bottom *= 4; left *= 4
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Trigger auto-absent if needed
        self.mark_absentees(slot)

        return frame, status_msg
