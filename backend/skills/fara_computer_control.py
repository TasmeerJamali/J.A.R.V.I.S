import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from PIL import ImageGrab
import pyautogui
import time
import re

class FaraComputerControl:
    """
    Uses Fara-7B (Microsoft's Computer Use Agent) to see and control the computer.
    Unlike Florence-2, Fara is TRAINED to click, type, and navigate.
    """
    
    def __init__(self):
        print("[Fara] Loading Fara-7B model...")
        try:
            # Load model in half-precision (float16) to save VRAM
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                "microsoft/Fara-7B",
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.processor = AutoProcessor.from_pretrained("microsoft/Fara-7B")
            print("[Fara] Model loaded successfully.")
        except Exception as e:
            print(f"[Fara] Error loading model: {e}")
            self.model = None
            self.processor = None
    
    def execute_task(self, natural_language_goal):
        """
        e.g., "Open Spotify and play focus music"
        Fara will autonomously decide the next action.
        """
        if not self.model:
            print("[Fara] Model not loaded.")
            return "Error: Model not loaded"

        print(f"[Fara] Executing task: {natural_language_goal}")
        screenshot = ImageGrab.grab()
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": screenshot},
                    {"type": "text", "text": f"Task: {natural_language_goal}\n\nWhat is the NEXT action you should take? Output in format: ACTION(arguments)"}
                ]
            }
        ]
        
        # Prepare inputs
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[screenshot], return_tensors="pt").to("cuda")
        
        # Generate action
        output = self.model.generate(**inputs, max_new_tokens=100)
        action_text = self.processor.decode(output[0], skip_special_tokens=True)
        
        print(f"[Fara] Generated Action: {action_text}")
        
        # Parse and execute
        self.parse_and_execute_action(action_text)
        
        return action_text
    
    def parse_and_execute_action(self, action_str):
        """Parse Fara's output and execute via PyAutoGUI"""
        
        if 'click(' in action_str:
            # Extract coordinates: click(x, y)
            coords = re.findall(r'click\((\d+),\s*(\d+)\)', action_str)
            if coords:
                x, y = int(coords[0][0]), int(coords[0][1])
                print(f"[Fara] Clicking at ({x}, {y})")
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                
        elif 'type(' in action_str:
            # Extract text: type("text")
            text = re.findall(r'type\(["\'](.+?)["\']\)', action_str)
            if text:
                print(f"[Fara] Typing: {text[0]}")
                pyautogui.typewrite(text[0], interval=0.05)
                
        elif 'press(' in action_str:
             # Extract key: press("enter")
            key = re.findall(r'press\(["\'](.+?)["\']\)', action_str)
            if key:
                print(f"[Fara] Pressing: {key[0]}")
                pyautogui.press(key[0])

if __name__ == "__main__":
    # Test stub
    fara = FaraComputerControl()
    # fara.execute_task("Click the Start button")
