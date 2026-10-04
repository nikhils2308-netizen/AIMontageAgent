import streamlit as st
import os
import shutil
import subprocess

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
FINAL_FILE = os.path.join(OUTPUT_FOLDER, "final_montage.mp4")

st.set_page_config(
    page_title="AI Montage Agent",
    page_icon="🎬",
    layout="centered"
)

st.title("AI MONTAGE AGENT 🎬")

st.write(
    "Create an AI-powered video montage from your clips."
)

st.subheader("Upload your videos")

uploaded_files = st.file_uploader(
    "Upload your videos",
    type=["mp4", "mov", "avi", "mkv"],
    accept_multiple_files=True
)

st.subheader("Describe your editing idea")

editing_idea = st.text_area(
    "Example: Create a cinematic and energetic 30-second montage",
    height=120
)

if st.button("🎬 Generate Montage", use_container_width=True):

    if not uploaded_files:
        st.error("Please upload at least one video.")
        st.stop()

    if not editing_idea.strip():
        st.error("Please describe your editing idea.")
        st.stop()

    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    with st.status(
        "Creating your AI montage...",
        expanded=True
    ) as status:

        st.write("📤 Uploading videos...")

        # Clear previous input files
        for filename in os.listdir(INPUT_FOLDER):
            file_path = os.path.join(INPUT_FOLDER, filename)

            if os.path.isfile(file_path):
                os.remove(file_path)

        # Save uploaded videos
        for uploaded_file in uploaded_files:

            file_path = os.path.join(
                INPUT_FOLDER,
                uploaded_file.name
            )

            with open(file_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

        st.write(
            f"✓ {len(uploaded_files)} video(s) uploaded"
        )

        # Remove previous final montage
        if os.path.exists(FINAL_FILE):
            os.remove(FINAL_FILE)

        st.write("🤖 AI analyzing editing idea...")

        process = subprocess.run(
            ["python", "src/ai_montage_agent.py"],
            input=editing_idea + "\n",
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True
        )

        # Show AI pipeline output
        if process.stdout:
            st.code(process.stdout)

        # Show errors from the pipeline
        if process.stderr:
            st.code(process.stderr)

        st.write("🎬 Creating montage candidates...")
        st.write("📊 Evaluating candidates...")
        st.write("🏆 Selecting best montage...")

        status.update(
            label="Montage processing finished",
            state="complete"
        )

    # Check final output
    if os.path.exists(FINAL_FILE):

        st.success("🎉 Final montage created successfully!")

        st.video(FINAL_FILE)

        with open(FINAL_FILE, "rb") as video_file:
            video_bytes = video_file.read()

        st.download_button(
            label="⬇ Download Final Montage",
            data=video_bytes,
            file_name="final_montage.mp4",
            mime="video/mp4",
            use_container_width=True
        )

    else:

        st.error("Final montage was not created.")

        st.write(
            "The pipeline completed, but "
            "final_montage.mp4 was not found."
        )