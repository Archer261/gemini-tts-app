from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from script_gen import generate_script, generate_audio

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
AUDIO_FOLDER = 'audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        # Generate script
        script = generate_script(topic)
        
        # Generate audio
        audio_path = generate_audio(script)
        
        # Get just the filename from the path
        audio_filename = os.path.basename(audio_path)
        
        return jsonify({
            'success': True,
            'script': script,
            'audioFile': audio_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)