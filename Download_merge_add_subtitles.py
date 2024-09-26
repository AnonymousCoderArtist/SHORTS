#best to use it in colab or in GPU
import logging
import os
import moviepy.editor as mpe
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import numpy as np
import json
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_caption(textJSON, framesize, font="Helvetica", color='white', highlight_color='yellow',
                   stroke_color='black', stroke_width=1.5):
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end'] - textJSON['start']

    word_clips = []
    xy_textclips_positions = []

    x_pos = 0
    y_pos = 0
    line_width = 0
    frame_width = framesize[0]
    frame_height = framesize[1]

    x_buffer = frame_width * 1/10
    max_line_width = frame_width - 2 * (x_buffer)
    fontsize = int(frame_height * 0.075)

    space_width = ""
    space_height = ""

    for index, wordJSON in enumerate(textJSON['textcontents']):
        duration = wordJSON['end'] - wordJSON['start']
        word_clip = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color,
                              stroke_color=stroke_color, stroke_width=stroke_width).set_start(textJSON['start']).set_duration(full_duration)
        word_clip_space = TextClip(" ", font=font, fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)

        word_width, word_height = word_clip.size
        space_width, space_height = word_clip_space.size

        if line_width + word_width + space_width <= max_line_width:
            xy_textclips_positions.append({
                "x_pos": x_pos,
                "y_pos": y_pos,
                "width": word_width,
                "height": word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })
            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))
            x_pos = x_pos + word_width + space_width
            line_width = line_width + word_width + space_width
        else:
            x_pos = 0
            y_pos = y_pos + word_height + 10
            line_width = word_width + space_width

            xy_textclips_positions.append({
                "x_pos": x_pos,
                "y_pos": y_pos,
                "width": word_width,
                "height": word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))
            x_pos = word_width + space_width

        word_clips.append(word_clip)
        word_clips.append(word_clip_space)

    for highlight_word in xy_textclips_positions:
        word_clip_highlight = TextClip(highlight_word['word'], font=font, fontsize=fontsize, color=highlight_color,
                                      stroke_color=stroke_color, stroke_width=stroke_width).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
        word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
        word_clips.append(word_clip_highlight)

    return word_clips, xy_textclips_positions

def download_audio(video_id):
    """Downloads the audio from a YouTube video."""
    youtube_link = video_id
    handler = Handler(query=youtube_link)

    for third_query_data in handler.run(format='mp3', quality='128kbps', limit=1):
        audio_path = handler.save(third_query_data, dir=os.getcwd())
        return audio_path

def srt_to_json(srt_file_path, json_file_path):
    """Converts an SRT file to JSON with timecode adjustments for subtitles."""

    data = []
    with open(srt_file_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    subtitle_regex = re.compile(r"\d+\n([\d:,.]+ --> [\d:,.]+)\n(.*?)(?=\n\d+\n|\Z)", re.DOTALL)

    for match in subtitle_regex.finditer(srt_content):
        timecode = match.group(1)
        transcript = match.group(2).strip().replace('\n', ' ')

        start_time_str, end_time_str = timecode.split(' --> ')

        # Convert SRT timecode (HH:MM:SS,mmm) to seconds
        start_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(start_time_str.replace(',', '.').split(':'))))
        end_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(end_time_str.replace(',', '.').split(':'))))

        words = transcript.split()
        word_duration = (end_time - start_time) / len(words) if len(words) > 0 else 0 # Avoid division by zero

        textcontents = []
        current_time = start_time
        for word in words:
            textcontents.append({
                "word": word,
                "start": current_time,
                "end": current_time + word_duration
            })
            current_time += word_duration

        data.append({
            "start": start_time,
            "end": end_time,
            "textcontents": textcontents
        })

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    """Main function to download, merge audio, and add subtitles."""

    video_url = "https://www.youtube.com/watch?v=fLeJJPxua3E"
    subtitle_file = "/content/SHORTS/transcript.srt"
    json_subtitle_file = "/content/SHORTS/transcript.json"

    handler = Handler(video_url)

    try:
        # 1. Download Video
        for video_data in handler.run(format='mp4', quality='720p', limit=1):
            cwd = os.getcwd()
            video_path = handler.save(video_data, dir=cwd)

        # 2. Download Audio
        audio_path = download_audio(video_url)

        # 3. Convert SRT to JSON for subtitles
        srt_to_json(subtitle_file, json_subtitle_file)

        # 4. Load Video, Audio, and Subtitles
        video_clip = mpe.VideoFileClip(video_path)
        audio_clip = mpe.AudioFileClip(audio_path)
        with open(json_subtitle_file, 'r') as f:
            linelevel_subtitles = json.load(f)

        # 5. Create and Add Subtitles
        frame_size = video_clip.size
        all_linelevel_splits = []
        for line in linelevel_subtitles:
            out_clips, positions = create_caption(line, frame_size)

            max_width = 0
            max_height = 0
            for position in positions:
                x_pos, y_pos = position['x_pos'], position['y_pos']
                width, height = position['width'], position['height']
                max_width = max(max_width, x_pos + width)
                max_height = max(max_height, y_pos + height)

            color_clip = ColorClip(size=(int(max_width * 1.1), int(max_height * 1.1)),
                                  color=(64, 64, 64))
            color_clip = color_clip.set_opacity(.6)
            color_clip = color_clip.set_start(line['start']).set_duration(line['end'] - line['start'])
            clip_to_overlay = CompositeVideoClip([color_clip] + out_clips)
            clip_to_overlay = clip_to_overlay.set_position("bottom")
            all_linelevel_splits.append(clip_to_overlay)

        # 6. Combine Audio, Video, and Subtitles
        final_video = CompositeVideoClip([video_clip] + all_linelevel_splits)
        final_video = final_video.set_audio(audio_clip)

        # 7. Save Final Video
        final_video.write_videofile("merged_output_with_audio_subtitles.mp4", codec="libx264", audio_codec="aac", audio = True)

        # 8. Delete Temporary Files (optional)
        os.remove(audio_path)
        os.remove(video_path)


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
