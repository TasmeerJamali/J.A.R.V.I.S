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
from api.server import (
    start_server, sio,
    emit_status_update, emit_voice_activity,
    emit_command_log, emit_brain_activity, emit_notification
)
# from core.vision import VisionModule # DISABLED for Cloud Pivot
# from brain.llm import ReasoningAgent # DISABLED for Cloud Pivot
from brain.gemini_brain import GeminiBrain
from skills.desktop_control import DesktopControl
from brain.memory import MemoryModule
from core.security import SecurityModule
from core.continuous_perception import ContinuousPerceptionDaemon

class JarvisBackend:
    def __init__(self):
        self.wake_word_listener = None
        self.websocket_thread = None
        self.gui_root = None
        self.status_labels = {}
        self.start_time = time.time()

        # Agentic Modules
        self.brain = None
        self.control = None
        self.memory = None
        self.security = None
        self.stt = None
        self.tts = None
        self.perception = None

        # Event loop for async emission from sync threads
        self._loop = None

    def _emit_async(self, coro):
        """Run an async coroutine from a synchronous context safely"""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self._loop)

    def start(self):
        print("=" * 50)
        print("  J.A.R.V.I.S. 3.0 — Cloud Intelligence Mode")
        print("=" * 50)

        # Initialize Modules
        print("\n[Init] Loading modules...")
        self.brain = GeminiBrain()
        self.control = DesktopControl()
        self.memory = MemoryModule()
        self.security = SecurityModule()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

        # Initialize Proactive Daemon (shares Brain instance)
        self.perception = ContinuousPerceptionDaemon(brain_instance=self.brain)

        # Start Security Monitoring
        self.security.start_monitoring()

        # Start WebSocket Server
        self.websocket_thread = threading.Thread(target=self._run_websocket_server, daemon=True)
        self.websocket_thread.start()

        # Start Wake Word Listener
        self.wake_word_listener = WakeWordListener(callback=self.on_wake_word_detected)
        self.wake_word_listener.start()

        # Start Proactive Daemon in Background Thread
        threading.Thread(target=self._run_perception_daemon, daemon=True).start()

        # Register Socket.IO events for frontend commands
        self._register_socket_events()

        print("\n[Init] All systems online.")
        print("[Init] Say 'Hey Jarvis' to begin.\n")

        # Launch Status GUI (must be on main thread)
        self.launch_status_gui()

    def _register_socket_events(self):
        """Register Socket.IO event handlers for frontend interaction"""
        @sio.event
        async def send_command(sid, data):
            """Handle typed commands from the frontend"""
            command = data.get('text', '')
            if command:
                print(f"[Main] Frontend command: {command}")
                threading.Thread(
                    target=self.process_text_command,
                    args=(command,),
                    daemon=True
                ).start()

    def _run_perception_daemon(self):
        """Run the proactive perception daemon with its own event loop"""
        def on_interrupt(message):
            print(f"[Main] Proactive Interrupt: {message}")
            if self.gui_root:
                self.gui_root.after(0, lambda: self.update_status("Brain", "PROACTIVE", "magenta"))
            self._emit_async(emit_brain_activity(thought=message, status="proactive"))
            self._emit_async(emit_notification(message, level="proactive"))
            self.tts.speak_sync(message)
            if self.gui_root:
                self.gui_root.after(0, lambda: self.update_status("Brain", "STANDBY", "yellow"))
            self._emit_async(emit_brain_activity(status="standby"))

        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.perception.run_forever(callback=on_interrupt))

    def _run_websocket_server(self):
        start_server(host='127.0.0.1', port=8000)

    def on_wake_word_detected(self):
        print(">>> WAKE WORD DETECTED <<<")

        # Check Security
        if not self.security.user_present:
            print("[Main] Access Denied: User not present.")
            if self.gui_root:
                self.gui_root.after(0, lambda: self.update_status("Security", "LOCKED", "red"))
            self._emit_async(emit_notification("Access denied: User not present", level="warning"))
            return

        # Update GUI + Frontend
        if self.gui_root:
            self.gui_root.after(0, lambda: self.update_status("Wake Word", "TRIGGERED", "red"))
            self.gui_root.after(2000, lambda: self.update_status("Wake Word", "LISTENING", "green"))
        self._emit_async(emit_status_update("wake_word", "TRIGGERED", "red"))
        self._emit_async(emit_voice_activity("wake_detected"))

        # Acknowledge
        self.tts.speak_sync("Yes sir?")

        # Start Voice Interaction
        threading.Thread(target=self.process_voice_command, daemon=True).start()

    def process_voice_command(self):
        """Process a voice command through STT -> Brain -> Action pipeline"""
        if self.gui_root:
            self.gui_root.after(0, lambda: self.update_status("Voice", "LISTENING...", "cyan"))
        self._emit_async(emit_voice_activity("listening"))
        self._emit_async(emit_status_update("voice", "LISTENING", "cyan"))

        command_text = self.stt.listen_and_transcribe()

        if not command_text:
            print("[Main] No speech detected.")
            if self.gui_root:
                self.gui_root.after(0, lambda: self.update_status("Voice", "IDLE", "yellow"))
            self._emit_async(emit_voice_activity("idle"))
            self._emit_async(emit_status_update("voice", "IDLE", "yellow"))
            return

        self._emit_async(emit_voice_activity("recognized", command_text))
        self._execute_command(command_text, source="voice")

    def process_text_command(self, command_text):
        """Process a text command from the frontend"""
        self._execute_command(command_text, source="frontend")

    def _execute_command(self, command_text, source="voice"):
        """Core command execution pipeline"""
        print(f"[Main] Command ({source}): {command_text}")

        # Log the command
        self._emit_async(emit_command_log({
            'text': command_text,
            'source': source,
            'timestamp': time.time(),
            'type': 'user',
        }))

        # Think & Act (Gemini Cloud)
        if self.gui_root:
            self.gui_root.after(0, lambda: self.update_status("Brain", "THINKING...", "cyan"))
        self._emit_async(emit_status_update("brain", "THINKING", "cyan"))
        self._emit_async(emit_brain_activity(thought="Analyzing command...", status="thinking"))

        # Retrieve Memory Context
        context = self.memory.query_memory(command_text)

        # Call Gemini
        plan = self.brain.think_and_act(command_text)
        print(f"[Main] Plan: {plan}")

        # Store interaction in memory
        self.memory.add_memory(f"User: {command_text}. Plan: {plan}")

        if "error" in plan:
            error_msg = plan.get("error", "Unknown error")
            print(f"[Main] Brain Error: {error_msg}")
            self._emit_async(emit_brain_activity(thought=error_msg, status="error"))
            self._emit_async(emit_command_log({
                'text': "I'm having trouble connecting to the cloud, sir.",
                'source': 'jarvis',
                'timestamp': time.time(),
                'type': 'error',
            }))
            self.tts.speak_sync("I'm having trouble connecting to the cloud, sir.")
            return

        # Extract plan data
        thought = plan.get("thought", "")
        action = plan.get("action", "")
        explanation = plan.get("explanation", "")
        args = plan.get("args", [])

        self._emit_async(emit_brain_activity(
            thought=thought,
            action=f"{action}({args})",
            status="executing",
        ))

        # Execute Plan
        try:
            if action == "speak":
                response_text = args[0] if args else ""
                self._emit_async(emit_command_log({
                    'text': response_text,
                    'source': 'jarvis',
                    'timestamp': time.time(),
                    'type': 'response',
                }))
                self._emit_async(emit_voice_activity("speaking", response_text))
                self.tts.speak_sync(response_text)

            elif action == "click":
                x, y = args[0], args[1]
                self._emit_async(sio.emit('target_lock', {
                    'x': x - 25, 'y': y - 25, 'width': 50, 'height': 50,
                    'label': explanation or 'Target'
                }))
                self._emit_async(emit_command_log({
                    'text': f"Clicking at ({x}, {y}) — {explanation}",
                    'source': 'jarvis',
                    'timestamp': time.time(),
                    'type': 'action',
                }))
                self.control.click_element([x-5, y-5, x+5, y+5])

            elif action == "type":
                text_to_type = args[0] if args else ""
                self._emit_async(emit_command_log({
                    'text': f"Typing: {text_to_type}",
                    'source': 'jarvis',
                    'timestamp': time.time(),
                    'type': 'action',
                }))
                self.control.type_text(text_to_type)

            elif action == "press":
                key = args[0] if args else ""
                self._emit_async(emit_command_log({
                    'text': f"Pressing key: {key}",
                    'source': 'jarvis',
                    'timestamp': time.time(),
                    'type': 'action',
                }))
                import pyautogui
                pyautogui.press(key)

        except Exception as e:
            print(f"[Main] Execution Error: {e}")
            self._emit_async(emit_command_log({
                'text': f"Execution failed: {e}",
                'source': 'jarvis',
                'timestamp': time.time(),
                'type': 'error',
            }))
            self.tts.speak_sync("I failed to execute that action, sir.")

        # Reset status
        if self.gui_root:
            self.gui_root.after(0, lambda: self.update_status("Brain", "STANDBY", "yellow"))
            self.gui_root.after(0, lambda: self.update_status("Voice", "IDLE", "yellow"))
        self._emit_async(emit_status_update("brain", "STANDBY", "yellow"))
        self._emit_async(emit_status_update("voice", "IDLE", "yellow"))
        self._emit_async(emit_brain_activity(status="standby"))
        self._emit_async(emit_voice_activity("idle"))

    def update_status(self, key, value, color):
        if key in self.status_labels:
            self.status_labels[key].config(text=f"  {key}: {value}", fg=color)

    def launch_status_gui(self):
        self.gui_root = tk.Tk()
        self.gui_root.title("J.A.R.V.I.S. 3.0 — Backend Status")
        self.gui_root.geometry("420x500")
        self.gui_root.configure(bg="#0a0a0a")
        self.gui_root.resizable(False, False)

        # Title
        title = tk.Label(
            self.gui_root, text="J.A.R.V.I.S. 3.0",
            font=("Courier", 22, "bold"), fg="#00ffcc", bg="#0a0a0a",
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.gui_root, text="Cloud Intelligence Mode",
            font=("Courier", 10), fg="#00ffcc", bg="#0a0a0a",
        )
        subtitle.pack(pady=(0, 15))

        # Separator
        sep = tk.Frame(self.gui_root, height=1, bg="#00ffcc")
        sep.pack(fill="x", padx=30, pady=5)

        # Status frame
        status_frame = tk.Frame(self.gui_root, bg="#0a0a0a")
        status_frame.pack(pady=10, fill="x", padx=20)

        self.create_status_label(status_frame, "Wake Word", "LISTENING", "green")
        self.create_status_label(status_frame, "Voice", "IDLE", "yellow")
        self.create_status_label(status_frame, "Brain", "STANDBY", "yellow")
        self.create_status_label(status_frame, "WebSocket", "RUNNING", "green")
        self.create_status_label(status_frame, "Security", "MONITORING", "cyan")
        self.create_status_label(status_frame, "Perception", "ACTIVE", "magenta")

        # Separator
        sep2 = tk.Frame(self.gui_root, height=1, bg="#333")
        sep2.pack(fill="x", padx=30, pady=10)

        # Info
        info = tk.Label(
            self.gui_root, text='Say "Hey Jarvis" to begin',
            font=("Courier", 10), fg="#666", bg="#0a0a0a",
        )
        info.pack(pady=5)

        # Shutdown button
        btn = tk.Button(
            self.gui_root, text="SHUTDOWN", command=self.shutdown,
            font=("Courier", 12, "bold"), bg="#cc0000", fg="white",
            activebackground="#990000", activeforeground="white",
            relief="flat", padx=20, pady=5,
        )
        btn.pack(pady=20)

        self.gui_root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.gui_root.mainloop()

    def create_status_label(self, parent, key, value, color):
        lbl = tk.Label(
            parent, text=f"  {key}: {value}",
            font=("Courier", 12), fg=color, bg="#0a0a0a", anchor="w",
        )
        lbl.pack(fill="x", pady=2)
        self.status_labels[key] = lbl

    def shutdown(self):
        print("\n[Shutdown] Shutting down J.A.R.V.I.S....")
        if self.wake_word_listener:
            self.wake_word_listener.stop()
        if self.security:
            self.security.stop()
        if self.perception:
            self.perception.running = False
        if self.gui_root:
            self.gui_root.destroy()
        print("[Shutdown] Goodbye, sir.")
        sys.exit(0)

if __name__ == "__main__":
    app = JarvisBackend()
    app.start()
