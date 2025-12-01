import cv2
import numpy as np
import os
import json
import insightface
from scipy.spatial.distance import cosine, euclidean
import datetime

# Load models
face_model = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=0)

# Load vote status
VOTE_FILE = "data/votes.json"
os.makedirs("data", exist_ok=True)
if os.path.exists(VOTE_FILE):
    with open(VOTE_FILE, "r") as f:
        votes = json.load(f)
else:
    votes = {}

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

def detect_iris(image):
    """Enhanced iris detection with better preprocessing"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    
    # Apply histogram equalization for better contrast
    gray = cv2.equalizeHist(gray)
    
    # Detect circles using HoughCircles
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=30,
        param1=50, param2=30, minRadius=15, maxRadius=100
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        if len(circles) > 0:
            # Return the most prominent circle (largest radius)
            best_circle = max(circles, key=lambda c: c[2])
            return best_circle
    return None

def extract_iris_features(image, circle):
    """Extract iris features using texture analysis"""
    if circle is None:
        return None
    
    x, y, r = circle
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Create mask for iris region
    mask = np.zeros(gray.shape[:2], dtype="uint8")
    cv2.circle(mask, (x, y), r, 255, -1)
    
    # Extract iris region
    iris_region = cv2.bitwise_and(gray, gray, mask=mask)
    
    # Crop to iris region
    iris_cropped = iris_region[max(0, y-r):min(gray.shape[0], y+r), 
                              max(0, x-r):min(gray.shape[1], x+r)]
    
    if iris_cropped.size == 0:
        return None
    
    # Normalize iris region to fixed size
    iris_normalized = cv2.resize(iris_cropped, (128, 128))
    
    # Extract texture features using Local Binary Pattern approach
    features = []
    
    # Extract statistical features from concentric rings
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
    
    # Extract block-wise features
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

def verify_face_live(user_name):
    """Face verification using InsightFace"""
    user_file = f"data/embeddings/face_{user_name.lower()}.npy"
    if not os.path.exists(user_file):
        print("[ERROR] No registered face found.")
        return False, 0.0

    saved_embedding = np.load(user_file)
    cap = cv2.VideoCapture(0)
    print("[INFO] Look at the camera for face verification...")

    verified = False
    attempts = 0
    confidence = 0.0

    while attempts < 150:
        ret, frame = cap.read()
        if not ret:
            continue

        faces = face_model.get(frame)
        for face in faces:
            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            current_embedding = face.embedding
            distance = cosine(saved_embedding, current_embedding)
            confidence = float(1 - distance)
            
            cv2.putText(frame, f"Face Conf: {confidence:.2f}", 
                       (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            print(f"[DEBUG] Face Distance: {distance:.3f}, Confidence: {confidence:.3f}")
            
            if distance < 0.6:  # Adjusted threshold
                print(f"[INFO] Face Verified. Confidence: {confidence:.3f}")
                verified = True
                break

        cv2.imshow("Verifying Face - Press 'q' to exit", frame)
        if verified or cv2.waitKey(1) == ord('q'):
            break
        attempts += 1

    cap.release()
    cv2.destroyAllWindows()
    return verified, confidence

def verify_iris_live(user_name):
    """Iris verification"""
    user_file = f"data/embeddings/iris_{user_name.lower()}.npy"
    if not os.path.exists(user_file):
        print("[ERROR] No registered iris found.")
        return False, 0.0

    saved_features = np.load(user_file)
    cap = cv2.VideoCapture(0)
    print("[INFO] Look directly at the camera for iris verification...")

    verified = False
    attempts = 0
    confidence = 0.0

    while attempts < 150:
        ret, frame = cap.read()
        if not ret:
            continue

        circle = detect_iris(frame)
        if circle is not None:
            x, y, r = circle
            cv2.circle(frame, (x, y), r, (255, 0, 0), 2)
            cv2.circle(frame, (x, y), 2, (255, 0, 0), 3)
            
            current_features = extract_iris_features(frame, circle)
            if current_features is not None and len(current_features) == len(saved_features):
                distance = euclidean(saved_features, current_features)
                # Normalize distance to confidence
                max_distance = 2000  # Adjusted based on feature range
                confidence = float(max(0, 1 - (distance / max_distance)))
                
                cv2.putText(frame, f"Iris Conf: {confidence:.2f}", 
                           (x-50, y-r-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                
                print(f"[DEBUG] Iris Distance: {distance:.1f}, Confidence: {confidence:.3f}")
                
                if distance < 1000:  # Adjusted threshold
                    print(f"[INFO] Iris Verified. Confidence: {confidence:.3f}")
                    verified = True
                    break

        cv2.imshow("Verifying Iris - Press 'q' to exit", frame)
        if verified or cv2.waitKey(1) == ord('q'):
            break
        attempts += 1

    cap.release()
    cv2.destroyAllWindows()
    return verified, confidence

def multimodal_verification(user_name):
    """Combine face and iris verification with score-level fusion"""
    print("[INFO] Starting multimodal biometric verification...")
    
    # Face verification
    face_verified, face_conf = verify_face_live(user_name)
    print(f"[INFO] Face verification: {face_verified}, Confidence: {face_conf:.3f}")
    
    # Iris verification
    iris_verified, iris_conf = verify_iris_live(user_name)
    print(f"[INFO] Iris verification: {iris_verified}, Confidence: {iris_conf:.3f}")
    
    # Score-level fusion (weighted average)
    face_weight = 0.6
    iris_weight = 0.4
    combined_score = float((face_conf * face_weight) + (iris_conf * iris_weight))
    
    # Decision fusion: Both must be verified OR combined score above threshold
    verified = (face_verified and iris_verified) or (combined_score > 0.65)
    
    print(f"[INFO] Combined Score: {combined_score:.3f}")
    print(f"[INFO] Final Decision: {'VERIFIED' if verified else 'FAILED'}")
    
    return verified, combined_score

def vote(user_name):
    if user_name in votes:
        print("[ERROR] You have already voted.")
        return

    verified, score = multimodal_verification(user_name)
    
    if verified:
        print(f"[SUCCESS] Multimodal verification passed (Score: {score:.3f})")
        print("You can now cast your vote.")
        print("1. BJP\n2. Congress\n3. AAP\n4. Others")
        choice = input("Enter your vote number: ")

        # Create vote record with proper type conversion
        vote_record = {
            "choice": choice,
            "verification_score": float(score),
            "face_verified": True,
            "iris_verified": True,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Convert any numpy types before saving
        votes[user_name] = convert_numpy_types(vote_record)
        
        with open(VOTE_FILE, "w") as f:
            json.dump(votes, f, indent=2)

        print("[SUCCESS] Your vote has been recorded securely.")
    else:
        print(f"[ERROR] Multimodal verification failed (Score: {score:.3f}). Cannot vote.")

if __name__ == "__main__":
    user_name = input("Enter your name for voting: ").lower()
    vote(user_name)
