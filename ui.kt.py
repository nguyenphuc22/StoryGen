import gradio as gr
from mock_image_generation import read_story_from_file, process_story
from fpdf import FPDF
import textwrap
import random

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'My Story', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_flexible_layout(num_images):
    layouts = [
        [(0, 0, 1, 1)],  # 1 image
        [(0, 0, 1, 0.5), (0, 0.5, 1, 0.5)],  # 2 images
        [(0, 0, 0.6, 1), (0.6, 0, 0.4, 0.5), (0.6, 0.5, 0.4, 0.5)],  # 3 images
        [(0, 0, 0.5, 0.5), (0.5, 0, 0.5, 0.5), (0, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5)]  # 4 images
    ]
    return layouts[min(num_images, 4) - 1]

def create_pdf(images, story_content, title, font_size):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set title
    pdf.set_font("Arial", "B", font_size + 4)
    pdf.cell(0, 10, title, 0, 1, "C")
    pdf.ln(10)

    # Calculate dimensions
    page_width = pdf.w - 2 * pdf.l_margin
    page_height = pdf.h - 2 * pdf.t_margin

    # Create flexible layout
    layout = create_flexible_layout(len(images))

    for i, (img_path, (x, y, w, h)) in enumerate(zip(images, layout)):
        # Calculate image position and size
        img_x = pdf.l_margin + x * page_width
        img_y = pdf.t_margin + y * page_height
        img_w = w * page_width
        img_h = h * page_height

        # Add image
        pdf.image(img_path, x=img_x, y=img_y, w=img_w, h=img_h)

        # Add text below the image
        pdf.set_font("Arial", "", font_size)
        text_y = img_y + img_h + 5
        story_text = f"This is the story text for image {i + 1}. " * 5  # Mock story text
        wrapped_text = textwrap.wrap(story_text, width=int(img_w / (font_size / 2)))

        for line in wrapped_text:
            if pdf.get_y() + pdf.font_size > pdf.page_break_trigger:
                pdf.add_page()
            pdf.set_xy(img_x, text_y)
            pdf.cell(img_w, pdf.font_size, line, 0, 1)
            text_y += pdf.font_size + 2

    pdf_path = "story_output.pdf"
    pdf.output(pdf_path)
    return pdf_path

def interface(story_content, story_file, num_frames, art_style, title, font_size):
    if story_file is not None:
        story_content = read_story_from_file(story_file)

    if not story_content:
        return [("Error", "Please enter story content or upload a txt file")], None

    num_frames = int(num_frames) if num_frames else 2  # Default to 2 frames if not specified

    result_images = process_story(story_content, num_frames, art_style)

    # Filter out any error messages and only return valid image paths
    valid_images = [img_path for _, img_path in result_images if not img_path.startswith("Error")]

    # Create PDF
    pdf_path = create_pdf(valid_images, story_content, title, font_size)

    return valid_images, pdf_path

iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(label="Story content", lines=5),
        gr.File(label="Or upload a .txt file"),
        gr.Slider(minimum=1, maximum=4, step=1, label="Number of frames", value=2),
        gr.Dropdown(["anime", "fairy tale illustration", "comic", "realistic"], label="Art style", value="anime"),
        gr.Textbox(label="Story Title", value="My Story"),
        gr.Slider(minimum=8, maximum=24, step=1, label="Font Size", value=12),
    ],
    outputs=[
        gr.Gallery(label="Generated Images"),
        gr.File(label="Download PDF")
    ],
    title="Convert Story to Comic and PDF",
    description="Enter story content or upload a .txt file to create a comic and export as PDF"
)

if __name__ == "__main__":
    iface.launch()