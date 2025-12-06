import win32com.client
import pythoncom

def speak(text):
    """
    Speaks text using Windows SAPI5. 
    BLOCKING: The code waits here until speaking is done.
    """
    print(f"Assistant: {text}")
    try:
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 1 
        speaker.Speak(text)
    except Exception as e:
        print(f"Voice Error: {e}")
    finally:
        pythoncom.CoUninitialize()