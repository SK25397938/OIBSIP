import os
import threading
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
import tools   
import voice    

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
my_tools = [
    tools.open_app,
    tools.close_app,
    tools.control_volume,
    tools.check_weather,
    tools.take_screenshot,
    tools.set_brightness,
    tools.get_time,        
    tools.get_date,      
    tools.play_youtube,
    tools.search_wikipedia
]
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash', 
    tools=my_tools,
    system_instruction="You are Vecna. You control the user's PC. "
                       "Capabilities: Open/Close apps, Play music (YouTube), "
                       "Control volume/brightness, Take screenshots, Check Date/Time, Search Wikipedia, and CHECK WEATHER. "
                       "If the user says a city name (e.g. 'Paris'), check the weather for that city. "
                       "IMPORTANT: If a tool returns an error, SPEAK THAT EXACT ERROR. "
                       "KEEP RESPONSES VERY SHORT (under 2 sentences)."
)

chat = model.start_chat(enable_automatic_function_calling=True)
class VecnaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vecna AI Assistant")
        self.root.geometry("600x500")
        self.status_label = tk.Label(root, text="Status: Initializing...", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11))
        self.chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.chat_area.insert(tk.END, "System: Vecna is starting up...\n")
        self.is_running = True
        self.thread = threading.Thread(target=self.run_voice_loop)
        self.thread.daemon = True 
        self.thread.start()

    def update_status(self, text):
        """Updates the status label safely."""
        self.status_label.config(text=f"Status: {text}")

    def log_message(self, sender, message):
        """Adds a message to the chat window."""
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.see(tk.END) 

    def run_voice_loop(self):
        """The main logic loop, running in a background thread."""
        recognizer = sr.Recognizer()
        
        recognizer.pause_threshold = 0.6 
        recognizer.non_speaking_duration = 0.4 
        recognizer.dynamic_energy_threshold = True 
        voice.speak("System online. Vecna is ready.")
        self.update_status("Ready")
        while self.is_running:
            try:
                with sr.Microphone() as source:
                    self.update_status("Listening...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
                self.update_status("Processing...")
                user_input = recognizer.recognize_google(audio).lower()
                self.log_message("User", user_input)
                if "exit" in user_input or "stop" in user_input:
                    voice.speak("Goodbye.")
                    self.update_status("Offline")
                    self.root.quit()
                    break
                response = chat.send_message(user_input)
                if response.text:
                    self.log_message("Vecna", response.text)
                    self.update_status("Speaking...")
                    voice.speak(response.text)
                    self.update_status("Ready")
            except sr.UnknownValueError:
                self.update_status("Idle (No speech detected)")
            except sr.RequestError:
                self.update_status("Internet Error")
                voice.speak("Internet connection error.")
            except Exception as e:
                self.log_message("Error", str(e))
                print(f"Error: {e}")
if __name__ == "__main__":
    root = tk.Tk()
    app = VecnaGUI(root)
    root.mainloop()