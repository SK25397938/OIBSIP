import os
import time
import threading
from AppOpener import open as app_open, close as app_close, mklist
import voice
import datetime
import pyautogui
import screen_brightness_control as sbc
import webbrowser
import wikipedia
import pywhatkit
import requests 

def open_app(app_name: str):
    """Opens an app (e.g., 'spotify', 'chrome')."""
    if not os.path.exists("app_data.json"):
        mklist(name="app_data.json")
    try:
        app_open(app_name, match_closest=True, output=False)
        return f"Opening {app_name}..."
    except Exception as e:
        return f"Error opening {app_name}: {e}"

def close_app(app_name: str):
    """
    Closes an application.
    Args: app_name (str) - The name of the app to close.
    """
    try:
        app_close(app_name, match_closest=True, output=False)
        return f"Closing {app_name}..."
    except Exception as e:
        return f"Could not close {app_name}. Error: {e}"

def control_volume(action: str):
    """
    Controls system volume.
    Args: action (str) - must be 'up', 'down', or 'mute'.
    """
    if action == "up":
        pyautogui.press("volumeup", presses=5) 
        return "Volume increased."
    elif action == "down":
        pyautogui.press("volumedown", presses=5)
        return "Volume decreased."
    elif action == "mute":
        pyautogui.press("volumemute")
        return "Volume muted."
    else:
        return "Invalid volume command."

def set_brightness(level: int):
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level}%."
    except: return "Brightness control failed."

def take_screenshot():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pyautogui.screenshot(f"screenshot_{timestamp}.png")
    return "Screenshot taken."

def get_time():
    """Returns the current system time (12-hour format)."""
    return datetime.datetime.now().strftime("%I:%M %p")

def get_date():
    """Returns the current system date."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y")

def play_youtube(query: str):
    try:
        pywhatkit.playonyt(query)
        return f"Playing {query} on YouTube."
    except Exception as e:
        return f"Error: {e}"

def search_wikipedia(query: str):
    try:
        return wikipedia.summary(query, sentences=2)
    except: return "No wikipedia page found."

def check_weather(city: str):
    """
    Checks weather using wttr.in (No API key required).
    Args: city (str) - The city name.
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=%C+%t")
        if response.status_code == 200:
            result = response.text.strip()
            return f"The weather in {city} is {result}."
        else:
            return "I couldn't reach the weather service."
    except Exception as e:
        return f"Connection error while checking weather: {e}"