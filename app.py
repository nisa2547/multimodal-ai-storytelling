from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

from src.image_processor import describe_image
from src.speech_to_text import transcribe_audio
from src.text_processor import clean_text_input
from src.prompt_builder import build_prompt
from src.story_generator import generate_story

image_path = "data/sample.jpg"
audio_path = "data/sample_audio.mp3"
user_text = "Make the character discover an ancient artifact."

scene_desc = describe_image(image_path, API_KEY)
speech_text = transcribe_audio(audio_path)
final_input = clean_text_input(user_text + " " + speech_text)
prompt = build_prompt(scene_desc, final_input)
story = generate_story(prompt, API_KEY)

print("\n===== Generated Story =====\n")
print(story)