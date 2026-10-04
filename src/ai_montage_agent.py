import subprocess
import os


print()
print("=" * 60)
print("AI VIDEO MONTAGE AGENT")
print("=" * 60)

print()

instruction = input("Enter your editing idea: ")

if not instruction.strip():
    print("No editing instruction provided.")
    exit()


# ============================================================
# STEP 1: AI EDITING PLAN
# ============================================================

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


# ============================================================
# STEP 2: GENERATE CANDIDATES
# ============================================================

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


# ============================================================
# STEP 3: ANALYZE AND SELECT BEST
# ============================================================

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


# ============================================================
# FINAL OUTPUT
# ============================================================

final_output = os.path.join(
    "output",
    "final_montage.mp4"
)

print()

if os.path.exists(final_output):

    print("=" * 60)
    print("AI MONTAGE COMPLETE")
    print("=" * 60)
    print()
    print("FINAL MONTAGE CREATED")
    print(f"Output: {final_output}")

else:

    print("=" * 60)
    print("FINAL MONTAGE NOT FOUND")
    print("=" * 60)