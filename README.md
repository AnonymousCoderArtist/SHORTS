# 🎬 YouTube Video Trimmer & Subtitler ✂️

This Python script allows you to download, trim, and add subtitles to YouTube videos! 

## ✨ Features

* **Download YouTube videos:** 📥 Downloads the highest resolution progressive MP4 stream available.
* **Trim videos:** ✂️ Specify start and end times to extract a portion of the video.
* **Fetch transcripts:** 📝 Retrieves transcripts (if available) from YouTube videos.
* **Trim transcripts:** ✂️  Trims the transcript to match the trimmed video segment.
* **Add subtitles:** 💬  Embeds the trimmed transcript as subtitles directly into the video. 

## 🚀 Getting Started

### 1. Prerequisites

* **Python 3.7+:** Make sure you have Python installed on your system.
* **Required Libraries:** 
    ```bash
    pip install moviepy pytube requests rich utube 
    ```

### 2. Running the Script

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/youtube-video-trimmer.git 
   cd youtube-video-trimmer
   ```
2. **Run the script:**
   ```bash
   python utube_short.py
   ```
3. **Provide Input:**
   * Enter the YouTube video URL.
   * Enter the desired start and end times for trimming (in HH:MM:SS.sss format).

### 3. Output

* **Downloaded Video:** The full video will be downloaded to the `downloads` folder.
* **Trimmed Video:** The trimmed video with subtitles will be saved to the `output` folder as `final_video.mp4`.
* **Subtitle File:** The trimmed transcript in VTT format will be saved to the `output` folder as `subtitles.vtt`.

## ⚙️ Customization

* **Download Path:** You can change the video download path by modifying the `download_path` variable in `main.py`.
* **Output Path:**  You can change the output path for the trimmed video and subtitles by modifying the `output_path` variable in the `trim_video` and `add_subtitles_to_video` functions.
* **Subtitle Font Size:** You can adjust the subtitle font size by changing the `font_size` parameter in the `add_subtitles_to_video` function.

## ⚠️ Notes

* The script relies on external libraries like `moviepy`, `pytube`, `requests`, `rich`, and `utube`. Ensure they are installed correctly.
* Transcripts are not available for all YouTube videos.
* Subtitle timing might not be perfect in all cases due to variations in YouTube's transcript formatting.

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or open issues.

## 📄 License

This project is licensed under the MIT License. 
