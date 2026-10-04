import subprocess
import os

input_videos = sorted([
    os.path.join("input", filename)
    for filename in os.listdir("input")
    if filename.lower().endswith(".mp4")
])

if not input_videos:
    print("No MP4 videos found in the input folder.")
    exit()

os.makedirs("output", exist_ok=True)

output_video = "output/montage.mp4"

command = ["ffmpeg"]

# Add all input videos
for video in input_videos:
    command.extend(["-i", video])

# Build the FFmpeg filter
filters = []

for i in range(len(input_videos)):
    filters.append(
        f"[{i}:v]"
        "scale=720:1280:force_original_aspect_ratio=decrease,"
        "pad=720:1280:(ow-iw)/2:(oh-ih)/2,"
        "fps=30,setsar=1,format=yuv420p"
        f"[v{i}]"
    )

    filters.append(
        f"[{i}:a]"
        "aresample=48000"
        f"[a{i}]"
    )

# Build concat inputs
concat_inputs = ""

for i in range(len(input_videos)):
    concat_inputs += f"[v{i}][a{i}]"

filters.append(
    concat_inputs
    + f"concat=n={len(input_videos)}:v=1:a=1[outv][outa]"
)

filter_complex = ";".join(filters)

command.extend([
    "-filter_complex",
    filter_complex,

    "-map", "[outv]",
    "-map", "[outa]",

    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "23",

    "-c:a", "aac",
    "-b:a", "192k",

    "-y",
    output_video
])

subprocess.run(command, check=True)

print()
print("Montage created successfully!")
print(f"Videos combined: {len(input_videos)}")
print(f"Output: {output_video}")