from flask import Flask, request, jsonify, send_file
import subprocess
import os

app = Flask(__name__)

@app.post("/register")
def register():
    data = request.json
    name = data["name"]
    usn = data["usn"]
    sem = data["sem"]
    dept = data["dept"]
    subprocess.Popen(["python", "gui_main_multimodal.py"])
    return jsonify({"status": "started multimodal GUI"}), 200

@app.post("/vote")
def vote():
    data = request.json
    name = data["name"]
    subprocess.Popen(["python", "give_vote_multimodal.py"], stdin=subprocess.PIPE)
    return jsonify({"status": "multimodal vote started"}), 200

@app.post("/clear_votes")
def clear_votes():
    subprocess.run(["python", "clear_biometric_data.py"])
    return jsonify({"status": "biometric data cleared"}), 200

@app.get("/results")
def show_results():
    """Generate and display voting results"""
    subprocess.run(["python", "results_visualizer.py"])
    return jsonify({"status": "results generated"}), 200

@app.get("/results/download/<chart_name>")
def download_chart(chart_name):
    """Download specific chart"""
    chart_path = f"results/{chart_name}.png"
    if os.path.exists(chart_path):
        return send_file(chart_path, as_attachment=True)
    else:
        return jsonify({"error": "Chart not found"}), 404

if __name__ == "__main__":
    app.run(port=5000)
