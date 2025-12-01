import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import insightface
import numpy as np
import os
import json
import threading
import pyttsx3
from scipy.spatial.distance import euclidean
import datetime
from datetime import date

# Load the face model
face_model = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=0, det_size=(640, 640))

# Load voting status
voted_users_file = "voted_users.json"
if os.path.exists(voted_users_file):
    try:
        with open(voted_users_file, "r") as f:
            voted_users = json.load(f)
    except json.decoder.JSONDecodeError:
        voted_users = {}
else:
    voted_users = {}

# Voice engine
try:
    engine = pyttsx3.init()
    voice_enabled = True
except:
    voice_enabled = False
    print("[WARNING] Voice engine not available")

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

def speak(text):
    if voice_enabled:
        def _speak():
            try:
                engine.say(text)
                engine.runAndWait()
            except:
                pass
        threading.Thread(target=_speak).start()

def is_18_or_above(dob_str):
    """Return True if age >= 18; invalid format -> False."""
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= 18

def detect_iris(image):
    """Detect iris in the image"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    gray = cv2.equalizeHist(gray)

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30,
        param1=50, param2=30, minRadius=15, maxRadius=100
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        if len(circles) > 0:
            return max(circles, key=lambda c: c[2])
    return None

def extract_iris_features(image, circle):
    """Extract iris features"""
    if circle is None:
        return None

    x, y, r = circle
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    mask = np.zeros(gray.shape[:2], dtype="uint8")
    cv2.circle(mask, (x, y), r, 255, -1)

    iris_region = cv2.bitwise_and(gray, gray, mask=mask)

    iris_cropped = iris_region[max(0, y-r):min(gray.shape[0], y+r),
                               max(0, x-r):min(gray.shape[1], x+r)]

    if iris_cropped.size == 0:
        return None

    iris_normalized = cv2.resize(iris_cropped, (128, 128))

    features = []

    center = (64, 64)
    for radius in [20, 35, 50]:
        ring_mask = np.zeros((128, 128), dtype=np.uint8)
        cv2.circle(ring_mask, center, radius, 255, 3)
        ring_pixels = iris_normalized[ring_mask > 0]

        if len(ring_pixels) > 0:
            features.extend([
                np.mean(ring_pixels),
                np.std(ring_pixels),
                np.median(ring_pixels),
                np.var(ring_pixels)
            ])

    block_size = 16
    for i in range(0, 128, block_size):
        for j in range(0, 128, block_size):
            block = iris_normalized[i:i+block_size, j:j+block_size]
            if block.size > 0:
                features.extend([
                    np.mean(block),
                    np.std(block)
                ])

    return np.array(features)

def validate_inputs():
    return (user_entry.get().strip() != "" and
            aadhar_entry.get().strip() != "" and
            dob_entry.get().strip() != "")

def register_multimodal():
    if not validate_inputs():
        messagebox.showerror("Error", "Please fill all fields: Name, Aadhar Number and DOB")
        return

    user_name = user_entry.get().lower().strip()
    aadhar = aadhar_entry.get().strip()
    dob_str = dob_entry.get().strip()

    if len(aadhar) != 12 or not aadhar.isdigit():
        messagebox.showerror("Error", "Aadhar Number must be 12 digits")
        return

    # Age check
    if not is_18_or_above(dob_str):
        messagebox.showerror("Not Eligible", "You are not 18 and you are not eligible to vote")
        speak("You are not 18 and you are not eligible to vote")
        return

    os.makedirs("registered_faces", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)

    cap = cv2.VideoCapture(0)
    speak(f"Registration started for {user_name}. First, show your face clearly.")

    face_registered = False
    iris_registered = False

    print("[INFO] Registration started. Press 'f' to capture face, 'i' to capture iris")

    while not (face_registered and iris_registered):
        ret, frame = cap.read()
        if not ret:
            continue

        display_frame = frame.copy()

        # Face detection
        if not face_registered:
            faces = face_model.get(frame)
            for face in faces:
                bbox = face.bbox.astype(int)
                cv2.rectangle(display_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                cv2.putText(display_frame, "Press 'f' to save face", (bbox[0], bbox[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Iris detection
        if not iris_registered:
            circle = detect_iris(frame)
            if circle is not None:
                x, y, r = circle
                cv2.circle(display_frame, (x, y), r, (255, 0, 0), 2)
                cv2.circle(display_frame, (x, y), 2, (255, 0, 0), 3)
                cv2.putText(display_frame, "Press 'i' to save iris", (x-50, y-r-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        status_text = f"Face: {'✓' if face_registered else '✗'} | Iris: {'✓' if iris_registered else '✗'}"
        cv2.putText(display_frame, status_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("Multimodal Registration", display_frame)
        key = cv2.waitKey(1)

        # Save face
        if key == ord('f') and not face_registered:
            faces = face_model.get(frame)
            if faces:
                face = faces[0]
                np.save(f"data/embeddings/face_{user_name}.npy", face.normed_embedding)
                face_registered = True
                speak("Face registered successfully")
                print("[INFO] Face registered successfully")

        # Save iris
        if key == ord('i') and not iris_registered:
            circle = detect_iris(frame)
            if circle is not None:
                iris_features = extract_iris_features(frame, circle)
                if iris_features is not None:
                    np.save(f"data/embeddings/iris_{user_name}.npy", iris_features)
                    iris_registered = True
                    speak("Iris registered successfully")
                    print("[INFO] Iris registered successfully")
                else:
                    print("[WARNING] Could not extract iris features. Try again.")

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if face_registered and iris_registered:
        details_file = f"registered_faces/{user_name}_details.json"
        details = {
            "aadhar": aadhar,
            "dob": dob_str,
            "biometrics": ["face", "iris"],
            "registration_date": datetime.datetime.now().isoformat()
        }
        with open(details_file, "w") as f:
            json.dump(details, f, indent=2)

        messagebox.showinfo("Registration Complete",
                            f"Both face and iris registered for {user_name}")
        speak(f"Registration completed successfully for {user_name}")
    else:
        messagebox.showwarning("Incomplete Registration",
                               "Please register both face and iris biometrics")

def multimodal_vote():
    if not validate_inputs():
        messagebox.showerror("Error", "Please fill all fields: Name, Aadhar Number and DOB")
        return

    user_name = user_entry.get().lower().strip()
    aadhar = aadhar_entry.get().strip()

    if user_name in voted_users:
        messagebox.showerror("Error", f"{user_name} has already voted!")
        speak(f"{user_name}, you have already voted")
        return

    face_path = f"data/embeddings/face_{user_name}.npy"
    iris_path = f"data/embeddings/iris_{user_name}.npy"
    details_file = f"registered_faces/{user_name}_details.json"

    if not all(os.path.exists(path) for path in [face_path, iris_path, details_file]):
        messagebox.showerror("Error", "Complete biometric registration not found")
        return

    with open(details_file, "r") as f:
        details = json.load(f)
    if details.get("aadhar") != aadhar:
        messagebox.showerror("Error", "Aadhar Number does not match registration")
        return

    registered_face = np.load(face_path)
    registered_iris = np.load(iris_path)

    cap = cv2.VideoCapture(0)
    speak(f"{user_name}, please show your face and iris for verification")

    face_verified = False
    iris_verified = False
    face_confidence = 0.0
    iris_confidence = 0.0
    attempts = 0

    print("[INFO] Verification started. Looking for face and iris...")

    while attempts < 200 and not (face_verified and iris_verified):
        ret, frame = cap.read()
        if not ret:
            continue

        display_frame = frame.copy()

        # Face verification
        faces = face_model.get(frame)
        for face in faces:
            bbox = face.bbox.astype(int)
            face_dist = np.linalg.norm(face.normed_embedding - registered_face)
            face_confidence = float(max(0, 1 - face_dist))

            color = (0, 255, 0) if face_dist < 1.2 else (0, 0, 255)
            cv2.rectangle(display_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(display_frame, f"Face: {face_confidence:.2f}",
                        (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if face_dist < 1.2:
                face_verified = True

        # Iris verification
        circle = detect_iris(frame)
        if circle is not None:
            x, y, r = circle
            iris_features = extract_iris_features(frame, circle)
            if iris_features is not None and len(iris_features) == len(registered_iris):
                iris_dist = euclidean(registered_iris, iris_features)
                max_distance = 2000
                iris_confidence = float(max(0, 1 - (iris_dist / max_distance)))

                color = (255, 0, 0) if iris_dist < 1000 else (0, 0, 255)
                cv2.circle(display_frame, (x, y), r, color, 2)
                cv2.putText(display_frame, f"Iris: {iris_confidence:.2f}",
                            (x-50, y-r-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if iris_dist < 1000:
                    iris_verified = True

        status = f"Face: {'✓' if face_verified else '✗'} | Iris: {'✓' if iris_verified else '✗'}"
        cv2.putText(display_frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("Multimodal Voting Verification", display_frame)
        if cv2.waitKey(1) == ord('q'):
            break
        attempts += 1

    cap.release()
    cv2.destroyAllWindows()

    combined_score = float((face_confidence * 0.6) + (iris_confidence * 0.4))
    final_verified = (face_verified and iris_verified) or (combined_score > 0.65)

    print(f"[INFO] Face: {face_verified} ({face_confidence:.3f}), Iris: {iris_verified} ({iris_confidence:.3f})")
    print(f"[INFO] Combined Score: {combined_score:.3f}, Final: {final_verified}")

    if final_verified:
        speak("Biometric verification successful. You can now cast your vote.")
        show_vote_options(user_name, combined_score)
    else:
        messagebox.showerror("Verification Failed",
                             f"Multimodal verification failed. Combined score: {combined_score:.2f}")
        speak("Biometric verification failed")

def show_vote_options(user_name, verification_score):
    def record_vote(party):
        vote_record = {
            "party": party,
            "verification_score": float(verification_score),
            "timestamp": datetime.datetime.now().isoformat(),
            "verification_method": "multimodal"
        }

        voted_users[user_name] = convert_numpy_types(vote_record)

        with open(voted_users_file, "w") as f:
            json.dump(voted_users, f, indent=2)

        messagebox.showinfo("Vote Recorded", f"Your vote for {party} has been recorded")
        speak(f"Your vote for {party} has been recorded. Thank you for voting.")
        vote_window.destroy()

    vote_window = tk.Toplevel(root)
    vote_window.title("Cast Your Vote")
    vote_window.geometry("400x400")
    vote_window.configure(bg="lightblue")

    tk.Label(vote_window, text="🗳️ CAST YOUR VOTE 🗳️",
             font=("Arial", 16, "bold"), bg="lightblue").pack(pady=20)
    tk.Label(vote_window, text=f"Verification Score: {float(verification_score):.2f}",
             font=("Arial", 10), fg="gray", bg="lightblue").pack()

    parties = ["BJP", "Congress", "JD(S)", "AAP"]
    colors = ["orange", "lightgreen", "yellow", "lightcoral"]

    for i, (party, color) in enumerate(zip(parties, colors), 1):
        btn = tk.Button(vote_window, text=f"{i}. {party}", font=("Arial", 12, "bold"),
                        width=20, height=2, bg=color,
                        command=lambda p=party: record_vote(p))
        btn.pack(pady=8)

# GUI setup
root = tk.Tk()
root.title("Smart Multimodal Voting System")
root.geometry("700x500")
root.configure(bg="lightgray")

# Header
header_frame = tk.Frame(root, bg="darkblue", height=80)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

header_label = tk.Label(header_frame, text="🔐 Multimodal Biometric Voting System 🔐",
                        font=("Arial", 20, "bold"), fg="white", bg="darkblue")
header_label.pack(expand=True)

# Description
desc_frame = tk.Frame(root, bg="lightgray")
desc_frame.pack(pady=10)
desc_label = tk.Label(desc_frame,
                      text="Secure voting using Face + Iris recognition technology",
                      font=("Arial", 12), fg="darkblue", bg="lightgray")
desc_label.pack()

# Input fields frame
input_frame = tk.LabelFrame(root, text="Voter Information", font=("Arial", 12, "bold"),
                            bg="white", padx=20, pady=20)
input_frame.pack(pady=20, padx=50, fill="x")

tk.Label(input_frame, text="👤 Enter your Name:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=10)
user_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
user_entry.grid(row=0, column=1, padx=5, pady=10)

tk.Label(input_frame, text="🆔 Enter Aadhar Number:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=10)
aadhar_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
aadhar_entry.grid(row=1, column=1, padx=5, pady=10)

tk.Label(input_frame, text="📅 Enter DOB (YYYY-MM-DD):", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=10)
dob_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
dob_entry.grid(row=2, column=1, padx=5, pady=10)

# Buttons frame
button_frame = tk.Frame(root, bg="lightgray")
button_frame.pack(pady=30)

register_btn = tk.Button(
    button_frame,
    text="📝 Register\n(Face + Iris)",
    font=("Arial", 12, "bold"),
    width=15,
    height=3,
    bg="lightgreen",
    fg="darkgreen",
    command=lambda: threading.Thread(target=register_multimodal).start()
)
register_btn.grid(row=0, column=0, padx=30)

vote_btn = tk.Button(
    button_frame,
    text="🗳️ Vote\n(Multimodal)",
    font=("Arial", 12, "bold"),
    width=15,
    height=3,
    bg="lightblue",
    fg="darkblue",
    command=lambda: threading.Thread(target=multimodal_vote).start()
)
vote_btn.grid(row=0, column=1, padx=30)

# Info frame
info_frame = tk.LabelFrame(root, text="Instructions", font=("Arial", 10, "bold"),
                           bg="lightyellow", padx=10, pady=10)
info_frame.pack(pady=20, padx=50, fill="x")

instructions = [
    "1. Registration: Capture both face and iris biometrics",
    "2. Voting: Both biometrics verified for maximum security",
    "3. Press 'f' to capture face, 'i' to capture iris",
    "4. Ensure good lighting for accurate detection"
]

for instruction in instructions:
    tk.Label(info_frame, text=instruction, font=("Arial", 9),
             justify="left", bg="lightyellow").pack(anchor="w")

# Status bar
status_bar = tk.Label(
    root,
    text="Ready - Please fill in your details",
    font=("Arial", 10),
    relief=tk.SUNKEN,
    anchor="w",
    bg="white"
)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()

