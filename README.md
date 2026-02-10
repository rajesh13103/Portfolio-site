# Face Recognition Attendance System (Academic Edition)

A production-ready Final Year Engineering Project implementation. This system uses real-time computer vision to automate student attendance based on a dynamic Excel timetable.

## Core Features
1.  **Face Recognition**: Powered by dlib/face_recognition for high accuracy.
2.  **Dynamic Timetable**: Automatically maps current time to subjects via `timetable.xlsx`.
3.  **Grace Period Logic**: Attendance is only marked as "Present" if the student is detected within the first 10 minutes of the lecture.
4.  **Auto-Absent System**: Students not detected within the grace period are automatically marked "Absent" in the Excel records.
5.  **Duplicate Prevention**: Ensures a student is marked only once per slot.
6.  **Excel Database**: No SQL setup required; uses `pandas` for handling attendance and user data.
7.  **Admin Dashboard**: Secure login to view live feeds, manage timetables, and generate reports.

## Prerequisites
- Python 3.8 or 3.9 (Recommended)
- C++ Compiler (Required for `dlib`). 
    - Windows: Install "Desktop Development with C++" via Visual Studio Installer.
    - Linux: `sudo apt-get install cmake build-essential libboost-all-dev`

## Installation

1. Clone or extract the project folder.
2. Open a terminal in the project directory.
3. Install dependencies:
    pip install -r requirements.txt

## Setup Instructions

1.  **Register Students**:
    - Go to the `faces/` directory.
    - Create a folder named after the student (e.g., `Amit_Kumar`).
    - Place 2-3 clear JPG/PNG images of that student inside their folder.
2.  **Timetable**:
    - The system comes with a default `timetable.xlsx`.
    - You can edit it directly or upload a new one via the Admin Dashboard.
    - Format: `Day | Start_Time (HH:MM) | End_Time (HH:MM) | Subject`.

## Running the Application

1. Start the server:
    python app.py
2. Open your browser and navigate to: `http://127.0.0.1:5000`
3. Login Credentials:
    - **Username**: `admin`
    - **Password**: `admin123`

## Technical Logic Explained

-   **Timetable Mapping**: On every frame, `attendance_engine.py` checks `datetime.now()` against the loaded Excel timetable to find the active "Subject".
-   **Grace Period**: Inside `process_frame`, a `grace_limit` is calculated. If `current_time > start_time + 10 mins`, the status switches to "Locked".
-   **Auto-Absent**: Once the grace period expires, the system identifies all registered folders in `faces/` that haven't been logged for the current slot and marks them "Absent".
-   **Storage**: `data_manager.py` uses `pandas` with the `openpyxl` engine to append rows to `attendance.xlsx`.

## Troubleshooting
- **Camera not opening**: Ensure no other app (Zoom, Teams) is using the webcam.
- **Dlib error**: Ensure you have installed Visual Studio C++ build tools.
- **Slow Frame Rate**: Face recognition is CPU intensive. The system is optimized to process every frame at 0.25x scale.
