import speech_recognition as sr
import tempfile
from gtts import gTTS
import os
import pygame
import streamlit as st  # Added missing import

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def text_to_speech(self, text):
        """Convert text to speech and play it"""
        tts = gTTS(text=text, lang='en')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name

    def play_audio(self, file_path):
        """Play audio file using pygame"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        finally:
            # Ensure file is cleaned up even if playback fails
            if os.path.exists(file_path):
                os.remove(file_path)

    def record_audio(self):
        """Record audio from microphone and convert to text"""
        try:
            with sr.Microphone() as source:
                st.write("Listening... Speak now!")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                st.error("Could not understand audio. Please try speaking again.")
                return None
            except sr.RequestError as e:
                st.error(f"Could not request results from speech recognition service; {e}")
                return None
        except Exception as e:
            st.error(f"Error recording audio: {str(e)}")
            return None