import gradio as gr
from mock_image_generation import read_story_from_file, process_story
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color
import textwrap
import json
import os

# Register fonts
pdfmetrics.registerFont(TTFont('DejaVuSans', 'Fonts/dsf/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ComicSansMS', 'Fonts/am/Action_Man.ttf'))


def create_flexible_layout(num_images, custom_layout=None):
    default_layouts = {
        1: [(0, 0, 1, 1)],
        2: [(0, 0, 0.5, 1), (0.5, 0, 0.5, 1)],
        3: [(0, 0, 0.5, 0.5), (0.5, 0, 0.5, 0.5), (0, 0.5, 1, 0.5)],
        4: [(0, 0, 0.5, 0.5), (0.5, 0, 0.5, 0.5), (0, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5)],
        5: [(0, 0, 0.33, 0.5), (0.33, 0, 0.33, 0.5), (0.66, 0, 0.34, 0.5),
            (0, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5)],
        6: [(0, 0, 0.33, 0.5), (0.33, 0, 0.33, 0.5), (0.66, 0, 0.34, 0.5),
            (0, 0.5, 0.33, 0.5), (0.33, 0.5, 0.33, 0.5), (0.66, 0.5, 0.34, 0.5)]
    }

    if custom_layout:
        try:
            return json.loads(custom_layout)
        except json.JSONDecodeError:
            print("Invalid custom layout. Using default.")

    return default_layouts.get(num_images, default_layouts[4])


def create_pdf(images, story_content, title, font_size, custom_layout, border_thickness, dialogue_position,
               frame_color):
    pdf_path = "story_output.pdf"
    page_width, page_height = A4
    margin = 0.5 * inch
    content_width = page_width - 2 * margin
    content_height = page_height - 2 * margin

    c = canvas.Canvas(pdf_path, pagesize=A4)

    # Set title
    title_height = 1 * inch
    c.setFont("ComicSansMS", font_size + 8)
    c.setFillColor(Color(0.1, 0.1, 0.1))
    c.drawCentredString(page_width / 2, page_height - 0.5 * inch, title)

    # Adjust content area for images
    image_area_height = content_height * 0.6  # Use 60% of the content area for images
    image_start_y = page_height - margin - title_height - image_area_height

    # Create flexible layout
    layout = create_flexible_layout(len(images), custom_layout)

    # Parse frame color
    frame_color = Color(*[int(frame_color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)])

    for i, (img_path, (x, y, w, h)) in enumerate(zip(images, layout)):
        # Calculate image position and size
        img_x = margin + x * content_width
        img_y = image_start_y + (1 - y - h) * image_area_height
        img_w = w * content_width
        img_h = h * image_area_height

        # Draw comic-style frame for each individual image
        c.setStrokeColor(frame_color)
        c.setLineWidth(border_thickness)
        c.rect(img_x, img_y, img_w, img_h)

        # Add image (adjusted to fit inside the border)
        image_margin = border_thickness / 2
        c.drawImage(img_path,
                    img_x + image_margin,
                    img_y + image_margin,
                    width=img_w - 2 * image_margin,
                    height=img_h - 2 * image_margin,
                    preserveAspectRatio=True,
                    mask='auto')

        # Add dialogue
        c.setFont("ComicSansMS", font_size)
        dialogue_text = f"Dialogue for image {i + 1}"

        # Create speech bubble
        bubble_margin = 10
        text_width = c.stringWidth(dialogue_text, "ComicSansMS", font_size)
        bubble_width = min(text_width + 2 * bubble_margin, img_w - 2 * bubble_margin)
        bubble_height = font_size + 2 * bubble_margin

        if dialogue_position == "inside_bottom":
            bubble_x = img_x + img_w / 2 - bubble_width / 2
            bubble_y = img_y + bubble_height + border_thickness
        elif dialogue_position == "outside_bottom":
            bubble_x = img_x + img_w / 2 - bubble_width / 2
            bubble_y = img_y - bubble_height
        else:  # inside_top
            bubble_x = img_x + img_w / 2 - bubble_width / 2
            bubble_y = img_y + img_h - bubble_height - border_thickness

        # Draw speech bubble
        c.setFillColor(Color(1, 1, 1))  # White fill
        c.setStrokeColor(frame_color)
        c.roundRect(bubble_x, bubble_y, bubble_width, bubble_height, 5, fill=1, stroke=1)

        # Add text to speech bubble
        c.setFillColor(Color(0.1, 0.1, 0.1))  # Dark grey text
        c.drawCentredString(bubble_x + bubble_width / 2, bubble_y + bubble_margin, dialogue_text)

    # Add story content
    story_start_y = image_start_y - 0.5 * inch
    story_height = story_start_y - margin
    styles = getSampleStyleSheet()
    style = ParagraphStyle('Comic', fontName='ComicSansMS', fontSize=font_size, leading=font_size * 1.2,
                           textColor=Color(0.1, 0.1, 0.1))

    story_frame = Frame(margin, margin, content_width, story_height, showBoundary=0)
    story = Paragraph(story_content, style)
    story_frame.addFromList([story], c)

    c.save()
    return pdf_path


def interface(story_content, story_file, num_frames, art_style, title, font_size, custom_layout, border_thickness,
              dialogue_position, frame_color):
    if story_file is not None:
        story_content = read_story_from_file(story_file)

    if not story_content:
        return [("Error", "Please enter story content or upload a txt file")], None

    num_frames = int(num_frames) if num_frames else 2

    result_images = process_story(story_content, num_frames, art_style)

    valid_images = [img_path for _, img_path in result_images if
                    not img_path.startswith("Error") and os.path.exists(img_path)]

    if not valid_images:
        return [("Error", "No valid images generated")], None

    pdf_path = create_pdf(valid_images, story_content, title, font_size, custom_layout, border_thickness,
                          dialogue_position, frame_color)

    return valid_images, pdf_path


iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(label="Story content", lines=5),
        gr.File(label="Or upload a .txt file"),
        gr.Slider(minimum=1, maximum=6, step=1, label="Number of frames", value=2),
        gr.Dropdown(["anime", "fairy tale illustration", "comic", "realistic"], label="Art style", value="comic"),
        gr.Textbox(label="Story Title", value="My Comic Story"),
        gr.Slider(minimum=8, maximum=24, step=1, label="Font Size", value=12),
        gr.Textbox(label="Custom Layout (JSON format, optional)", lines=2),
        gr.Slider(minimum=1, maximum=8, step=0.5, label="Border Thickness", value=3),
        gr.Radio(["inside_top", "inside_bottom", "outside_bottom"], label="Dialogue Position", value="inside_bottom"),
        gr.ColorPicker(label="Frame Color", value="#4A4A4A")
    ],
    outputs=[
        gr.Gallery(label="Generated Comic Frames"),
        gr.File(label="Download Comic PDF")
    ],
    title="Story to Comic Generator",
    description="Transform your story into a comic book style PDF with customizable layouts, styles, and frame colors!"
)

if __name__ == "__main__":
    iface.launch()