import re
import json

def srt_to_json(srt_file_path, json_file_path):
    """
    Converts an SRT file to JSON, replacing commas with periods in timecodes.
    """

    data = []
    with open(srt_file_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    subtitle_regex = re.compile(r"\d+\n([\d:,.]+ --> [\d:,.]+)\n(.*?)(?=\n\d+\n|\Z)", re.DOTALL)

    for match in subtitle_regex.finditer(srt_content):
        timecode = match.group(1)
        transcript = match.group(2).strip().replace('\n', ' ')

        start_time, end_time = timecode.split(' --> ')

        # Replace comma with period in timecodes
        data.append({
            "start": start_time.replace(',', '.').strip(),
            "end": end_time.replace(',', '.').strip(),
            "transcript": transcript
        })

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Your file paths
srt_file_path = 'transcript.srt'
json_file_path = 'transcript.json'

srt_to_json(srt_file_path, json_file_path)