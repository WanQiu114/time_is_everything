import psutil
import pygetwindow as gw
from pywinauto import Application
from datetime import datetime, timedelta  # Correctly import timedelta
import time
import requests
import json
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import atexit
from time_is_everything import add_event_to_calendar, get_google_calendar_service

# Global variable to store activity logs
activity_log = []

# Google Calendar API scopes




def get_maximized_app():
    try:
        current_window = gw.getActiveWindow()
        if current_window and current_window.isMaximized:
            app = Application().connect(handle=current_window._hWnd)
            process_id = app.process
            process = psutil.Process(process_id)
            return current_window.title, process.name()
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def get_chrome_tab_title():
    try:
        response = requests.get('http://localhost:9222/json')
        tabs = json.loads(response.text)
        if tabs:
            return tabs[0]['title']
        else:
            return "No active tabs"
    except Exception as e:
        print(f"Error fetching Chrome title: {e}")
        return "Unknown Chrome Tab"

def get_firefox_tab_title():
    # Simulated return for Firefox; replace with actual MozRepl integration if needed
    return "Simulated Firefox Tab"

def detect_browser_title(process_name):
    if 'chrome' in process_name.lower():
        return get_chrome_tab_title()
    elif 'firefox' in process_name.lower():
        return get_firefox_tab_title()
    else:
        return None

def upload_to_google_calendar():
    service = get_google_calendar_service()
    if activity_log:
        for app_name, start_time, end_time, duration in activity_log:
            add_event_to_calendar(service, app_name, start_time, end_time)
        print("All activities have been uploaded to Google Calendar.")
    else:
        print("No activities to upload.")

def monitor_fullscreen_apps():
    global activity_log
    current_app = None
    start_time = None
    accumulated_time = timedelta()  # To store accumulated time on the same title

    while True:
        app_title, process_name = get_maximized_app()

        if process_name:
            browser_tab_title = detect_browser_title(process_name)
            if browser_tab_title:
                app_title = browser_tab_title
            
            if app_title != current_app:
                if current_app:
                    # End time for the previous app
                    end_time = datetime.now()
                    # Calculate the total time spent
                    total_duration = accumulated_time + (end_time - start_time)
                    print(f"{current_app} ran for {total_duration} time.")
                    activity_log.append((current_app, start_time, end_time, total_duration))

                # Start tracking the new application
                current_app = app_title
                start_time = datetime.now()
                accumulated_time = timedelta()  # Reset accumulated time for new app
                print(f"Current application: {current_app}, started at: {start_time}")
            else:
                # If the same app is still running, keep accumulating time
                accumulated_time += timedelta(seconds=5)  # Increment accumulated time

        time.sleep(5)

# Register the upload function to run on exit
atexit.register(upload_to_google_calendar)

if __name__ == "__main__":
    try:
        monitor_fullscreen_apps()
    except KeyboardInterrupt:
        print("Monitoring stopped. Uploading data to Google Calendar...")
