"""
Windows Personal Voice Assistant - Main Entry Point
Run: python src/main.py
"""

from assistant import VoiceAssistant

def main():
    assistant = VoiceAssistant(user_name="User")  # change name if you like
    assistant.greet_user()
    assistant.run()

if __name__ == "__main__":
    main()
