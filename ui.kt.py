import gradio as gr
from image_generation import read_story_from_file, process_story


def interface(story_content, story_file, num_frames, art_style):
    if story_file is not None:
        story_content = read_story_from_file(story_file)

    if not story_content:
        return [("Error", "Please enter story content or upload a txt file")]

    num_frames = int(num_frames) if num_frames else 2  # Default to 2 frames if not specified

    result_images = process_story(story_content, num_frames, art_style)

    # Filter out any error messages and only return valid image paths
    valid_images = [img_path for _, img_path in result_images if not img_path.startswith("Error")]

    return valid_images


iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(label="Story content", lines=5),
        gr.File(label="Or upload a .txt file"),
        gr.Slider(minimum=1, maximum=10, step=1, label="Number of frames", value=2),
        gr.Dropdown(["anime", "fairy tale illustration", "comic", "realistic"], label="Art style", value="anime")
    ],
    outputs=gr.Gallery(label="Generated Images"),
    title="Convert Story to Comic",
    description="Enter story content or upload a .txt file to create a comic"
)

if __name__ == "__main__":
    iface.launch()