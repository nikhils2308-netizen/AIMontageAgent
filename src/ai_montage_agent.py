import subprocess
import os
import shutil


print()
print("=" * 60)
print("AI VIDEO MONTAGE AGENT")
print("=" * 60)

print()
instruction = input("Enter your editing idea: ")

if not instruction.strip():
    print("No editing instruction provided.")
    exit()


# ==================================================
# STEP 1 — Create AI editing plan
# ==================================================

print()
print("=" * 60)
print("STEP 1: Creating AI editing plan...")
print("=" * 60)

planner = subprocess.run(
    [
        "python",
        "src\\ai_planner.py"
    ],
    input=instruction + "\n",
    text=True,
    encoding="utf-8",
    errors="replace"
)

if planner.returncode != 0:
    print("AI planner failed.")
    exit()


# ==================================================
# STEP 2 — Generate AI-guided candidates
# ==================================================

print()
print("=" * 60)
print("STEP 2: Generating montage candidates...")
print("=" * 60)

generator = subprocess.run(
    [
        "python",
        "src\\generate_candidates.py"
    ],
    text=True,
    encoding="utf-8",
    errors="replace"
)

if generator.returncode != 0:
    print("Candidate generation failed.")
    exit()


# ==================================================
# STEP 3 — Run Part 3 evaluation
# ==================================================

print()
print("=" * 60)
print("STEP 3: Evaluating montage candidates...")
print("=" * 60)

analyzer = subprocess.run(
    [
        "python",
        "src\\analyze_montages.py"
    ],
    text=True,
    encoding="utf-8",
    errors="replace"
)

if analyzer.returncode != 0:
    print("Montage evaluation failed.")
    exit()


# ==================================================
# STEP 4 — Check final montage
# ==================================================

final_file = "output\\final_montage.mp4"

print()
print("=" * 60)

if os.path.exists(final_file):

    print("AI MONTAGE CREATED SUCCESSFULLY!")
    print("=" * 60)

    print()
    print("Final montage:")
    print(final_file)

else:

    print("Final montage was not created.")
    print("=" * 60)