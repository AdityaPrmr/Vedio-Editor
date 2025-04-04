from flask import Flask, request, jsonify, send_file, render_template
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
from moviepy.video.fx import all as vfx
from moviepy.editor import VideoFileClip, AudioFileClip

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Variable to store the path of the trimmed video
trimmed_video_path = None
video_with_audio_path = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trim', methods=['POST'])
def trim_video():
    global trimmed_video_path

    video = request.files['video']
    start = float(request.form['start'])
    end = float(request.form['end'])
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(input_path)

    trimmed_video_path = os.path.join(app.config['UPLOAD_FOLDER'], f'trimmed_{video.filename}')
    video_clip = VideoFileClip(input_path).subclip(start, end)
    video_clip.write_videofile(trimmed_video_path, codec='libx264')

    return jsonify({'fileUrl': f'/download/{os.path.basename(trimmed_video_path)}'})

@app.route('/add_audio', methods=['POST'])
def add_audio():
    global video_with_audio_path

    if not trimmed_video_path:
        return jsonify({'error': 'No trimmed video available'}), 400

    video = VideoFileClip(trimmed_video_path)
    audio = request.files['audio']
    audio_start = float(request.form['audio-start'])
    audio_end = float(request.form['audio-end'])

    video_with_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video_with_audio.mp4')
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)

    audio.save(audio_path)

    # Load audio and trim to the specified range
    audio_clip = AudioFileClip(audio_path).subclip(audio_start, audio_end)
    
    # Ensure audio length does not exceed video length
    if audio_clip.duration > video.duration:
        audio_clip = audio_clip.subclip(0, video.duration)

    video_with_audio = video.set_audio(audio_clip)
    video_with_audio.write_videofile(video_with_audio_path, codec='libx264')

    return jsonify({'fileUrl': f'/download/{os.path.basename(video_with_audio_path)}'})

@app.route('/remove_audio', methods=['POST'])
def remove_audio():
    global video_with_audio_path

    if not trimmed_video_path:
        return jsonify({'error': 'No trimmed video available'}), 400

    # Remove audio from the trimmed video
    video = VideoFileClip(trimmed_video_path)
    video_without_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video_without_audio.mp4')
    
    video_without_audio = video.set_audio(None)
    video_without_audio.write_videofile(video_without_audio_path, codec='libx264')

    video_with_audio_path = None  # Reset path to indicate no audio file is set

    return jsonify({'fileUrl': f'/download/{os.path.basename(video_without_audio_path)}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/apply_transition', methods=['POST'])
def apply_transition():
    video_path = request.form['video']
    transition_type = request.form['transition']
    start_time = float(request.form['start'])
    end_time = float(request.form['end'])

    # Load the original video
    video = VideoFileClip(video_path)

    # Split the video into three parts: before, during, and after the transition
    before_transition = video.subclip(0, start_time)
    transition_clip = video.subclip(start_time, end_time)
    after_transition = video.subclip(end_time, video.duration)

    # Apply the selected transition
    if transition_type == 'fade':
        transition_clip = transition_clip.fadein(1).fadeout(1)
    elif transition_type == 'flip':
        transition_clip = transition_clip.fx(vfx.mirror_x)
    elif transition_type == 'rotate':
        transition_clip = transition_clip.rotate(180)
    else:
        return jsonify({'error': 'Invalid transition type'}), 400

    # Concatenate the clips
    final_clip = concatenate_videoclips([before_transition, transition_clip, after_transition])

    # Save the final video
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_video.mp4')
    final_clip.write_videofile(output_path, codec='libx264')

    return jsonify({'fileUrl': f'/download/{os.path.basename(output_path)}'})

if __name__ == '__main__':
    app.run(debug=True)
