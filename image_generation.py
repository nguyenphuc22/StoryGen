import base64
from openai import OpenAI
import os

client = OpenAI(api_key="key")

def read_story_from_file(file):
    return file.decode('utf-8')

def generate_prompts(story_content, num_frames, art_style):
    prompt = f"""
    Based on the following story:

    {story_content}

    Create {num_frames} prompts to draw illustrations for this story. 
    Each prompt should describe an important scene in the story.
    Art style: {art_style}

    Respond with a list of prompts, one prompt per line.
    """

    print("Generating prompts...")
    print(prompt)

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().split('\n')


def create_image(prompt, model="dall-e-2"):
    print(f"Creating image with prompt: {prompt}")
    if not prompt:
        raise ValueError("Empty prompt provided to create_image function")

    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="b64_json"
    )
    return response.data[0].b64_json


def process_story(story_content, num_frames, art_style):
    prompts = generate_prompts(story_content, num_frames, art_style)
    print(f"Generated prompts: {prompts}")

    result_images = []
    os.makedirs("images", exist_ok=True)

    for i, prompt in enumerate(prompts):
        try:
            b64_image = create_image(prompt)
            image_data = base64.b64decode(b64_image)

            image_filename = f"frame_{i + 1}.png"
            image_path = os.path.join("images", image_filename)
            with open(image_path, "wb") as file:
                file.write(image_data)

            result_images.append((f"Frame {i + 1}", image_path))
            print(f"Saved image: {image_path}")
        except Exception as e:
            print(f"Error generating image for prompt {i + 1}: {str(e)}")
            result_images.append((f"Frame {i + 1} (Error)", str(e)))

    return result_images