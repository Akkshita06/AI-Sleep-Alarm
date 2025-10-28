import cv2

for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Camera opened successfully at index {i}. Press Q to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        break
    else:
        print(f"❌ Camera not found at index {i}. Trying next...")
