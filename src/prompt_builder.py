def build_prompt(scene_description: str, user_text: str) -> str:
    return f"""
You are a creative AI storyteller.

Scene Description:
{scene_description}

User Instruction:
{user_text}

Write a short, vivid story that incorporates the user's input and the scene context. Maintain a logical narrative flow.
"""