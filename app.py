import streamlit as st
import os
import shutil
import subprocess


# ==================================================
# Page configuration
# ==================================================

st.set_page_config(
    page_title="AI Montage Agent",
    page_icon="🎬",
    layout="centered"
)


# ==================================================
# Project folders
# ==================================================

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
FINAL_FILE = os.path.join(
    OUTPUT_FOLDER,
    "final_montage.mp4"
)


# ==================================================
# Title
# ==================================================

st.title("AI MONTAGE AGENT 🎬")

st.write(
    "Create an AI-powered video montage from your clips."
)


# ==================================================
# Upload videos
# ==================================================

st.subheader("Upload your videos")

uploaded_files = st.file_uploader(
    "Choose one or more video files",
    type=["mp4", "mov", "avi", "mkv"],
    accept_multiple_files=True
)


# ==================================================
# Editing instruction
# ==================================================

st.subheader("Describe your editing idea")

editing_idea = st.text_area(
    "Editing idea",
    placeholder=(
        "Example: Create a fast energetic "
        "30-second montage"
    )
)


# ==================================================
# Generate button
# ==================================================

generate = st.button(
    "🎬 Generate Montage",
    type="primary",
    use_container_width=True
)


# ==================================================
# Generate montage
# ==================================================

if generate:

    # ------------------------------------------------
    # Validate videos
    # ------------------------------------------------

    if not uploaded_files:

        st.error(
            "Please upload at least one video."
        )

        st.stop()


    # ------------------------------------------------
    # Validate editing idea
    # ------------------------------------------------

    if not editing_idea.strip():

        st.error(
            "Please describe your editing idea."
        )

        st.stop()


    # ------------------------------------------------
    # Create folders
    # ------------------------------------------------

    os.makedirs(
        INPUT_FOLDER,
        exist_ok=True
    )

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )


    # ------------------------------------------------
    # Status: uploading videos
    # ------------------------------------------------

    with st.status(
        "Creating your AI montage...",
        expanded=True
    ) as status:

        st.write("📤 Uploading videos...")


        # ------------------------------------------------
        # Remove old input videos
        # ------------------------------------------------

        for filename in os.listdir(INPUT_FOLDER):

            file_path = os.path.join(
                INPUT_FOLDER,
                filename
            )

            if os.path.isfile(file_path):

                os.remove(file_path)


        # ------------------------------------------------
        # Save uploaded videos
        # ------------------------------------------------

        for uploaded_file in uploaded_files:

            destination = os.path.join(
                INPUT_FOLDER,
                uploaded_file.name
            )

            with open(
                destination,
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )


        st.write(
            f"✓ {len(uploaded_files)} video(s) uploaded"
        )


        # ------------------------------------------------
        # Remove previous final montage
        # ------------------------------------------------

        if os.path.exists(FINAL_FILE):

            os.remove(FINAL_FILE)


        # ------------------------------------------------
        # Run existing Part 4 agent
        # ------------------------------------------------

        st.write(
            "🤖 AI analyzing editing idea..."
        )

        st.write(
            "🎬 Creating montage candidates..."
        )

        st.write(
            "📊 Evaluating candidates..."
        )

        st.write(
            "🏆 Selecting best montage..."
        )


        process = subprocess.run(
            [
                "python",
                "src\\ai_montage_agent.py"
            ],
            input=editing_idea + "\n",
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True
        )


        # ------------------------------------------------
        # Check pipeline result
        # ------------------------------------------------

        if process.returncode != 0:

            status.update(
                label="Montage generation failed",
                state="error"
            )

            st.error(
                "The AI montage pipeline encountered an error."
            )

            st.code(
                process.stdout +
                "\n" +
                process.stderr
            )

            st.stop()


        # ------------------------------------------------
        # Check final file
        # ------------------------------------------------

        if not os.path.exists(FINAL_FILE):

            status.update(
                label="Final montage was not created",
                state="error"
            )

            st.error(
                "The pipeline completed, but "
                "final_montage.mp4 was not found."
            )

            st.code(
                process.stdout
            )

            st.stop()


        # ------------------------------------------------
        # Success
        # ------------------------------------------------

        st.write(
            "✓ Final montage ready"
        )

        status.update(
            label="Montage ready!",
            state="complete"
        )


# ==================================================
# Display final montage
# ==================================================

if os.path.exists(FINAL_FILE):

    st.subheader("Final Montage")

    st.video(
        FINAL_FILE
    )


    # ------------------------------------------------
    # Download button
    # ------------------------------------------------

    with open(
        FINAL_FILE,
        "rb"
    ) as file:

        video_bytes = file.read()


    st.download_button(
        label="⬇ Download Final Montage",
        data=video_bytes,
        file_name="final_montage.mp4",
        mime="video/mp4",
        use_container_width=True
    )