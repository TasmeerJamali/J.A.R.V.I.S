import os
import threading
import time
import numpy as np
import pyaudio
import openwakeword
from openwakeword.model import Model

class WakeWordListener:
    def __init__(self, callback=None):
        self.running = False
        self.callback = callback
        self.thread = None
        
        # Audio config
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1280
        self.audio = pyaudio.PyAudio()
        self.mic_stream = None
        
        # Load openWakeWord model
        # We'll use the pre-trained 'hey_jarvis' model if available, or a default one
        try:
            openwakeword.utils.download_models(["hey_jarvis"])
            self.owwModel = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
            print("[Voice] openWakeWord 'hey_jarvis' model loaded.")
        except Exception as e:
            print(f"[Voice] Error loading openWakeWord model: {e}")
            self.owwModel = None

    def start(self):
        if not self.owwModel:
            print("[Voice] Wake Word model not loaded. Aborting listener.")
            return

        self.running = True
        self.mic_stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                          rate=self.RATE, input=True,
                                          frames_per_buffer=self.CHUNK)
        
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("[Voice] Wake Word Listener started.")

    def _listen_loop(self):
        print("[Voice] Listening for 'Hey Jarvis'...")
        while self.running:
            try:
                # Get audio
                audio = np.frombuffer(self.mic_stream.read(self.CHUNK), dtype=np.int16)
                
                # Feed to openWakeWord
                prediction = self.owwModel.predict(audio)
                
                # Check for activation
                # prediction is a dict like {'hey_jarvis': 0.002, ...}
                for model_name, score in prediction.items():
                    if score > 0.5: # Threshold
                        print(f"[Voice] Wake Word Detected! ({model_name})")
                        if self.callback:
                            self.callback()
                        # Reset buffer or pause briefly to avoid double triggers
                        self.owwModel.reset()
            except Exception as e:
                print(f"[Voice] Error in listen loop: {e}")
                break

    def stop(self):
        self.running = False
        if self.mic_stream:
            self.mic_stream.stop_stream()
            self.mic_stream.close()
        if self.audio:
            self.audio.terminate()
        if self.thread:
            self.thread.join()
        print("[Voice] Wake Word Listener stopped.")

if __name__ == "__main__":
    def on_wake():
        print(">>> WAKE WORD TRIGGERED <<<")
    
    listener = WakeWordListener(callback=on_wake)
    listener.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
