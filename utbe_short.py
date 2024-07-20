import os
import subprocess
from datetime import timedelta
import requests
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pytube import YouTube
from rich.console import Console
from rich.progress import track

from utube import extract_transcript, create_vtt_file

console = Console()


def download_yt_video(url: str, download_path: str = "downloads") -> str:
    """Downloads a YouTube video to the specified path."""
    yt = YouTube(url)
    console.print(f"[bold blue]Downloading:[/] {yt.title}")

    # Choose the highest resolution stream that's a progressive video
    video_stream = (
        yt.streams.filter(progressive=True, file_extension="mp4")
        .order_by("resolution")
        .desc()
        .first()
    )

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Download the video
    video_stream.download(download_path)
    console.print(f"[bold green]Downloaded:[/] {yt.title}")
    return os.path.join(download_path, video_stream.default_filename)


def trim_video(
    video_path: str, start_time: str, end_time: str, output_path: str = "output"
) -> str:
    """Trims a video to the specified start and end times."""
    console.print(f"[bold blue]Trimming video:[/] {video_path}")
    video = VideoFileClip(video_path)

    # Convert time strings to seconds
    start_seconds = convert_time_to_seconds(start_time)
    end_seconds = convert_time_to_seconds(end_time)

    # Trim the video
    trimmed_video = video.subclip(start_seconds, end_seconds)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Save the trimmed video
    trimmed_video_path = os.path.join(output_path, "trimmed_video.mp4")
    trimmed_video.write_videofile(trimmed_video_path, codec="libx264")
    console.print(f"[bold green]Trimmed video saved to:[/] {trimmed_video_path}")
    return trimmed_video_path


def get_transcript_from_youtube(video_id: str) -> tuple[str, str]:
    """Fetches the transcript from a YouTube video using its ID."""
    console.print(f"[bold blue]Fetching transcript for video ID:[/] {video_id}")
    return extract_transcript(video_id)


def trim_transcript(
    transcript_text: str, start_time: str, end_time: str
) -> str:
    """Trims a transcript to the specified start and end times."""
    console.print(f"[bold blue]Trimming transcript:[/]")
    start_seconds = convert_time_to_seconds(start_time)
    end_seconds = convert_time_to_seconds(end_time)

    trimmed_transcript = ""
    for line in transcript_text.splitlines():
        if ":" in line:
            try:
                timestamp, text = line.split(":", 1)
                line_start_time, line_end_time = map(float, timestamp.split("-"))

                # Check if this line's timestamp falls within the trim range
                if (
                    line_start_time >= start_seconds
                    and line_end_time <= end_seconds
                ):
                    trimmed_transcript += line + "\n"
            except ValueError:
                # Handle lines that do not contain proper timestamps
                continue
        else:
            # Handle non-timestamp lines (like speaker names)
            trimmed_transcript += line + "\n"

    console.print(
        f"[bold green]Transcript trimmed to times:[/] {start_time} - {end_time}"
    )
    return trimmed_transcript


def convert_time_to_seconds(time_str: str) -> float:
    """Converts a time string in the format HH:MM:SS.sss to seconds."""
    try:
        hours, minutes, seconds_milliseconds = map(
            float, time_str.split(":")
        )
        seconds = (
            hours * 3600 + minutes * 60 + seconds_milliseconds
        )
        return seconds
    except ValueError:
        raise ValueError(
            "Invalid time format. Please use HH:MM:SS.sss (e.g., 00:01:15.500)"
        )


def add_subtitles_to_video(
    video_path: str,
    subtitle_path: str,
    output_path: str = "output",
    font_size: int = 30,
) -> None:
    """Adds subtitles to a video."""
    console.print(f"[bold blue]Adding subtitles to video:[/] {video_path}")
    video = VideoFileClip(video_path)
    # Load the subtitle file
    # This assumes .srt format for now
    subtitles = subtitle_path

    # Create a text clip for each subtitle
    text_clips = []
    with open(subtitles, "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f]

    i = 1
    while i < len(lines):
        if "-->" in lines[i]:
            start, end = lines[i].split(" --> ")
            text = lines[i + 1]

            # Convert VTT timestamps to seconds
            start_time = convert_vtt_time_to_seconds(start)
            end_time = convert_vtt_time_to_seconds(end)

            # Create the text clip
            text_clip = (
                TextClip(
                    text,
                    fontsize=font_size,
                    color="white",
                    font="Arial",  # You can change the font
                    bg_color="black",
                )
                .set_start(start_time)
                .set_end(end_time)
                .set_position(("center", "bottom"))
            )

            text_clips.append(text_clip)
            i += 3  # Skip to the next subtitle block
        else:
            i += 1

    # Combine the video and text clips
    final_video = CompositeVideoClip([video] + text_clips)

    # Save the final video with subtitles
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_video_path = os.path.join(output_path, "final_video.mp4")
    final_video.write_videofile(output_video_path, codec="libx264")
    console.print(f"[bold green]Final video saved to:[/] {output_video_path}")


def convert_vtt_time_to_seconds(vtt_time: str) -> float:
    """Converts a VTT time string (HH:MM:SS.sss) to seconds."""
    try:
        hours, minutes, seconds_milliseconds = vtt_time.split(":")
        seconds, milliseconds = map(float, seconds_milliseconds.split("."))
        total_seconds = (
            int(hours) * 3600 + int(minutes) * 60 + seconds + milliseconds / 1000
        )
        return total_seconds
    except ValueError:
        raise ValueError(
            "Invalid VTT time format. Please use HH:MM:SS.sss (e.g., 00:01:15.500)"
        )


def main():
    video_url = "https://www.youtube.com/watch?v=fLeJJPxua3E"
    start_time = input("Enter the start time (HH:MM:SS.sss): ")
    end_time = input("Enter the end time (HH:MM:SS.sss): ")

    try:
        video_id = video_url.split("=")[1]
        download_path = "downloads"
        video_path = download_yt_video(video_url, download_path)

        trimmed_video_path = trim_video(
            video_path, start_time, end_time, "output"
        )

        (
            full_transcript,
            _,
        ) = get_transcript_from_youtube(video_id)
        trimmed_transcript = trim_transcript(
            full_transcript, start_time, end_time
        )
        subtitle_path = "output/subtitles.vtt"
        create_vtt_file(trimmed_transcript, subtitle_path)

        add_subtitles_to_video(trimmed_video_path, subtitle_path)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


if __name__ == "__main__":
    main()