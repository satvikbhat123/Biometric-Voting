import os
import json

def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'data',
        'data/embeddings',
        'results',
        'registered_faces'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_css_file():
    """Create the main CSS file"""
    css_content = '''/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* Landing Page Styles */
.landing-container {
    min-height: 100vh;
    position: relative;
    overflow: hidden;
}

/* Animated Background */
.bg-animation {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
}

.bg-circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    animation: float 6s ease-in-out infinite;
}

.bg-circle1 {
    width: 300px;
    height: 300px;
    background: #ff6b6b;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
}

.bg-circle2 {
    width: 200px;
    height: 200px;
    background: #4ecdc4;
    top: 60%;
    right: 10%;
    animation-delay: 2s;
}

.bg-circle3 {
    width: 150px;
    height: 150px;
    background: #45b7d1;
    bottom: 20%;
    left: 60%;
    animation-delay: 4s;
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(10deg); }
}

/* Header */
.main-header {
    text-align: center;
    padding: 3rem 1rem;
    color: white;
}

.logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.logo i {
    font-size: 3rem;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo h1 {
    font-size: 3.5rem;
    font-weight: bold;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Add more CSS styles here - this is a condensed version */
.login-btn {
    display: block;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 3rem 2rem;
    text-decoration: none;
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
    margin: 1rem;
}

.login-btn:hover {
    transform: translateY(-10px);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.btn-content i {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
}

.btn-content span {
    font-size: 1.5rem;
    font-weight: bold;
    display: block;
    margin-bottom: 0.5rem;
}
'''
    
    with open('static/css/style.css', 'w') as f:
        f.write(css_content)
    print("✅ Created CSS file")

def create_js_files():
    """Create JavaScript files"""
    
    # Main JS
    main_js = '''
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Biometric Voting System Loaded');
});

function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const toggle = field.parentElement.querySelector('.password-toggle i');
    
    if (field.type === 'password') {
        field.type = 'text';
        toggle.classList.remove('fa-eye');
        toggle.classList.add('fa-eye-slash');
    } else {
        field.type = 'password';
        toggle.classList.remove('fa-eye-slash');
        toggle.classList.add('fa-eye');
    }
}
'''
    
    with open('static/js/main.js', 'w') as f:
        f.write(main_js)
    
    with open('static/js/auth.js', 'w') as f:
        f.write(main_js)
    
    # Voter JS
    voter_js = '''
function startBiometricVoting() {
    const btn = document.getElementById('voteBtn');
    const status = document.getElementById('voteStatus');
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting Biometric System...';
    
    fetch('/start-biometric-voting', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            status.className = 'vote-status success';
            status.innerHTML = '<i class="fas fa-check-circle"></i> Biometric voting system started!';
            status.style.display = 'block';
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        status.className = 'vote-status error';
        status.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error starting system.';
        status.style.display = 'block';
        
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-fingerprint"></i> START BIOMETRIC VOTING';
    });
}
'''
    
    with open('static/js/voter.js', 'w') as f:
        f.write(voter_js)
    
    # Admin JS
    admin_js = '''
function refreshData() {
    console.log('Refreshing data...');
    location.reload();
}

function generateResults() {
    fetch('/generate-results', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Results generated successfully!');
        }
    })
    .catch(error => {
        alert('Error generating results: ' + error.message);
    });
}

function clearAllData() {
    if (confirm('Are you sure you want to clear all data?')) {
        fetch('/clear-all-data', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('All data cleared successfully!');
                location.reload();
            }
        })
        .catch(error => {
            alert('Error clearing data: ' + error.message);
        });
    }
}

function exportData() { alert('Export functionality coming soon!'); }
function viewLogs() { alert('Logs functionality coming soon!'); }
'''
    
    with open('static/js/admin.js', 'w') as f:
        f.write(admin_js)
    
    print("✅ Created JavaScript files")

def create_sample_templates():
    """Create basic HTML templates"""
    
    # Index template
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Secure Biometric Voting System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="landing-container">
        <div class="bg-animation">
            <div class="bg-circle bg-circle1"></div>
            <div class="bg-circle bg-circle2"></div>
            <div class="bg-circle bg-circle3"></div>
        </div>
        
        <header class="main-header">
            <div class="logo">
                <i class="fas fa-shield-alt"></i>
                <h1>E-Vote Print</h1>
            </div>
            <p class="tagline">Next-Generation Biometric Voting System</p>
        </header>
        
        <main style="text-align: center; padding: 2rem;">
            <h2 style="color: white; margin-bottom: 2rem;">🗳️ Welcome to the Future of Voting</h2>
            
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <a href="{{ url_for('voter_login') }}" class="login-btn" style="max-width: 300px;">
                    <div class="btn-content">
                        <i class="fas fa-user"></i>
                        <span>VOTER LOGIN</span>
                        <p>Cast your secure vote</p>
                    </div>
                </a>
                
                <a href="{{ url_for('admin_login') }}" class="login-btn" style="max-width: 300px;">
                    <div class="btn-content">
                        <i class="fas fa-user-shield"></i>
                        <span>ADMIN LOGIN</span>
                        <p>Manage election system</p>
                    </div>
                </a>
            </div>
        </main>
    </div>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>'''
    
    # Voter login template
    voter_login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voter Login -  E-Vote Print</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body style="display: flex; align-items: center; justify-content: center; min-height: 100vh;">
    <div style="background: white; padding: 3rem; border-radius: 20px; max-width: 400px; width: 100%; margin: 2rem;">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="width: 80px; height: 80px; background: linear-gradient(45deg, #4ecdc4, #44a08d); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                <i class="fas fa-user" style="font-size: 2rem; color: white;"></i>
            </div>
            <h2>Voter Login</h2>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div style="padding: 1rem; margin-bottom: 1rem; border-radius: 10px; background: {{ '#ffe6e6' if category == 'error' else '#e6f7e1' }}; color: {{ '#d63031' if category == 'error' else '#00b894' }};">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form action="{{ url_for('voter_authenticate') }}" method="POST">
            <div style="margin-bottom: 1.5rem;">
                <label style="display: block; margin-bottom: 0.5rem;"><i class="fas fa-id-card"></i> Voter ID</label>
                <input type="text" name="voter_id" required style="width: 100%; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 10px;">
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <label style="display: block; margin-bottom: 0.5rem;"><i class="fas fa-lock"></i> Password</label>
                <input type="password" id="password" name="password" required style="width: 100%; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 10px;">
            </div>
            
            <button type="submit" style="width: 100%; padding: 1rem; background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">
                <i class="fas fa-sign-in-alt"></i> LOGIN TO VOTE
            </button>
        </form>
        
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <h4>Demo Credentials:</h4>
            <p><strong>Voter ID:</strong> voter1 | <strong>Password:</strong> password123</p>
        </div>
        
        <div style="text-align: center; margin-top: 1rem;">
            <a href="{{ url_for('index') }}" style="color: #666; text-decoration: none;">← Back to Home</a>
        </div>
    </div>
</body>
</html>'''

    # Save templates
    templates = {
        'index.html': index_html,
        'voter_login.html': voter_login_html,
        'admin_login.html': voter_login_html.replace('voter_login', 'admin_login').replace('voter_authenticate', 'admin_authenticate').replace('Voter', 'Admin').replace('voter_id', 'username').replace('Voter ID', 'Username'),
        'voter_dashboard.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Voter Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; background: #f0f0f0;">
    <div style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center;">
        <h1><i class="fas fa-shield-alt"></i>  E-Vote Print</h1>
        <div>
            Welcome, {{ voter_name }} | <a href="{{ url_for('logout') }}" style="color: white;">Logout</a>
        </div>
    </div>
    
    <div style="max-width: 800px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 15px;">
        <h2 style="text-align: center;"><i class="fas fa-vote-yea"></i> Cast Your Vote</h2>
        
        <div style="text-align: center; margin: 2rem 0;">
            <button onclick="startBiometricVoting()" id="voteBtn" style="background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; border: none; padding: 1.5rem 3rem; border-radius: 15px; font-size: 1.2rem; cursor: pointer;">
                <i class="fas fa-fingerprint"></i> START BIOMETRIC VOTING
            </button>
        </div>
        
        <div id="voteStatus" style="display: none;"></div>
    </div>
    
    <script src="{{ url_for('static', filename='js/voter.js') }}"></script>
</body>
</html>''',
        'admin_dashboard.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; background: #f0f0f0;">
    <div style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center;">
        <h1><i class="fas fa-shield-alt"></i> SecureVote Admin</h1>
        <div>
            Admin: {{ admin_user }} | <a href="{{ url_for('logout') }}" style="color: white;">Logout</a>
        </div>
    </div>
    
    <div style="max-width: 1200px; margin: 2rem auto; padding: 2rem;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center;">
                <h3>{{ stats.total_votes }}</h3>
                <p>Total Votes</p>
            </div>
            <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center;">
                <h3>{{ stats.parties|length }}</h3>
                <p>Active Parties</p>
            </div>
        </div>
        
        <div style="background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
            <h3>Control Panel</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <button onclick="generateResults()" style="padding: 1rem; background: #4ecdc4; color: white; border: none; border-radius: 10px; cursor: pointer;">
                    <i class="fas fa-chart-bar"></i> Generate Reports
                </button>
                <button onclick="clearAllData()" style="padding: 1rem; background: #ff7675; color: white; border: none; border-radius: 10px; cursor: pointer;">
                    <i class="fas fa-trash"></i> Clear All Data
                </button>
            </div>
        </div>
        
        <div style="background: white; padding: 2rem; border-radius: 15px;">
            <h3>Live Results</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 1rem; text-align: left;">Party</th>
                        <th style="padding: 1rem; text-align: left;">Votes</th>
                        <th style="padding: 1rem; text-align: left;">Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {% for party, votes in stats.parties.items() %}
                    <tr>
                        <td style="padding: 1rem; border-bottom: 1px solid #eee;">{{ party }}</td>
                        <td style="padding: 1rem; border-bottom: 1px solid #eee;">{{ votes }}</td>
                        <td style="padding: 1rem; border-bottom: 1px solid #eee;">{{ "%.1f"|format((votes / stats.total_votes * 100) if stats.total_votes > 0 else 0) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/admin.js') }}"></script>
</body>
</html>'''
    }
    
    for filename, content in templates.items():
        with open(f'templates/{filename}', 'w') as f:
            f.write(content)
    print(f"✅ Created {len(templates)} template files")

def create_empty_json_files():
    """Create empty JSON files to prevent errors"""
    json_files = {
        'data/votes.json': {},
        'voted_users.json': {}
    }
    
    for filepath, content in json_files.items():
        with open(filepath, 'w') as f:
            json.dump(content, f)
    print("✅ Created JSON data files")

def main():
    print("🚀 Setting up Biometric Voting Web Application")
    print("="*60)
    
    create_directory_structure()
    create_css_file()
    create_js_files()
    create_sample_templates()
    create_empty_json_files()
    
    print("\n✅ Setup completed successfully!")
    print("="*60)
    print("📌 Next steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Demo credentials:")
    print("   • Voter: voter1 / password123")
    print("   • Admin: admin / admin123")

if __name__ == "__main__":
    main()
