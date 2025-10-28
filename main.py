import cv2
import mediapipe as mp
import threading
import time
import pygame

# -------- Settings --------
ALARM_FILE = "alarm.mp3"
EYES_OPEN_THRESHOLD = 0.4  # lower = more sensitive
AWAKE_HOLD_TIME = 3        # seconds to keep eyes open before stopping alarm

# -------- Init --------
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Initialize pygame for sound
pygame.mixer.init()

def play_alarm():
    """Plays alarm in a loop"""
    try:
        pygame.mixer.music.load(ALARM_FILE)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"⚠️ Could not play alarm: {e}")

def stop_alarm():
    """Stops the alarm"""
    pygame.mixer.music.stop()

# -------- Main Function --------
def main():
    cap = cv2.VideoCapture(0)  # camera index 0 = default webcam
    if not cap.isOpened():
        print("❌ Cannot access camera!")
        return

    print("AI Sleep Alarm started... Don't try to fake it 😴")
    alarm_on = False
    awake_start_time = None

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)

            if result.multi_face_landmarks:
                for face_landmarks in result.multi_face_landmarks:
                    # Get eye landmarks (top + bottom of left eye)
                    left = face_landmarks.landmark[159].y
                    right = face_landmarks.landmark[145].y
                    eye_open_ratio = abs(right - left)

                    if eye_open_ratio > EYES_OPEN_THRESHOLD:
                        # Eyes open
                        if awake_start_time is None:
                            awake_start_time = time.time()
                        elif time.time() - awake_start_time > AWAKE_HOLD_TIME:
                            if alarm_on:
                                print("✅ You're finally awake 😤")
                                stop_alarm()
                                alarm_on = False
                    else:
                        # Eyes closed
                        awake_start_time = None
                        if not alarm_on:
                            print("⏰ Wake up!! Eyes closed detected!")
                            threading.Thread(target=play_alarm, daemon=True).start()
                            alarm_on = True

            # Show video window
            cv2.namedWindow("AI Sleep Alarm", cv2.WINDOW_NORMAL)
            cv2.imshow("AI Sleep Alarm", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    stop_alarm()

# -------- Entry Point --------
if __name__ == "__main__":
    main()
