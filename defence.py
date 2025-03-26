import cv2
import time
import RPi.GPIO as GPIO
from ultralytics import YOLO

class WildlifeDefenseSystem:
    def __init__(self, camera_url, confidence_threshold=0.6):
        # GPIO Pin Configuration
        self.STROBE_PIN = 18
        self.ALARM_PIN = 23
        self.FENCE_PIN = 24

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.STROBE_PIN, GPIO.OUT)
        GPIO.setup(self.ALARM_PIN, GPIO.OUT)
        GPIO.setup(self.FENCE_PIN, GPIO.OUT)

        # Camera and Detection Setup
        self.camera_url = camera_url
        self.confidence_threshold = confidence_threshold
        
        # Load YOLO model
        self.model = YOLO("yolov8n.pt")  # Nano model for performance
        
        # Detected animal types
        self.target_animals = [
            "dog", "cat", "cow", "elephant", 
            "bear", "wolf", "fox", "deer"
        ]

    def activate_defense(self, duration=10):
        """Activate defense systems when animal detected"""
        print("🚨 ANIMAL DETECTED! ACTIVATING DEFENSE SYSTEMS 🚨")
        
        # Activate strobe, alarm, and fence
        GPIO.output(self.STROBE_PIN, GPIO.HIGH)
        GPIO.output(self.ALARM_PIN, GPIO.HIGH)
        GPIO.output(self.FENCE_PIN, GPIO.HIGH)
        
        # Active for specified duration
        time.sleep(duration)
        
        # Deactivate systems
        GPIO.output(self.STROBE_PIN, GPIO.LOW)
        GPIO.output(self.ALARM_PIN, GPIO.LOW)
        GPIO.output(self.FENCE_PIN, GPIO.LOW)

    def detect_animals(self):
        """Main detection loop"""
        cap = cv2.VideoCapture(self.camera_url)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame. Retrying...")
                time.sleep(1)
                continue

            # Run detection
            results = self.model(frame)
            
            for result in results:
                for box in result.boxes.data:
                    x1, y1, x2, y2, conf, cls = box
                    label = result.names[int(cls)]
                    
                    if label in self.target_animals and conf > self.confidence_threshold:
                        # Draw bounding box
                        cv2.rectangle(
                            frame, 
                            (int(x1), int(y1)), 
                            (int(x2), int(y2)), 
                            (0, 0, 255), 
                            2
                        )
                        cv2.putText(
                            frame, 
                            f"{label} (conf: {conf:.2f})", 
                            (int(x1), int(y1 - 10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, 
                            (0, 0, 255), 
                            2
                        )
                        
                        # Activate defense
                        self.activate_defense()

            # Display frame (optional, can be disabled)
            cv2.imshow("Wildlife Defense Camera", frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()

    def run(self):
        """Start the wildlife defense system"""
        try:
            print("🌿 Wildlife Defense System Initialized 🌿")
            print(f"Monitoring RTSP Stream: {self.camera_url}")
            print(f"Target Animals: {', '.join(self.target_animals)}")
            self.detect_animals()
        except Exception as e:
            print(f"Error: {e}")
            GPIO.cleanup()

def main():
    # Replace with your actual RTSP camera URL
    CAMERA_URL = "rtsp://<camera-ip>:554/stream"
    
    defense_system = WildlifeDefenseSystem(
        camera_url=CAMERA_URL, 
        confidence_threshold=0.6
    )
    defense_system.run()

if __name__ == "__main__":
    main()
