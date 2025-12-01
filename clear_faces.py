import os
import shutil
import json

def clear_all_data():
    """Clear all biometric data and votes"""
    
    directories_to_clear = [
        "data/embeddings",
        "registered_faces"
    ]
    
    files_to_clear = [
        "data/votes.json",
        "voted_users.json"
    ]
    
    # Clear directories
    for directory in directories_to_clear:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                os.makedirs(directory, exist_ok=True)
                print(f"[INFO] Cleared directory: {directory}")
            except Exception as e:
                print(f"[ERROR] Could not clear {directory}: {e}")
    
    # Clear files
    for file_path in files_to_clear:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[INFO] Removed file: {file_path}")
            except Exception as e:
                print(f"[ERROR] Could not remove {file_path}: {e}")
    
    # Recreate necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)
    os.makedirs("registered_faces", exist_ok=True)
    
    print("[SUCCESS] All biometric data and votes cleared successfully.")

if __name__ == "__main__":
    confirmation = input("Are you sure you want to clear all data? (yes/no): ")
    if confirmation.lower() == "yes":
        clear_all_data()
    else:
        print("Operation cancelled.")
