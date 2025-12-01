import os
import subprocess
import sys

def start_application():
    """Start the biometric voting web application"""
    
    print("🚀 Starting Biometric Voting System Web Application")
    print("="*60)
    
    # Check if required directories exist
    directories = ['templates', 'static/css', 'static/js', 'data', 'results']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
    
    # Start the Flask application
    print("\n🌐 Starting web server...")
    print("📱 Access the application at: http://localhost:5000")
    print("🗳️ Voter Login: http://localhost:5000/voter-login")
    print("👨‍💼 Admin Login: http://localhost:5000/admin-login")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    try:
        # Start the web application
        subprocess.run([sys.executable, "web_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    start_application()
