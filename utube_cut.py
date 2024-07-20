from moviepy.editor import VideoFileClip, concatenate_videoclips

def convert_to_shorts_moviepy(input_file, intro_file, output_file, start_time, end_time):
    try:
        main_clip = VideoFileClip(input_file)
        intro_clip = VideoFileClip(intro_file)

        cut_clip = main_clip.subclip(start_time, end_time)

        rotated_clip = cut_clip.rotate(90)

        final_clip = concatenate_videoclips([intro_clip, rotated_clip])

        final_clip.write_videofile(output_file)

        print(f"Successfully converted and saved as {output_file}")

    except OSError as e:
        print(f"Error processing video: {e}")

input_video = "merged_output.mp4"
intro_video = "rotate.mp4" 
output_video = "shorts_output.mp4"
start_time = 12  
end_time = 24

convert_to_shorts_moviepy(input_video, intro_video, output_video, start_time, end_time) 