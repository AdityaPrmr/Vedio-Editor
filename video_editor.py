from moviepy.editor import VideoFileClip

def trim_video(input_path, start_time, end_time, output_path):
    video = VideoFileClip(input_path)
    trimmed = video.subclip(start_time, end_time)
    trimmed.write_videofile(output_path, codec="libx264")
    print(f"Trimmed video saved to {output_path}")
