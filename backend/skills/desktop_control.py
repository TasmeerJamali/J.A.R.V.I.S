import pyautogui
import time
import random
import math
import scipy.interpolate
import numpy as np

# Fail-safe: Move mouse to upper-left corner to abort
pyautogui.FAILSAFE = True

class DesktopControl:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

    def move_mouse_smooth(self, x, y, duration=0.5):
        """
        Moves the mouse to (x, y) using a Bézier curve to simulate human movement.
        """
        start_x, start_y = pyautogui.position()
        
        # Random control points for Bézier curve
        control_1_x = start_x + (x - start_x) * random.uniform(0.2, 0.8) + random.randint(-50, 50)
        control_1_y = start_y + (y - start_y) * random.uniform(0.2, 0.8) + random.randint(-50, 50)
        
        # Generate points
        points = np.array([[start_x, start_y], [control_1_x, control_1_y], [x, y]])
        
        # Interpolate
        t = np.linspace(0, 1, num=20)
        # Simple quadratic bezier
        curve_x = (1-t)**2 * start_x + 2*(1-t)*t * control_1_x + t**2 * x
        curve_y = (1-t)**2 * start_y + 2*(1-t)*t * control_1_y + t**2 * y
        
        # Move
        for i in range(len(curve_x)):
            pyautogui.moveTo(curve_x[i], curve_y[i], _pause=False)
            time.sleep(duration / len(curve_x))

    def click_element(self, coords):
        """
        Clicks at the specified coordinates [x1, y1, x2, y2].
        Calculates the center and adds a small random offset.
        """
        if not coords or len(coords) != 4:
            print("[Control] Invalid coordinates for click.")
            return

        x1, y1, x2, y2 = coords
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Add slight randomness to avoid bot detection logic (if any)
        target_x = center_x + random.randint(-5, 5)
        target_y = center_y + random.randint(-5, 5)
        
        print(f"[Control] Moving to ({target_x}, {target_y})...")
        self.move_mouse_smooth(target_x, target_y)
        pyautogui.click()
        print("[Control] Clicked.")

    def type_text(self, text):
        """Types text with variable delay."""
        print(f"[Control] Typing: {text}")
        for char in text:
            pyautogui.write(char)
            time.sleep(random.uniform(0.05, 0.15))

if __name__ == "__main__":
    ctrl = DesktopControl()
    print("Moving mouse in 2 seconds...")
    time.sleep(2)
    ctrl.move_mouse_smooth(500, 500)
