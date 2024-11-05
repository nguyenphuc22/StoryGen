# ui.kt.py
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


def create_flexible_layout(num_images, custom_layout=None, layout_style='default'):
    # Each number of frames now has 3 layout options
    default_layouts = {
        1: {
            'default': [(0, 0, 1, 1)],  # Single full frame
            'option1': [(0.1, 0.1, 0.8, 0.8)],  # Centered frame with margin
            'option2': [(0.2, 0, 0.6, 1)]  # Centered vertical strip
        },
        2: {
            'default': [(0, 0, 0.5, 1), (0.5, 0, 0.5, 1)],  # Vertical split
            'option1': [(0, 0, 1, 0.5), (0, 0.5, 1, 0.5)],  # Horizontal split
            'option2': [(0.1, 0, 0.4, 1), (0.5, 0, 0.4, 1)]  # Vertical split with margins
        },
        3: {
            'default': [(0, 0, 0.5, 0.5), (0.5, 0, 0.5, 0.5), (0, 0.5, 1, 0.5)],  # Two top, one bottom
            'option1': [(0, 0, 1, 0.4), (0, 0.4, 0.5, 0.6), (0.5, 0.4, 0.5, 0.6)],  # One top, two bottom
            'option2': [(0, 0, 0.33, 1), (0.33, 0, 0.34, 1), (0.67, 0, 0.33, 1)]  # Three vertical strips
        },
        4: {
            'default': [(0, 0, 0.5, 0.5), (0.5, 0, 0.5, 0.5), (0, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5)],  # Grid
            'option1': [(0, 0, 1, 0.4), (0, 0.4, 0.33, 0.6), (0.33, 0.4, 0.34, 0.6), (0.67, 0.4, 0.33, 0.6)],
            # One top, three bottom
            'option2': [(0, 0, 0.25, 1), (0.25, 0, 0.25, 1), (0.5, 0, 0.25, 1), (0.75, 0, 0.25, 1)]
            # Four vertical strips
        },
        5: {
            'default': [(0, 0, 0.33, 0.5), (0.33, 0, 0.33, 0.5), (0.66, 0, 0.34, 0.5),
                        (0, 0.5, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5)],  # Three top, two bottom
            'option1': [(0, 0, 1, 0.4), (0, 0.4, 0.25, 0.6), (0.25, 0.4, 0.25, 0.6),
                        (0.5, 0.4, 0.25, 0.6), (0.75, 0.4, 0.25, 0.6)],  # One top, four bottom
            'option2': [(0, 0, 0.2, 1), (0.2, 0, 0.2, 1), (0.4, 0, 0.2, 1),
                        (0.6, 0, 0.2, 1), (0.8, 0, 0.2, 1)]  # Five vertical strips
        },
        6: {
            'default': [(0, 0, 0.33, 0.5), (0.33, 0, 0.33, 0.5), (0.66, 0, 0.34, 0.5),
                        (0, 0.5, 0.33, 0.5), (0.33, 0.5, 0.33, 0.5), (0.66, 0.5, 0.34, 0.5)],  # 3x2 grid
            'option1': [(0, 0, 1, 0.33), (0, 0.33, 0.5, 0.34), (0.5, 0.33, 0.5, 0.34),
                        (0, 0.67, 0.33, 0.33), (0.33, 0.67, 0.33, 0.33), (0.66, 0.67, 0.34, 0.33)],
            # One top, two middle, three bottom
            'option2': [(0, 0, 0.167, 1), (0.167, 0, 0.167, 1), (0.334, 0, 0.167, 1),
                        (0.501, 0, 0.167, 1), (0.668, 0, 0.167, 1), (0.835, 0, 0.165, 1)]  # Six vertical strips
        }
    }

    if custom_layout:
        try:
            return json.loads(custom_layout)
        except json.JSONDecodeError:
            print("Invalid custom layout. Using default.")

    return default_layouts.get(num_images, default_layouts[4])[layout_style]


def create_pdf(images, story_content, title, font_size, custom_layout, border_thickness, dialogue_position, frame_color,
               full_fill=False, layout_style='default'):
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

    # Create flexible layout with specified style
    layout = create_flexible_layout(len(images), custom_layout, layout_style)

    # Parse frame color
    frame_color = Color(*[int(frame_color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)])

    for i, (img_path, (x, y, w, h)) in enumerate(zip(images, layout)):
        # Calculate image position and size
        img_x = margin + x * content_width
        img_y = image_start_y + (1 - y - h) * image_area_height
        img_w = w * content_width
        img_h = h * image_area_height

        # Draw comic-style frame
        c.setStrokeColor(frame_color)
        c.setLineWidth(border_thickness)
        c.rect(img_x, img_y, img_w, img_h)

        # Add image
        image_margin = border_thickness / 2
        if full_fill:
            c.drawImage(img_path,
                        img_x + image_margin,
                        img_y + image_margin,
                        width=img_w - 2 * image_margin,
                        height=img_h - 2 * image_margin,
                        mask='auto')
        else:
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


def interface(
        story_content,
        story_file,
        title,
        num_frames,
        art_style,
        font_size,
        border_thickness,
        dialogue_position,
        frame_color,
        full_fill,
        custom_layout,
        layout_style
):
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

    pdf_path = create_pdf(
        valid_images,
        story_content,
        title,
        font_size,
        custom_layout,
        border_thickness,
        dialogue_position,
        frame_color,
        full_fill,
        layout_style
    )

    return valid_images, pdf_path


# Create the Gradio interface
with gr.Blocks(title="Story to Comic Generator", theme=gr.themes.Soft()) as iface:
    gr.Markdown("""
    # Story to Comic Generator
    Transform your story into a comic book style PDF with customizable layouts and styles!
    """)

    with gr.Tabs():
        # Story Input Tab
        with gr.TabItem("1️⃣ Story Input"):
            with gr.Row():
                with gr.Column():
                    title = gr.Textbox(
                        label="Story Title",
                        value="My Comic Story",
                        placeholder="Enter your story title..."
                    )
                    story_content = gr.Textbox(
                        label="Story Content",
                        lines=5,
                        placeholder="Write your story here..."
                    )
                    story_file = gr.File(
                        label="Or Upload a .txt file",
                        file_types=[".txt"]
                    )

        # Comic Style Tab
        with gr.TabItem("2️⃣ Comic Style"):
            with gr.Row():
                with gr.Column():
                    art_style = gr.Dropdown(
                        choices=["comic", "anime", "fairy tale illustration", "realistic"],
                        label="Art Style",
                        value="comic",
                        info="Choose the visual style for your comic"
                    )
                    num_frames = gr.Slider(
                        minimum=1,
                        maximum=6,
                        step=1,
                        label="Number of Frames",
                        value=2,
                        info="How many panels should your comic have?"
                    )
                    layout_style = gr.Radio(
                        choices=["default", "option1", "option2"],
                        label="Layout Style",
                        value="default",
                        info="Choose the panel arrangement style"
                    )
                    frame_color = gr.ColorPicker(
                        label="Frame Color",
                        value="#4A4A4A",
                        info="Choose the color for panel borders"
                    )
                    border_thickness = gr.Slider(
                        minimum=1,
                        maximum=8,
                        step=0.5,
                        label="Border Thickness",
                        value=3
                    )

        # Text Settings Tab
        with gr.TabItem("3️⃣ Text Settings"):
            with gr.Row():
                with gr.Column():
                    font_size = gr.Slider(
                        minimum=8,
                        maximum=24,
                        step=1,
                        label="Font Size",
                        value=12
                    )
                    dialogue_position = gr.Radio(
                        choices=["inside_top", "inside_bottom", "outside_bottom"],
                        label="Dialogue Position",
                        value="inside_bottom",
                        info="Where should the dialogue bubbles appear?"
                    )

            # Advanced Settings Tab
        with gr.TabItem("⚙️ Advanced"):
            with gr.Row():
                with gr.Column():
                    full_fill = gr.Checkbox(
                        label="Full Fill Images",
                        value=False,
                        info="Should images fill the entire panel?"
                    )
                    custom_layout = gr.Textbox(
                        label="Custom Layout (JSON format)",
                        lines=2,
                        placeholder="Advanced: Enter custom panel layout in JSON format",
                        info="For advanced users: Customize panel positions and sizes"
                    )

        # Output Section
    with gr.Row():
        generate_btn = gr.Button("Generate Comic", variant="primary")

    with gr.Row():
        gallery = gr.Gallery(label="Generated Comic Frames")
        pdf_output = gr.File(label="Download Comic PDF")

        # Connect the interface
    generate_btn.click(
        interface,
        inputs=[
            story_content,
            story_file,
            title,
            num_frames,
            art_style,
            font_size,
            border_thickness,
            dialogue_position,
            frame_color,
            full_fill,
            custom_layout,
            layout_style
        ],
        outputs=[gallery, pdf_output]
    )

if __name__ == "__main__":
    iface.launch()