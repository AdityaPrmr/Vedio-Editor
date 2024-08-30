from flask import Flask, request, jsonify, send_file, render_template
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trim', methods=['POST'])
def trim_video():
    video = request.files['video']
    start = float(request.form['start'])
    end = float(request.form['end'])
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(input_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'trimmed_{video.filename}')
    video_clip = VideoFileClip(input_path).subclip(start, end)
    video_clip.write_videofile(output_path, codec='libx264')

    return jsonify({'fileUrl': f'/download/{os.path.basename(output_path)}'})

@app.route('/add_audio', methods=['POST'])
def add_audio():
    video = request.files['video']
    audio = request.files['audio']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)

    video.save(video_path)
    audio.save(audio_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'audio_added_{video.filename}')
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    video_with_audio = video_clip.set_audio(audio_clip)
    video_with_audio.write_videofile(output_path, codec='libx264')

    return jsonify({'fileUrl': f'/download/{os.path.basename(output_path)}'})

@app.route('/apply_transition', methods=['POST'])
def apply_transition():
    transition = request.form['transition']
    start = float(request.form['start'])
    end = float(request.form['end'])
    video = request.files['video']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    
    input_path = video_path
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'transition_{transition}_{video.filename}')
    
    video_clip = VideoFileClip(input_path)

    # Define the transition duration (slow for visibility)
    transition_duration = 4  # seconds

    # Create clips for before, transition, and after
    before_transition_clip = video_clip.subclip(0, start)
    transition_clip = video_clip.subclip(start, end)
    after_transition_clip = video_clip.subclip(end, video_clip.duration)
    
    # Apply the specified transition
    if transition == 'fade':
        transition_clip = transition_clip.fx(vfx.fadein, duration=transition_duration).fx(vfx.fadeout, duration=transition_duration)
    elif transition == 'rotate':
        transition_clip = transition_clip.fx(vfx.rotate, angle=90)
    elif transition == 'flip':
        transition_clip = transition_clip.fx(vfx.mirror_x)
    else:
        return jsonify({'error': 'Unsupported transition type'}), 400
    
    # Concatenate clips
    final_clip = concatenate_videoclips([before_transition_clip, transition_clip, after_transition_clip])

    # Write the result to a file
    final_clip.write_videofile(output_path, codec='libx264')

    return jsonify({'fileUrl': f'/download/{os.path.basename(output_path)}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)
