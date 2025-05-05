from dotenv import load_dotenv
import os
import json

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

if os.path.exists("saved_stories.json"):
    with open("saved_stories.json", "r") as file:
        saved_stories = json.load(file)
else:
    saved_stories = {}

if saved_stories:
    print("\nSaved stories available:")
    for name in saved_stories:
        print(f"- {name}")
    load_choice = input("Do you want to load one of these stories? (y/n): ").strip().lower()

    if load_choice == "y":
        story_name = input("Enter the name of the story you want to load: ").strip()
        story_so_far = saved_stories.get(story_name, "")
        if story_so_far:
            print(f"\nLoaded story '{story_name}':\n{story_so_far}")
        else:
            print("Story not found. Starting a new one.")
            story_so_far = ""
    else:
        story_so_far = ""
else:
    print("\nNo saved stories found. Starting fresh.")
    story_so_far = ""


from src.image_processor import describe_image
from src.speech_to_text import transcribe_audio
from src.text_processor import clean_text_input
# from src.prompt_builder import build_prompt
from src.story_generator import generate_story
from src.prompt_strategy import extract_character_and_goal, assemble_prompt, show_initial_prompt, ask_user_choice, handle_choice


# image_path = "data/sample.jpg"
# audio_path = "data/sample_audio.mp3"
image_path = input("Please enter the path to your image (or leave blank to skip): ").strip()
audio_path = input("Please enter the path to your audio (or leave blank to skip): ").strip()
# user_text = "Make the character discover an ancient artifact."

show_initial_prompt()
choice = ask_user_choice()
scene_desc_choice, text_input = handle_choice(choice)

if image_path:
    scene_desc = describe_image(image_path, API_KEY)
    print(f"Scene description from image: {scene_desc}")
else:
    scene_desc = "A vast, open field under a bright blue sky, with a single oak tree in the distance."

if audio_path:
    speech_text = transcribe_audio(audio_path)
    print(f"Transcribed speech: {speech_text}")
else:
    speech_text = ""
    

if scene_desc_choice and scene_desc_choice != scene_desc:
    scene_desc = scene_desc_choice

# scene_desc = describe_image(image_path, API_KEY)
# speech_text = transcribe_audio(audio_path)
combined_input = clean_text_input(text_input + " " + speech_text)
character_description, goal_description = extract_character_and_goal(combined_input)
prompt = assemble_prompt(scene_desc, character_description, goal_description)
# prompt = build_prompt(scene_desc, final_input)
story = generate_story(prompt, API_KEY)

print("\n===== Generated Story =====\n")
print(story)

save_choice = input("\nWould you like to save this story to continue later? (y/n): ").strip().lower()
if save_choice == "y":
    story_name = input("Enter a name for this story: ").strip()
    if story_name in saved_stories:
        saved_stories[story_name] += "\n" + story  # Append to existing story
    else:
        saved_stories[story_name] = story

    with open("saved_stories.json", "w") as file:
        json.dump(saved_stories, file, indent=4)

    print(f"Story saved under the name '{story_name}'!")
