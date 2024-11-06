import base64
from openai import OpenAI
from prompt_template import PROMPT_GENERATION_TEMPLATE
import os

client = OpenAI(api_key="key")

def read_story_from_file(story_file):
    with open(story_file, 'r', encoding='utf-8') as file:
        return file.read()

def generate_prompts(story_content, num_frames, art_style):
    prompt = PROMPT_GENERATION_TEMPLATE.format(story=story_content, number=num_frames, style=art_style)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    prompts = response.choices[0].message.content.split('[')
    cleaned_prompts = []
    for prompt in prompts:
        if prompt.strip():  # Ignore empty or whitespace-only strings
            # Remove the leading number and bracket, and strip any excess whitespace
            cleaned_prompt = prompt.split(']', 1)[-1].strip().strip('"')
            cleaned_prompts.append(cleaned_prompt)    
    return cleaned_prompts


def create_image(prompt, model="dall-e-3"):
    print(f"Creating image with prompt: {prompt}")
    if not prompt:
        raise ValueError("Empty prompt provided to create_image function")

    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="b64_json",
        quality="standard"
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