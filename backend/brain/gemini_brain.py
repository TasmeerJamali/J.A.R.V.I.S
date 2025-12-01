import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import ImageGrab
import json
import time

# Load environment variables
load_dotenv()

class GeminiBrain:
    def __init__(self):
        print("[Gemini] Initializing Cloud Brain...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[Gemini] CRITICAL ERROR: GEMINI_API_KEY not found in .env")
            self.model = None
            return

        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash for speed and multimodal capabilities
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("[Gemini] Connected to Google AI Cloud.")

    def think_and_act(self, user_command):
        """
        Captures screen, sends to Gemini with user command, returns JSON plan.
        """
        if not self.model:
            return {"error": "Gemini API key missing"}

        print(f"[Gemini] Analyzing: '{user_command}'...")
        
        # 1. Capture Screen
        screenshot = ImageGrab.grab()
        
        # 2. Construct Prompt
        prompt = f"""
        You are J.A.R.V.I.S., an intelligent desktop assistant.
        USER COMMAND: "{user_command}"
        
        Analyze the attached screenshot and the user's command.
        Return a JSON object with your plan.
        
        AVAILABLE TOOLS:
        - click(x, y): Click at coordinates.
        - type(text): Type text.
        - speak(text): Speak a response.
        - press(key): Press a key (e.g., 'enter', 'win').
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "thought": "Brief reasoning about what to do.",
            "action": "tool_name",
            "args": [arg1, arg2],
            "explanation": "Why this action?"
        }}
        
        Example:
        {{
            "thought": "I see the Spotify icon at 100, 200.",
            "action": "click",
            "args": [100, 200],
            "explanation": "Opening Spotify."
        }}
        
        If you need to do nothing or just reply:
        {{
            "thought": "User just said hello.",
            "action": "speak",
            "args": ["Hello sir, how can I help?"],
            "explanation": "Greeting user."
        }}
        """
        
        try:
            # 3. Call Gemini API
            start_time = time.time()
            response = self.model.generate_content([prompt, screenshot])
            latency = time.time() - start_time
            print(f"[Gemini] Response received in {latency:.2f}s")
            
            # 4. Parse Response
            text_response = response.text
            # Clean up json markdown if present
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].split("```")[0].strip()
                
            plan = json.loads(text_response)
            return plan
            
        except Exception as e:
            print(f"[Gemini] Error: {e}")
            return {"error": str(e), "thought": "I encountered an error connecting to the cloud."}

if __name__ == "__main__":
    brain = GeminiBrain()
    # Test
    # print(brain.think_and_act("What is on my screen?"))
