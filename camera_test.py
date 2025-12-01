import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

frame_count = 0

while True:
    ret, frame = cap.read()
    frame_count += 1
    print(f"Frame count: {frame_count}, ret: {ret}")
    if not ret:
        print("Can't receive frame. Exiting ...")
        break
    cv2.imshow('Test Camera', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
