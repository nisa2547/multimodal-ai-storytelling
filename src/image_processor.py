from openai import OpenAI
import base64

def describe_image(image_path: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)

    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the scene in this image for a fantasy story."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content
