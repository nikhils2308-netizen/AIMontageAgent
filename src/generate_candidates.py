import os
import subprocess
import random
import json


# ==================================================
# Configuration
# ==================================================

PLAN_FILE = "output/editing_plan.json"


# ==================================================
# Load AI editing plan
# ==================================================

if not os.path.exists(PLAN_FILE):

    print("AI editing plan not found:")
    print(PLAN_FILE)
    print()
    print("Run ai_planner.py first.")
    exit()


with open(
    PLAN_FILE,
    "r",
    encoding="utf-8"
) as file:

    plan = json.load(file)


print()
print("=" * 60)
print("USING AI EDITING PLAN")
print("=" * 60)

print(
    json.dumps(
        plan,
        indent=2
    )
)


# ==================================================
# Read plan values
# ==================================================

target_duration = int(
    plan.get("duration", 30)
)

pacing = plan.get(
    "pacing",
    "medium"
).lower()

clip_variation = plan.get(
    "clip_variation",
    "medium"
).lower()

style = plan.get(
    "style",
    "balanced"
).lower()


# ==================================================
# Find input videos
# ==================================================

input_videos = sorted([
    os.path.join(
        "input",
        filename
    )
    for filename in os.listdir("input")
    if filename.lower().endswith(".mp4")
])


if not input_videos:

    print("No MP4 videos found in input folder.")
    exit()


os.makedirs(
    "output",
    exist_ok=True
)


# ==================================================
# Check audio streams
# ==================================================

has_audio = []

for video in input_videos:

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a",
            "-show_entries", "stream=index",
            "-of", "json",
            video
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    try:

        data = json.loads(
            result.stdout
        )

    except json.JSONDecodeError:

        data = {}

    has_audio.append(
        len(
            data.get(
                "streams",
                []
            )
        ) > 0
    )


print()
print(
    f"Found {len(input_videos)} input videos."
)


# ==================================================
# Create montage
# ==================================================

def create_montage(
    videos,
    durations,
    output_file
):

    command = [
        "ffmpeg"
    ]


    # ----------------------------------------------
    # Add input videos
    # ----------------------------------------------

    for video in videos:

        command.extend([
            "-i",
            video
        ])


    filters = []


    # ----------------------------------------------
    # Create video/audio streams
    # ----------------------------------------------

    for i, duration in enumerate(durations):

        # Video
        filters.append(
            f"[{i}:v]"
            f"trim=duration={duration},"
            "setpts=PTS-STARTPTS,"
            "scale=720:1280:"
            "force_original_aspect_ratio=decrease,"
            "pad=720:1280:"
            "(ow-iw)/2:(oh-ih)/2,"
            "fps=30,"
            "setsar=1,"
            "format=yuv420p"
            f"[v{i}]"
        )


        # Audio
        if has_audio[
            input_videos.index(
                videos[i]
            )
        ]:

            filters.append(
                f"[{i}:a]"
                f"atrim=duration={duration},"
                "asetpts=PTS-STARTPTS,"
                "aresample=48000,"
                "aformat="
                "sample_fmts=fltp:"
                "sample_rates=48000:"
                "channel_layouts=stereo"
                f"[a{i}]"
            )

        else:

            filters.append(
                "anullsrc="
                "channel_layout=stereo:"
                "sample_rate=48000,"
                f"atrim=duration={duration},"
                "asetpts=PTS-STARTPTS"
                f"[a{i}]"
            )


    # ----------------------------------------------
    # Concatenate
    # ----------------------------------------------

    concat_inputs = ""

    for i in range(
        len(videos)
    ):

        concat_inputs += (
            f"[v{i}][a{i}]"
        )


    filters.append(
        concat_inputs
        + f"concat="
        f"n={len(videos)}:"
        "v=1:a=1"
        "[outv][outa]"
    )


    filter_complex = ";".join(
        filters
    )


    command.extend([
        "-filter_complex",
        filter_complex,

        "-map",
        "[outv]",

        "-map",
        "[outa]",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-y",

        output_file
    ])


    subprocess.run(
        command,
        check=True
    )


# ==================================================
# Calculate clip durations
# ==================================================

number_of_clips = len(
    input_videos
)


base_duration = (
    target_duration
    / number_of_clips
)


# ==================================================
# Candidate 1
#
# AI pacing controls duration
# ==================================================

if pacing == "fast":

    candidate_1_duration = max(
        2,
        base_duration * 0.65
    )

elif pacing == "slow":

    candidate_1_duration = (
        base_duration * 1.25
    )

else:

    candidate_1_duration = (
        base_duration
    )


durations_1 = [
    candidate_1_duration
] * number_of_clips


create_montage(
    input_videos,
    durations_1,
    "output/montage_1.mp4"
)


print(
    "Candidate 1 created."
)


# ==================================================
# Candidate 2
#
# Different order + different pacing
# ==================================================

videos_2 = list(
    reversed(input_videos)
)


if pacing == "fast":

    candidate_2_duration = (
        base_duration * 0.85
    )

elif pacing == "slow":

    candidate_2_duration = (
        base_duration * 1.35
    )

else:

    candidate_2_duration = (
        base_duration * 1.10
    )


durations_2 = [
    candidate_2_duration
] * number_of_clips


create_montage(
    videos_2,
    durations_2,
    "output/montage_2.mp4"
)


print(
    "Candidate 2 created."
)


# ==================================================
# Candidate 3
#
# Variation controlled by AI
# ==================================================

videos_3 = input_videos.copy()

random.shuffle(
    videos_3
)


durations_3 = []


for _ in videos_3:

    if clip_variation == "high":

        variation = random.uniform(
            0.35,
            1.25
        )

    elif clip_variation == "low":

        variation = random.uniform(
            0.85,
            1.15
        )

    else:

        variation = random.uniform(
            0.60,
            1.10
        )


    duration = (
        base_duration
        * variation
    )


    duration = max(
        2,
        duration
    )


    durations_3.append(
        duration
    )


create_montage(
    videos_3,
    durations_3,
    "output/montage_3.mp4"
)


print(
    "Candidate 3 created."
)


# ==================================================
# Finished
# ==================================================

print()
print("=" * 60)
print("AI-GUIDED CANDIDATES CREATED")
print("=" * 60)

print(
    f"Style: {style}"
)

print(
    f"Pacing: {pacing}"
)

print(
    f"Target duration: "
    f"{target_duration} seconds"
)

print(
    f"Clip variation: "
    f"{clip_variation}"
)

print()
print(
    "Created:"
)

print(
    "output/montage_1.mp4"
)

print(
    "output/montage_2.mp4"
)

print(
    "output/montage_3.mp4"
)