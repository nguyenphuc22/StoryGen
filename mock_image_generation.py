import os

def read_story_from_file(file):
    return file.decode('utf-8')

def generate_prompts(story_content, num_frames, art_style):
    # Mock prompts
    mock_prompts = [
        "A young hero embarking on a journey",
        "The hero facing a fearsome dragon",
        "The hero discovering a magical artifact",
        "The hero returning triumphantly to their village",
        "The hero celebrating with friends and family"
    ]
    return mock_prompts[:num_frames]

def create_image(i):
    # Instead of creating an image, we'll return a path to a mock image
    return f"images/frame_{i + 1}.png"

def process_story(story_content, num_frames, art_style):
    prompts = generate_prompts(story_content, num_frames, art_style)
    print(f"Generated prompts: {prompts}")

    result_images = []

    for i, prompt in enumerate(prompts):
        try:
            image_path = create_image(i)
            result_images.append((f"Frame {i + 1}", image_path))
            print(f"Mock image path: {image_path}")
        except Exception as e:
            print(f"Error generating image for prompt {i + 1}: {str(e)}")
            result_images.append((f"Frame {i + 1} (Error)", str(e)))

    return result_images