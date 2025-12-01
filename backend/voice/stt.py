from faster_whisper import WhisperModel
import pyaudio
import wave
import os
import numpy as np

class SpeechToText:
    def __init__(self, model_size="tiny.en"): # Use tiny.en for speed
        print(f"[Voice] Loading Whisper model ({model_size})...")
        try:
            # Run on CPU with INT8 for speed/compatibility
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            print("[Voice] Whisper model loaded.")
        except Exception as e:
            print(f"[Voice] Error loading Whisper: {e}")
            self.model = None

    def listen_and_transcribe(self, duration=5):
        """
        Records audio for a fixed duration and transcribes it.
        In a real app, use VAD (Voice Activity Detection) instead of fixed duration.
        """
        if not self.model:
            return ""

        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 16000
        p = pyaudio.PyAudio()

        print("[Voice] Listening...")
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        frames = []

        for i in range(0, int(rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        print("[Voice] Processing...")
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save to temp file
        filename = "temp_audio.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Transcribe
        segments, info = self.model.transcribe(filename, beam_size=5)
        text = "".join([segment.text for segment in segments]).strip()
        
        os.remove(filename)
        print(f"[Voice] Heard: '{text}'")
        return text

if __name__ == "__main__":
    stt = SpeechToText()
    stt.listen_and_transcribe()
