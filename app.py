from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import subprocess
import os
import json
import hashlib
from datetime import datetime, date
import sys

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Admin credentials
ADMIN_CREDENTIALS = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest(),
    'election_officer': hashlib.sha256('officer456'.encode()).hexdigest()
}

# Voter database (add dob field; update with your real data)
VOTER_DATABASE = {
    'voter1': {
        'password': hashlib.sha256('password123'.encode()).hexdigest(),
        'name': 'John Doe',
        'aadhar': '123456789012',
        'dob': '2000-01-01'
    },
    'voter2': {
        'password': hashlib.sha256('password456'.encode()).hexdigest(),
        'name': 'Jane Smith',
        'aadhar': '123456789013',
        'dob': '2010-05-10'  # < 18 example
    },
    'voter3': {
        'password': hashlib.sha256('password789'.encode()).hexdigest(),
        'name': 'Bob Johnson',
        'aadhar': '123456789014',
        'dob': '2003-11-30'
    }
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_18_or_above(dob_str):
    """Return True if age >= 18, else False."""
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= 18

def get_voting_stats():
    """Get real-time voting statistics from your biometric system"""
    stats = {
        'total_votes': 0,
        'parties': {},
        'avg_score': 0,
        'methods': {}
    }
    try:
        # Load CLI votes
        cli_votes_file = "data/votes.json"
        if os.path.exists(cli_votes_file):
            with open(cli_votes_file, "r") as f:
                content = f.read().strip()
                if content:
                    cli_votes = json.loads(content)
                    for user, vote_data in cli_votes.items():
                        if isinstance(vote_data, dict):
                            choice = vote_data.get('choice', 'Unknown')
                            party_map = {'1': 'BJP', '2': 'Congress', '3': 'AAP', '4': 'Others'}
                            party = party_map.get(str(choice), 'Unknown')
                            stats['parties'][party] = stats['parties'].get(party, 0) + 1
                            stats['total_votes'] += 1
                            if 'verification_score' in vote_data:
                                stats['avg_score'] += vote_data['verification_score']
                            stats['methods']['CLI'] = stats['methods'].get('CLI', 0) + 1

        # Load GUI votes
        gui_votes_file = "voted_users.json"
        if os.path.exists(gui_votes_file):
            with open(gui_votes_file, "r") as f:
                content = f.read().strip()
                if content:
                    gui_votes = json.loads(content)
                    for user, vote_data in gui_votes.items():
                        if isinstance(vote_data, dict):
                            party = vote_data.get('party', 'Unknown')
                            stats['parties'][party] = stats['parties'].get(party, 0) + 1
                            stats['total_votes'] += 1
                            if 'verification_score' in vote_data:
                                stats['avg_score'] += vote_data['verification_score']
                            stats['methods']['GUI'] = stats['methods'].get('GUI', 0) + 1

        # Calculate average score
        if stats['total_votes'] > 0:
            stats['avg_score'] = stats['avg_score'] / stats['total_votes']
    except Exception as e:
        print(f"Error loading stats: {e}")
    return stats

def check_voter_voted(voter_id):
    """Check if voter has already voted"""
    # Check CLI votes
    cli_votes_file = "data/votes.json"
    if os.path.exists(cli_votes_file):
        try:
            with open(cli_votes_file, "r") as f:
                content = f.read().strip()
                if content:
                    cli_votes = json.loads(content)
                    if voter_id in cli_votes:
                        return True
        except:
            pass

    # Check GUI votes
    gui_votes_file = "voted_users.json"
    if os.path.exists(gui_votes_file):
        try:
            with open(gui_votes_file, "r") as f:
                content = f.read().strip()
                if content:
                    gui_votes = json.loads(content)
                    if voter_id in gui_votes:
                        return True
        except:
            pass

    return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voter-login')
def voter_login():
    return render_template('voter_login.html')

@app.route('/admin-login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/voter-authenticate', methods=['POST'])
def voter_authenticate():
    voter_id = request.form.get('voter_id')
    password = request.form.get('password')

    if voter_id in VOTER_DATABASE:
        stored_password = VOTER_DATABASE[voter_id]['password']
        if hash_password(password) == stored_password:
            # Age check
            dob_str = VOTER_DATABASE[voter_id].get('dob')
            if dob_str and not is_18_or_above(dob_str):
                flash('You are not 18 and you are not eligible to vote', 'error')
                return redirect(url_for('voter_login'))

            if check_voter_voted(voter_id):
                flash('You have already voted!', 'error')
                return redirect(url_for('voter_login'))

            session['voter_id'] = voter_id
            session['voter_name'] = VOTER_DATABASE[voter_id]['name']
            session['user_type'] = 'voter'
            return redirect(url_for('voter_dashboard'))

    flash('Invalid credentials!', 'error')
    return redirect(url_for('voter_login'))

@app.route('/admin-authenticate', methods=['POST'])
def admin_authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in ADMIN_CREDENTIALS:
        if hash_password(password) == ADMIN_CREDENTIALS[username]:
            session['admin_user'] = username
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))

    flash('Invalid admin credentials!', 'error')
    return redirect(url_for('admin_login'))

@app.route('/voter-dashboard')
def voter_dashboard():
    if 'voter_id' not in session:
        return redirect(url_for('voter_login'))
    return render_template('voter_dashboard.html',
                           voter_name=session['voter_name'])

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_user' not in session:
        return redirect(url_for('admin_login'))

    stats = get_voting_stats()
    return render_template('admin_dashboard.html',
                           admin_user=session['admin_user'],
                           stats=stats)

@app.route('/start-biometric-voting', methods=['POST'])
def start_biometric_voting():
    if 'voter_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        if not os.path.exists('gui_main_multimodal.py'):
            return jsonify({'error': 'Biometric system not found. Please ensure gui_main_multimodal.py exists.'}), 500

        process = subprocess.Popen([sys.executable, "gui_main_multimodal.py"])
        return jsonify({
            'status': 'success',
            'message': 'Biometric voting interface started',
            'process_id': process.pid
        })
    except Exception as e:
        return jsonify({'error': f'Failed to start biometric system: {str(e)}'}), 500

@app.route('/generate-results', methods=['POST'])
def generate_results():
    if 'admin_user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        if not os.path.exists('results_visualizer.py'):
            return jsonify({'error': 'Results visualizer not found'}), 500

        result = subprocess.run(
            [sys.executable, "-c",
             "from results_visualizer import VotingResultsVisualizer; v = VotingResultsVisualizer(); v.create_all_visualizations()"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Results generated successfully'})
        else:
            return jsonify({'error': f'Error generating results: {result.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to generate results: {str(e)}'}), 500

@app.route('/clear-all-data', methods=['POST'])
def clear_all_data():
    if 'admin_user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        if os.path.exists('clear_biometric_data.py'):
            subprocess.run([sys.executable, "clear_biometric_data.py"])
        else:
            files_to_clear = ["data/votes.json", "voted_users.json"]
            dirs_to_clear = ["data/embeddings", "registered_faces"]

            for file_path in files_to_clear:
                if os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        json.dump({}, f)

            for dir_path in dirs_to_clear:
                if os.path.exists(dir_path):
                    import shutil
                    shutil.rmtree(dir_path)
                os.makedirs(dir_path, exist_ok=True)

        return jsonify({'status': 'success', 'message': 'All data cleared successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to clear data: {str(e)}'}), 500

@app.route('/get-live-results')
def get_live_results():
    if 'admin_user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    stats = get_voting_stats()
    return jsonify(stats)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/check-backend-status')
def check_backend_status():
    """Check if all backend files are present"""
    required_files = [
        'gui_main_multimodal.py',
        'give_vote_multimodal.py',
        'results_visualizer.py',
        'clear_biometric_data.py'
    ]

    status = {}
    for file in required_files:
        status[file] = os.path.exists(file)

    return jsonify({
        'backend_files': status,
        'all_present': all(status.values())
    })

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/embeddings', exist_ok=True)
    os.makedirs('registered_faces', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    json_files = ['data/votes.json', 'voted_users.json']
    for json_file in json_files:
        if not os.path.exists(json_file):
            with open(json_file, 'w') as f:
                json.dump({}, f)

    print("🔗 Backend Integration Status:")
    required_files = ['gui_main_multimodal.py', 'give_vote_multimodal.py', 'results_visualizer.py']
    for file in required_files:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"   {status} {file}")

    app.run(debug=True, host='0.0.0.0', port=5000)
