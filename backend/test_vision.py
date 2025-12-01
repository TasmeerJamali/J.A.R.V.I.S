import sys
import os
import time

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.vision import VisionModule

def test_vision():
    print("Initializing Vision Module...")
    vision = VisionModule()
    
    target = "Windows Start Button" # Adjust based on OS, but "Start Button" usually works for Windows
    
    print(f"\nTest: Looking for '{target}' on screen...")
    print("Please ensure the taskbar is visible.")
    print("Capturing in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    
    results = vision.analyze_screen_for_text(target)
    
    if results:
        print(f"\nSUCCESS: Found {len(results)} matches.")
        for res in results:
            print(f" - Label: {res['label']}")
            print(f" - Box: {res['box']}")
            
            # Calculate center for clicking
            box = res['box']
            center_x = (box[0] + box[2]) / 2
            center_y = (box[1] + box[3]) / 2
            print(f" - Center: ({center_x}, {center_y})")
    else:
        print("\nFAILURE: No matches found.")

if __name__ == "__main__":
    test_vision()
