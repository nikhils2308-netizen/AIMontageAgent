import os
import cv2
import shutil

# ==================================================
# Montage files
# ==================================================

montages = [
    "output/montage_1.mp4",
    "output/montage_2.mp4",
    "output/montage_3.mp4",
]


# ==================================================
# Analyze one video
# ==================================================

def analyze_video(video_path):

    if not os.path.exists(video_path):
        print(f"File not found: {video_path}")
        return None

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Could not open: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    frame_count = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = frame_count / fps

    # Sample approximately 4 frames per second
    sample_interval = max(
        int(fps / 4),
        1
    )

    previous_gray = None

    visual_changes = []

    frame_number = 0

    # ==================================================
    # Read video frames
    # ==================================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_number % sample_interval != 0:
            frame_number += 1
            continue

        # Resize for faster analysis
        small_frame = cv2.resize(
            frame,
            (160, 90)
        )

        # Convert to grayscale
        gray = cv2.cvtColor(
            small_frame,
            cv2.COLOR_BGR2GRAY
        )

        # Compare with previous sampled frame
        if previous_gray is not None:

            difference = cv2.absdiff(
                gray,
                previous_gray
            )

            change_score = float(
                difference.mean()
            )

            visual_changes.append(
                change_score
            )

        previous_gray = gray

        frame_number += 1

    cap.release()


    # ==================================================
    # Calculate visual diversity
    # ==================================================

    if visual_changes:

        average_visual_change = (
            sum(visual_changes)
            / len(visual_changes)
        )

        # Sort visual changes
        sorted_changes = sorted(
            visual_changes
        )

        # Use the top 10% as strong transitions
        index = int(
            len(sorted_changes) * 0.90
        )

        index = min(
            index,
            len(sorted_changes) - 1
        )

        high_change_threshold = (
            sorted_changes[index]
        )

        # Estimate scene changes
        estimated_cuts = sum(
            1
            for change in visual_changes
            if change >= max(
                high_change_threshold,
                18
            )
        )

    else:

        average_visual_change = 0
        estimated_cuts = 0


    # ==================================================
    # Cuts per second
    # ==================================================

    if duration > 0:

        cuts_per_second = (
            estimated_cuts / duration
        )

    else:

        cuts_per_second = 0


    return {
        "duration": duration,
        "frame_count": frame_count,
        "average_visual_change":
            average_visual_change,
        "estimated_cuts":
            estimated_cuts,
        "cuts_per_second":
            cuts_per_second
    }


# ==================================================
# Normalize value to 0-100
# ==================================================

def normalize(value, minimum, maximum):

    if maximum == minimum:
        return 50

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100

    return max(
        0,
        min(100, score)
    )


# ==================================================
# Analyze all montages
# ==================================================

results = []

for montage in montages:

    print()
    print("=" * 50)
    print(f"Analyzing: {montage}")
    print("=" * 50)

    result = analyze_video(montage)

    if result is not None:

        results.append({
            "file": montage,
            **result
        })


# ==================================================
# Make sure results exist
# ==================================================

if not results:

    print("No montage files could be analyzed.")
    exit()


# ==================================================
# Get metric ranges
# ==================================================

visual_values = [
    result["average_visual_change"]
    for result in results
]

cut_values = [
    result["estimated_cuts"]
    for result in results
]


# ==================================================
# Calculate scores
# ==================================================

for result in results:

    # ==================================================
    # Visual diversity score
    # ==================================================

    visual_score = normalize(
        result["average_visual_change"],
        min(visual_values),
        max(visual_values)
    )


    # ==================================================
    # Editing activity score
    # ==================================================

    cut_score = normalize(
        result["estimated_cuts"],
        min(cut_values),
        max(cut_values)
    )


    # ==================================================
    # Pacing score
    #
    # Ideal target:
    # approximately 0.22 cuts per second
    # ==================================================

    cuts_per_second = (
        result["cuts_per_second"]
    )

    pacing_score = (
        100
        - abs(
            cuts_per_second - 0.22
        ) * 300
    )

    pacing_score = max(
        0,
        min(100, pacing_score)
    )


    # ==================================================
    # Duration score
    #
    # TARGET = 30 seconds
    # ==================================================

    duration = result["duration"]

    duration_difference = abs(
        duration - 30
    )

    duration_score = (
        100
        - duration_difference * 2
    )

    duration_score = max(
        0,
        min(100, duration_score)
    )


    # ==================================================
    # Final score
    #
    # Visual diversity = 40%
    # Editing activity = 20%
    # Pacing          = 20%
    # Duration        = 20%
    # ==================================================

    final_score = (
        visual_score * 0.40
        + cut_score * 0.20
        + pacing_score * 0.20
        + duration_score * 0.20
    )


    result["visual_score"] = visual_score
    result["cut_score"] = cut_score
    result["pacing_score"] = pacing_score
    result["duration_score"] = duration_score
    result["final_score"] = final_score


# ==================================================
# Display results
# ==================================================

print()
print()
print("=" * 65)
print("MONTAGE UNIQUENESS SCORES")
print("=" * 65)

for result in results:

    print()
    print(
        os.path.basename(
            result["file"]
        )
    )

    print(
        f"  Duration: "
        f"{result['duration']:.1f} sec"
    )

    print(
        f"  Estimated cuts: "
        f"{result['estimated_cuts']}"
    )

    print(
        f"  Cuts/sec: "
        f"{result['cuts_per_second']:.2f}"
    )

    print(
        f"  Visual diversity: "
        f"{result['visual_score']:.1f}/100"
    )

    print(
        f"  Editing activity: "
        f"{result['cut_score']:.1f}/100"
    )

    print(
        f"  Pacing: "
        f"{result['pacing_score']:.1f}/100"
    )

    print(
        f"  Duration: "
        f"{result['duration_score']:.1f}/100"
    )

    print(
        f"  FINAL SCORE: "
        f"{result['final_score']:.1f}/100"
    )


# ==================================================
# Select best montage
# ==================================================

best = max(
    results,
    key=lambda result:
        result["final_score"]
)


# ==================================================
# Display winner
# ==================================================

print()
print("=" * 65)
print("BEST MONTAGE")
print("=" * 65)

print(
    f"Selected: "
    f"{best['file']}"
)

print(
    f"Score: "
    f"{best['final_score']:.1f}/100"
)
# ==================================================
# Create final montage
# ==================================================

final_output = "output/final_montage.mp4"

shutil.copy2(
    best["file"],
    final_output
)

print()
print("=" * 65)
print("FINAL MONTAGE CREATED")
print("=" * 65)

print(
    f"Final file: {final_output}"
)