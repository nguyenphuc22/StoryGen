import gradio as gr
from mock_image_generation import read_story_from_file, process_story
from fpdf import FPDF
import textwrap
import math


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'My Story', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def create_pdf(images, story_content, title, font_size, layout, images_per_page, image_size):
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

    if layout == "side_by_side":
        image_width = page_width * image_size
        text_width = page_width - image_width
        image_height = image_width * 0.75  # Assuming 4:3 aspect ratio
    elif layout == "top_bottom":
        image_width = page_width
        image_height = page_height * image_size
        text_width = page_width
    else:  # grid
        cols = math.ceil(math.sqrt(images_per_page))
        rows = math.ceil(images_per_page / cols)
        image_width = page_width / cols
        image_height = (page_height * image_size) / rows
        text_width = page_width

    images_on_current_page = 0
    for i, img_path in enumerate(images):
        if images_on_current_page == 0 or (layout == "grid" and images_on_current_page >= images_per_page):
            if i != 0:
                pdf.add_page()
            images_on_current_page = 0

        if layout == "side_by_side":
            if pdf.get_y() + image_height > pdf.page_break_trigger:
                pdf.add_page()
            pdf.image(img_path, x=pdf.l_margin, w=image_width)
            pdf.set_xy(pdf.l_margin + image_width + 5, pdf.get_y())
        elif layout == "top_bottom":
            pdf.image(img_path, x=pdf.l_margin, w=image_width)
            pdf.ln(image_height + 5)
        else:  # grid
            x = pdf.l_margin + (images_on_current_page % cols) * image_width
            y = pdf.t_margin + (images_on_current_page // cols) * image_height
            pdf.image(img_path, x=x, y=y, w=image_width, h=image_height)

        # Add corresponding text
        pdf.set_font("Arial", "", font_size)

        # Mock story text (replace with actual story content)
        story_text = f"This is the story text for image {i + 1}. " * 20

        wrapped_text = textwrap.wrap(story_text, width=int(text_width / (font_size / 2)))

        if layout != "grid":
            for line in wrapped_text:
                if pdf.get_y() + pdf.font_size > pdf.page_break_trigger:
                    pdf.add_page()
                    if layout == "side_by_side":
                        pdf.set_xy(pdf.l_margin + image_width + 5, pdf.t_margin)
                pdf.cell(text_width, pdf.font_size, line, 0, 1)

        pdf.ln(10)
        images_on_current_page += 1

    if layout == "grid":
        pdf.add_page()
        for line in wrapped_text:
            if pdf.get_y() + pdf.font_size > pdf.page_break_trigger:
                pdf.add_page()
            pdf.cell(text_width, pdf.font_size, line, 0, 1)

    pdf_path = "story_output.pdf"
    pdf.output(pdf_path)
    return pdf_path


def interface(story_content, story_file, num_frames, art_style, title, font_size, layout, images_per_page, image_size):
    if story_file is not None:
        story_content = read_story_from_file(story_file)

    if not story_content:
        return [("Error", "Please enter story content or upload a txt file")], None

    num_frames = int(num_frames) if num_frames else 2  # Default to 2 frames if not specified

    result_images = process_story(story_content, num_frames, art_style)

    # Filter out any error messages and only return valid image paths
    valid_images = [img_path for _, img_path in result_images if not img_path.startswith("Error")]

    # Create PDF
    pdf_path = create_pdf(valid_images, story_content, title, font_size, layout, images_per_page, image_size)

    return valid_images, pdf_path


iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(label="Story content", lines=5),
        gr.File(label="Or upload a .txt file"),
        gr.Slider(minimum=1, maximum=10, step=1, label="Number of frames", value=2),
        gr.Dropdown(["anime", "fairy tale illustration", "comic", "realistic"], label="Art style", value="anime"),
        gr.Textbox(label="Story Title", value="My Story"),
        gr.Slider(minimum=8, maximum=24, step=1, label="Font Size", value=12),
        gr.Radio(["side_by_side", "top_bottom", "grid"], label="Layout", value="side_by_side"),
        gr.Slider(minimum=1, maximum=9, step=1, label="Images per page (for grid layout)", value=4),
        gr.Slider(minimum=0.1, maximum=0.9, step=0.1, label="Image size (proportion of page)", value=0.4),
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