import edge_tts
import pygame
import asyncio
import os

class TextToSpeech:
    def __init__(self, voice="en-GB-RyanNeural"): # Jarvis-like British voice
        self.voice = voice
        pygame.mixer.init()

    async def speak(self, text):
        """Generates audio from text and plays it."""
        if not text:
            return

        print(f"[Voice] Speaking: {text}")
        output_file = "temp_speech.mp3"
        
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)
            
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            pygame.mixer.music.unload()
            os.remove(output_file)
            
        except Exception as e:
            print(f"[Voice] TTS Error: {e}")

    def speak_sync(self, text):
        asyncio.run(self.speak(text))

if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak_sync("Hello sir, I am J.A.R.V.I.S. Systems are online.")
