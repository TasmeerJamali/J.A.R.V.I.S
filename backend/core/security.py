import cv2
import mediapipe as mp
import time
import threading

class SecurityModule:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.running = False
        self.user_present = False
        self.thread = None

    def start_monitoring(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("[Security] Face Monitoring started.")

    def _monitor_loop(self):
        # 0 is usually the default webcam
        self.cap = cv2.VideoCapture(0)
        
        while self.running and self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("[Security] Ignoring empty camera frame.")
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(image)

            # Draw the face mesh annotations on the image.
            # image.flags.writeable = True
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.multi_face_landmarks:
                if not self.user_present:
                    print("[Security] User detected.")
                    self.user_present = True
            else:
                if self.user_present:
                    print("[Security] User away.")
                    self.user_present = False
            
            # We could emit this status to the frontend for a "Locked/Unlocked" UI
            
            time.sleep(0.1) # Limit frame rate check

        self.cap.release()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("[Security] Face Monitoring stopped.")

if __name__ == "__main__":
    sec = SecurityModule()
    sec.start_monitoring()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sec.stop()
