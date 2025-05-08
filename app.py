from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

from src.story_storage import StoryStorage

stories = StoryStorage.list_stories()
if stories:
    print("\nAvailable saved stories:")
    for s in stories:
        print(f"- {s['story_id']} (Title: {s.get('title', 'Untitled')})")
    load_choice = input("Do you want to load one of these stories? (y/n): ").strip().lower()

    if load_choice == "y":
        story_id = input("Enter the story ID to load: ").strip()
        try:
            story_storage = StoryStorage.load_story(story_id)
            print(f"\nLoaded story '{story_id}':")
            print(story_storage.generate_recap())
        except FileNotFoundError:
            print("Story ID not found. Starting a new story.")
            story_storage = StoryStorage()
    else:
        story_storage = StoryStorage()
else:
    print("\nNo saved stories found. Starting a new story.")
    story_storage = StoryStorage()

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

if choice == "1" and image_path:
    scene_desc = describe_image(image_path, API_KEY)
    print(f"Scene description from image: {scene_desc}")
else:
    scene_desc = "A vast, open field under a bright blue sky, with a single oak tree in the distance."

if audio_path:
    speech_text = transcribe_audio(audio_path)
    print(f"Transcribed speech: {speech_text}")
else:
    speech_text = ""

# scene_desc = describe_image(image_path, API_KEY)
# speech_text = transcribe_audio(audio_path)
combined_input = clean_text_input(text_input + " " + speech_text)
character_description, goal_description = extract_character_and_goal(combined_input)
# if scene_desc_choice and scene_desc_choice != scene_desc:
#     scene_desc = scene_desc_choice
prompt = assemble_prompt(scene_desc, character_description, goal_description)
# prompt = build_prompt(scene_desc, final_input)

story = generate_story(prompt, API_KEY)

print("\n===== Generated Story =====\n")
print(story)

generate_image = input("\nWould you like to generate an image based on the story? (y/n): ").strip().lower()

if generate_image == "y":
    try:
        image_prompt = f"{scene_desc} {character_description} {goal_description}"
        print("\nGenerating image for the scene and character...")

        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        print(f"\nGenerated Image URL: {image_url}")

    except Exception as e:
        print("\nImage generation failed:", e)
else:
    print("\nSkipping image generation.")

save_choice = input("\nWould you like to save this story as a new section? (y/n): ").strip().lower()
if save_choice == "y":
    section_title = input("Enter a title for this section: ").strip() or None
    section_number = story_storage.add_section(story, section_title)
    print(f"Story saved as Section {section_number + 1} in '{story_storage.story_id}'.")
else:
    print("Story not saved.")