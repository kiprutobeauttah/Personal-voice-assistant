import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import subprocess
import threading
import time
import pyjokes
import sys

# Optional: pygame for playing local music
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

class VoiceAssistant:
    def __init__(self, user_name="User", wake_word="assistant"):
        self.user_name = user_name
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        # Configure voice rate (optional)
        rate = self.tts.getProperty('rate')
        self.tts.setProperty('rate', rate - 20)

        # If pygame is available, init mixer for music playback
        if PYGAME_AVAILABLE:
            pygame.mixer.init()

        self.listening = True

    def speak(self, text):
        """Speak text using pyttsx3 and also print to console."""
        print(f"Assistant: {text}")
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception as e:
            print("TTS error:", e)

    def listen(self, timeout=5, phrase_time_limit=7):
        """Listen for audio and return recognized text (or None)."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio)
                print("You:", text)
                return text.lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print("Speech recognition service error:", e)
                return None

    def greet_user(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greet = "Good morning"
        elif hour < 18:
            greet = "Good afternoon"
        else:
            greet = "Good evening"
        self.speak(f"{greet}, {self.user_name}. I am ready. Say '{self.wake_word}' to wake me, or press Ctrl+C to exit.")

    def run(self):
        """Main loop: waits for wake word, then processes commands."""
        try:
            while self.listening:
                print("Listening for wake word...")
                text = self.listen(timeout=8, phrase_time_limit=4)
                if not text:
                    continue
                if self.wake_word in text:
                    self.speak("Yes? How can I help you?")
                    command = self.listen(timeout=6, phrase_time_limit=8)
                    if not command:
                        self.speak("I did not catch that. Please try again.")
                        continue
                    self.handle_command(command)
        except KeyboardInterrupt:
            self.speak("Shutting down. Goodbye.")
            sys.exit(0)

    def handle_command(self, cmd):
        cmd = cmd.lower()
        # Basic commands
        if "time" in cmd:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {now}.")
        elif "date" in cmd:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {today}.")
        elif "open youtube" in cmd:
            self.speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif cmd.startswith("open "):
            # open website or application name
            target = cmd.replace("open ", "").strip()
            # simple heuristic: if contains dot or http, treat as URL
            if "." in target or "http" in target:
                url = target if target.startswith("http") else f"https://{target}"
                webbrowser.open(url)
                self.speak(f"Opening {url}")
            else:
                # attempt to launch an application by name (Windows)
                self.open_application_by_name(target)
        elif "search for" in cmd:
            query = cmd.split("search for",1)[1].strip()
            if query:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(url)
                self.speak(f"Searching Google for {query}")
            else:
                self.speak("What should I search for?")
        elif "play music" in cmd:
            # play first music file in assets/music if present
            music_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "music")
            if PYGAME_AVAILABLE and os.path.isdir(music_dir):
                files = [f for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav'))]
                if files:
                    file_path = os.path.join(music_dir, files[0])
                    self.play_music(file_path)
                    self.speak(f"Playing {files[0]}")
                else:
                    self.speak("No music files found in assets/music.")
            else:
                self.speak("Music playback is not available. Ensure pygame is installed and there is an assets/music folder.")
        elif "stop music" in cmd:
            if PYGAME_AVAILABLE:
                pygame.mixer.music.stop()
                self.speak("Music stopped.")
            else:
                self.speak("Music module not available.")
        elif "joke" in cmd:
            joke = pyjokes.get_joke()
            self.speak(joke)
        elif "exit" in cmd or "quit" in cmd or "goodbye" in cmd:
            self.speak("Goodbye.")
            sys.exit(0)
        else:
            # fallback: suggest searching the web
            self.speak("I can not perform that command yet. I will search the web for you.")
            url = f"https://www.google.com/search?q={cmd.replace(' ', '+')}"
            webbrowser.open(url)

    def open_application_by_name(self, name):
        """
        Attempts to open an application by name.
        For Windows, common apps can be launched by 'startfile' if a file association exists,
        or by calling 'start <app>' via subprocess with shell=True.
        You can customize this method to map friendly names to executable paths.
        """
        name = name.lower()
        mapping = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "edge": r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "vlc": r"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
        }
        if name in mapping:
            path = mapping[name]
            try:
                if os.path.isfile(path):
                    subprocess.Popen([path])
                else:
                    # try to use shell start for known executable names
                    subprocess.Popen(path, shell=True)
                self.speak(f"Launching {name}")
            except Exception as e:
                self.speak(f"Failed to launch {name}: {e}")
        else:
            # fallback: try start file on the name
            try:
                subprocess.Popen(name, shell=True)
                self.speak(f"Attempting to open {name}")
            except Exception as e:
                self.speak(f"Could not open {name}: {e}")

    def play_music(self, filepath):
        if not PYGAME_AVAILABLE:
            self.speak("Pygame is not installed. Install it to play music.")
            return
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
        except Exception as e:
            self.speak(f"Failed to play music: {e}")
