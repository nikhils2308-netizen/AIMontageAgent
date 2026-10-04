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

print()
print("=" * 60)
print("STEP 1: Creating AI editing plan...")
print("=" * 60)

planner = subprocess.run(
    ["python", "src/ai_planner.py"],
    input=instruction + "\n",
    text=True,
    encoding="utf-8",
    errors="replace"
)

if planner.returncode != 0:
    print("AI planner failed.")
    exit()

print()
print("=" * 60)
print("STEP 2: Generating montage candidates...")
print("=" * 60)

generator = subprocess.run(
    ["python", "src/generate_candidates.py"],
    text=True,
    encoding="utf-8",
    errors="replace"
)

if generator.returncode != 0:
    print("Candidate generation failed.")
    exit()

print()
print("=" * 60)
print("STEP 3: Analyzing montage candidates...")
print("=" * 60)

analyzer = subprocess.run(
    ["python", "src/analyze_montages.py"],
    text=True,
    encoding="utf-8",
    errors="replace"
)

if analyzer.returncode != 0:
    print("Montage analysis failed.")
    exit()

print()
print("=" * 60)
print("AI MONTAGE COMPLETE")
print("=" * 60)

final_output = os.path.join(
    "output",
    "final_montage.mp4"
)

if os.path.exists(final_output):

    print()
    print("FINAL MONTAGE CREATED")
    print("=" * 60)
    print(f"Output: {final_output}")

else:

    print()
    print("FINAL MONTAGE NOT FOUND")
    print("=" * 60)