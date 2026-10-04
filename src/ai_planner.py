import json
import os

from huggingface_hub import InferenceClient


# ==================================================
MODEL = "google/gemma-2-2b-it"


# ==================================================
# Create editing plan
# ==================================================

def create_editing_plan(user_instruction):

    prompt = f"""
You are an AI video editing planner.

Convert the user's video editing instruction into
a simple JSON editing plan.

User instruction:
{user_instruction}

Return ONLY valid JSON.

Use exactly these fields:

{{
    "style": "string",
    "pacing": "slow, medium, or fast",
    "duration": "number of seconds",
    "clip_variation": "low, medium, or high",
    "transitions": "string",
    "mood": "string"
}}

Important:
- duration must be a number.
- Do not include markdown.
- Do not include explanations.
- Return only JSON.
"""

    token = os.environ.get("HF_TOKEN")

    if not token:
        print("HF_TOKEN environment variable is missing.")
        return None

    try:

        client = InferenceClient(api_key=token, provider="featherless-ai")

        result = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.2
        )

        response = result.choices[0].message.content.strip()

    except Exception as error:

        print("Hugging Face AI error:")
        print(error)

        return None


    # ==================================================
    # Find JSON
    # ==================================================

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:

        print(
            "Could not find JSON in AI response."
        )

        print()
        print("AI response:")
        print(response)

        return None

    json_text = response[
        start:end + 1
    ]


    # ==================================================
    # Parse JSON
    # ==================================================

    try:

        plan = json.loads(
            json_text
        )

    except json.JSONDecodeError:

        print(
            "AI returned invalid JSON."
        )

        print()
        print("Response:")
        print(response)

        return None


    # ==================================================
    # Normalize duration
    # ==================================================

    duration = plan.get(
        "duration",
        30
    )

    if isinstance(duration, str):

        digits = ""

        for character in duration:

            if character.isdigit():
                digits += character

        if digits:
            duration = int(digits)
        else:
            duration = 30

    elif isinstance(duration, float):

        duration = int(duration)

    elif not isinstance(duration, int):

        duration = 30

    plan["duration"] = duration

    return plan


# ==================================================
# Main program
# ==================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("AI VIDEO EDITING PLANNER")
    print("=" * 60)

    instruction = input(
        "\nEnter your editing idea: "
    )

    plan = create_editing_plan(
        instruction
    )

    if plan is None:

        print()
        print(
            "Could not create editing plan."
        )

    else:

        # ------------------------------------------
        # Create output folder
        # ------------------------------------------

        os.makedirs(
            "output",
            exist_ok=True
        )

        # ------------------------------------------
        # Save editing plan
        # ------------------------------------------

        with open(
            "output/editing_plan.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                plan,
                file,
                indent=2
            )

        # ------------------------------------------
        # Display plan
        # ------------------------------------------

        print()
        print("=" * 60)
        print("AI-GENERATED EDITING PLAN")
        print("=" * 60)

        print(
            json.dumps(
                plan,
                indent=2
            )
        )

        print()
        print(
            "Plan saved to:"
        )

        print(
            "output/editing_plan.json"
        )