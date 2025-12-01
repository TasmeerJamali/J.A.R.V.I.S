import os
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import pyautogui
import time

class VisionModule:
    def __init__(self, model_id='microsoft/Florence-2-large'):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        print(f"[Vision] Loading Florence-2 model on {self.device}...")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                trust_remote_code=True,
                torch_dtype=self.torch_dtype
            ).to(self.device)
            
            self.processor = AutoProcessor.from_pretrained(
                model_id, 
                trust_remote_code=True
            )
            print("[Vision] Model loaded successfully.")
        except Exception as e:
            print(f"[Vision] CRITICAL ERROR loading model: {e}")
            self.model = None
            self.processor = None

    def capture_screen(self):
        """Captures the current screen and returns a PIL Image."""
        screenshot = pyautogui.screenshot()
        return screenshot

    def analyze_screen_for_text(self, text_prompt, image=None):
        """
        Finds the bounding box of a specific UI element described by text_prompt.
        Returns a list of dicts: {'label': str, 'box': [x1, y1, x2, y2]}
        """
        if not self.model:
            print("[Vision] Model not loaded.")
            return []

        if image is None:
            image = self.capture_screen()

        # Florence-2 uses specific task prompts. 
        # For finding objects/text, '<OPEN_VOCABULARY_DETECTION>' or '<CAPTION_TO_PHRASE_GROUNDING>' is best.
        # We'll use <CAPTION_TO_PHRASE_GROUNDING> as it maps a description to a box.
        
        task_prompt = "<CAPTION_TO_PHRASE_GROUNDING>"
        prompt = task_prompt + text_prompt
        
        inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)

        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            early_stopping=False,
            do_sample=False,
            num_beams=3,
        )
        
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        
        # Post-process to get coordinates
        parsed_answer = self.processor.post_process_generation(
            generated_text, 
            task=task_prompt, 
            image_size=(image.width, image.height)
        )
        
        # parsed_answer format for this task: {'<CAPTION_TO_PHRASE_GROUNDING>': {'bboxes': [[x1, y1, x2, y2]], 'labels': ['text_prompt']}}
        
        results = []
        if task_prompt in parsed_answer:
            data = parsed_answer[task_prompt]
            bboxes = data.get('bboxes', [])
            labels = data.get('labels', [])
            
            for bbox, label in zip(bboxes, labels):
                results.append({
                    'label': label,
                    'box': bbox # [x1, y1, x2, y2]
                })
                
        return results

if __name__ == "__main__":
    # Simple test if run directly
    vision = VisionModule()
    print("Capturing screen in 3 seconds...")
    time.sleep(3)
    results = vision.analyze_screen_for_text("Start Button")
    print("Results:", results)
