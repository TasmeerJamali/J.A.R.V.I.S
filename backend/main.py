import threading
import time
import tkinter as tk
from tkinter import ttk
import sys
import os
import asyncio
import json

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice.wake_word import WakeWordListener
from voice.stt import SpeechToText
from voice.tts import TextToSpeech
from api.server import start_server, sio
# from core.vision import VisionModule # DISABLED for Cloud Pivot
# from brain.llm import ReasoningAgent # DISABLED for Cloud Pivot
from brain.gemini_brain import GeminiBrain # NEW Cloud Brain
from skills.desktop_control import DesktopControl
from brain.memory import MemoryModule
from core.security import SecurityModule
from core.continuous_perception import ContinuousPerceptionDaemon # NEW Proactive Daemon

class JarvisBackend:
    def __init__(self):
        self.wake_word_listener = None
        self.websocket_thread = None
        self.gui_root = None
        self.status_labels = {}
        
        # Agentic Modules
        self.brain = None # Gemini Brain
        self.control = None
        self.memory = None
        self.security = None
        self.stt = None
        self.tts = None
        self.perception = None # Proactive Daemon

    def start(self):
        print("Initializing J.A.R.V.I.S. Backend (Cloud Mode)...")
        
        # Initialize Modules
        self.brain = GeminiBrain() # Cloud Brain
        self.control = DesktopControl()
        self.memory = MemoryModule()
        self.security = SecurityModule()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        
        # Initialize Proactive Daemon (Share Brain)
        self.perception = ContinuousPerceptionDaemon(brain_instance=self.brain)
        
        # Start Security Monitoring
        # self.security.start_monitoring()
        
        # Start WebSocket Server
        self.websocket_thread = threading.Thread(target=self._run_websocket_server, daemon=True)
        self.websocket_thread.start()
        
        # Start Wake Word Listener
        self.wake_word_listener = WakeWordListener(callback=self.on_wake_word_detected)
        self.wake_word_listener.start()
        
        # Start Proactive Daemon in Background Thread
        threading.Thread(target=self._run_perception_daemon, daemon=True).start()
        
        # Launch Dummy GUI (Must be on main thread)
        self.launch_dummy_gui()

    def _run_perception_daemon(self):
        # Callback for when Daemon wants to speak
        def on_interrupt(message):
            print(f"[Main] Proactive Interrupt: {message}")
            if self.gui_root:
                 self.gui_root.after(0, lambda: self.update_status("Brain", "PROACTIVE", "magenta"))
            self.tts.speak_sync(message)
            if self.gui_root:
                 self.gui_root.after(0, lambda: self.update_status("Brain", "STANDBY", "yellow"))

        asyncio.run(self.perception.run_forever(callback=on_interrupt))

    def _run_websocket_server(self):
        # Run uvicorn server
        start_server(host='127.0.0.1', port=8000)

    def on_wake_word_detected(self):
        print(">>> MAIN: Wake Word Detected! <<<")
        
        # Check Security
        # if not self.security.user_present:
        #     print("[Main] Access Denied: User not present.")
        #     if self.gui_root:
        #         self.gui_root.after(0, lambda: self.update_status("Security", "LOCKED", "red"))
        #     return

        # Update GUI
        if self.gui_root:
            self.gui_root.after(0, lambda: self.update_status("Wake Word", "TRIGGERED", "red"))
            self.gui_root.after(2000, lambda: self.update_status("Wake Word", "LISTENING", "green"))
            
        # Play listening sound (optional)
        # self.tts.speak_sync("Yes sir?")
        
        # Start Voice Interaction Loop
        threading.Thread(target=self.process_voice_command, daemon=True).start()

    def process_voice_command(self):
        # 1. Listen (STT)
        if self.gui_root:
             self.gui_root.after(0, lambda: self.update_status("Voice", "LISTENING...", "cyan"))
        
        command_text = self.stt.listen_and_transcribe()
        
        if not command_text:
            print("[Main] No speech detected.")
            if self.gui_root:
                 self.gui_root.after(0, lambda: self.update_status("Voice", "IDLE", "yellow"))
            return

        print(f"[Main] User said: {command_text}")
        
        # 2. Think & Act (Gemini Cloud)
        if self.gui_root:
             self.gui_root.after(0, lambda: self.update_status("Brain", "THINKING (CLOUD)...", "cyan"))
        
        # Retrieve Context (Optional, can pass to Gemini too)
        context = self.memory.query_memory(command_text)
        
        # Call Gemini
        plan = self.brain.think_and_act(command_text)
        print(f"[Main] Plan: {plan}")
        
        # Store interaction
        self.memory.add_memory(f"User: {command_text}. Plan: {plan}")
        
        if "error" in plan:
            print(f"[Main] Brain Error: {plan['error']}")
            self.tts.speak_sync("I'm having trouble connecting to the cloud, sir.")
            return

        # Execute Plan
        if "thought" in plan:
            # self.tts.speak_sync(plan["thought"]) # Optional: Speak thought
            pass
            
        action = plan.get("action")
        args = plan.get("args", [])
        
        try:
            if action == "speak":
                self.tts.speak_sync(args[0])
                
            elif action == "click":
                x, y = args[0], args[1]
                # UI Feedback
                asyncio.run(sio.emit('target_lock', {
                    'x': x - 25, 'y': y - 25, 'width': 50, 'height': 50, 'label': 'Target'
                }))
                self.control.click_element([x-5, y-5, x+5, y+5]) # Create dummy box for clicker
                
            elif action == "type":
                self.control.type_text(args[0])
                
            elif action == "press":
                import pyautogui
                pyautogui.press(args[0])
                
        except Exception as e:
            print(f"[Main] Execution Error: {e}")
            self.tts.speak_sync("I failed to execute that action.")
            
        if self.gui_root:
             self.gui_root.after(0, lambda: self.update_status("Brain", "STANDBY", "yellow"))
             self.gui_root.after(0, lambda: self.update_status("Voice", "IDLE", "yellow"))

    def update_status(self, key, value, color):
        if key in self.status_labels:
            self.status_labels[key].config(text=f"{key}: {value}", fg=color)

    def launch_dummy_gui(self):
        self.gui_root = tk.Tk()
        self.gui_root.title("J.A.R.V.I.S. Backend Status")
        self.gui_root.geometry("400x450")
        self.gui_root.configure(bg="black")

        style = ttk.Style()
        style.theme_use('clam')
        
        label = tk.Label(self.gui_root, text="J.A.R.V.I.S. ONLINE", font=("Courier", 20, "bold"), fg="#00ffcc", bg="black")
        label.pack(pady=20)

        status_frame = tk.Frame(self.gui_root, bg="black")
        status_frame.pack(pady=10)

        # Status Labels
        self.create_status_label(status_frame, "Wake Word", "LISTENING", "green")
        self.create_status_label(status_frame, "Voice", "IDLE", "yellow")
        self.create_status_label(status_frame, "WebSocket", "RUNNING", "green")
        self.create_status_label(status_frame, "LLM", "STANDBY", "yellow")
        self.create_status_label(status_frame, "Security", "MONITORING", "cyan")

        btn = tk.Button(self.gui_root, text="SHUTDOWN", command=self.shutdown, font=("Courier", 12, "bold"), bg="red", fg="white")
        btn.pack(pady=20)

        self.gui_root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.gui_root.mainloop()

    def create_status_label(self, parent, key, value, color):
        lbl = tk.Label(parent, text=f"{key}: {value}", font=("Courier", 12), fg=color, bg="black")
        lbl.pack()
        self.status_labels[key] = lbl

    def shutdown(self):
        print("Shutting down J.A.R.V.I.S....")
        if self.wake_word_listener:
            self.wake_word_listener.stop()
        if self.security:
            self.security.stop()
        if self.gui_root:
            self.gui_root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = JarvisBackend()
    app.start()
