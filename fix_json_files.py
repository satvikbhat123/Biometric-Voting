import json
import os

def fix_json_files():
    """Fix corrupted or empty JSON files"""
    
    files_to_fix = [
        "data/votes.json",
        "voted_users.json"
    ]
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    
    for file_path in files_to_fix:
        try:
            # Try to read the file
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read().strip()
                if not content:
                    # File is empty, write empty JSON object
                    with open(file_path, "w") as f:
                        json.dump({}, f)
                    print(f"✅ Fixed empty file: {file_path}")
                else:
                    # Try to parse JSON
                    json.loads(content)
                    print(f"✅ File is valid: {file_path}")
            else:
                # File doesn't exist, create it
                with open(file_path, "w") as f:
                    json.dump({}, f)
                print(f"✅ Created missing file: {file_path}")
        except json.JSONDecodeError:
            # File has invalid JSON, fix it
            with open(file_path, "w") as f:
                json.dump({}, f)
            print(f"✅ Fixed corrupted JSON: {file_path}")
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print("\n🔧 JSON file repair completed!")

if __name__ == "__main__":
    fix_json_files()
