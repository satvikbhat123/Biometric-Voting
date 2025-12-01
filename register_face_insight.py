# register_face_insight.py
import cv2
import numpy as np
import os
import insightface

# Create embedding folder
os.makedirs("data/embeddings", exist_ok=True)

# Load model
model = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
model.prepare(ctx_id=0)

def register_face(user_name):
    cap = cv2.VideoCapture(0)
    print("[INFO] Look straight into the camera...")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        faces = model.get(frame)
        for face in faces:
            # Draw box
            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            # Extract embedding
            embedding = face.embedding
            # Save embedding
            np.save(f"data/embeddings/{user_name.lower()}.npy", embedding)
            print(f"[INFO] Face registered for {user_name}.")
            cap.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow("Register Face - Press 'q' to exit", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    user_name = input("Enter your name for face registration: ")
    register_face(user_name)
