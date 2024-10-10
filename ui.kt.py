import gradio as gr
from mock_image_generation import read_story_from_file, process_story
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
from reportlab.lib.units import inch
from PIL import Image
import io
import os
import tempfile


def create_pdf(story_content, image_paths):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        doc = SimpleDocTemplate(tmp_file.name, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        width, height = letter
        story = []

        # Combine images
        images = [Image.open(path) for path in image_paths]
        widths, heights = zip(*(i.size for i in images))
        max_width = max(widths)
        total_height = sum(heights)
        combined_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.size[1]

        # Save combined image
        combined_image_path = "combined_image.png"
        combined_image.save(combined_image_path)

        # Calculate image size (40% of page height)
        img_height = height * 0.4
        img_width = img_height * combined_image.size[0] / combined_image.size[1]

        # Add image to the story
        img = ReportLabImage(combined_image_path, width=img_width, height=img_height)
        story.append(img)
        story.append(Spacer(1, 12))  # Add some space after the image

        # Add story content
        styles = getSampleStyleSheet()
        story_paragraphs = story_content.split('\n')
        for paragraph in story_paragraphs:
            story.append(Paragraph(paragraph, styles['Normal']))
            story.append(Spacer(1, 6))  # Add some space between paragraphs

        # Build the PDF
        doc.build(story)

    return tmp_file.name


def interface(story_content, story_file, num_frames, art_style):
    if story_file is not None:
        story_content = read_story_from_file(story_file)

    if not story_content:
        return [("Error", "Please enter story content or upload a txt file")], None

    num_frames = int(num_frames) if num_frames else 2  # Default to 2 frames if not specified

    result_images = process_story(story_content, num_frames, art_style)

    # Filter out any error messages and only return valid image paths
    valid_images = [img_path for _, img_path in result_images if not img_path.startswith("Error")]

    # Create PDF
    pdf_path = create_pdf(story_content, valid_images)

    return valid_images, pdf_path


iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(label="Story content", lines=5),
        gr.File(label="Or upload a .txt file"),
        gr.Slider(minimum=1, maximum=5, step=1, label="Number of frames", value=2),
        gr.Dropdown(["anime", "fairy tale illustration", "comic", "realistic"], label="Art style", value="anime")
    ],
    outputs=[
        gr.Gallery(label="Generated Images"),
        gr.File(label="Download PDF")
    ],
    title="Convert Story to Comic",
    description="Enter story content or upload a .txt file to create a comic and PDF"
)

if __name__ == "__main__":
    iface.launch()