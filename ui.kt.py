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
pdfmetrics.registerFont(TTFont('ComicSansMS', 'Fonts/dsf/DejaVuSans.ttf'))

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
            'option1': [(0, 0, 1, 0.4), (0, 0.4, 0.33, 0.6), (0.33, 0.4, 0.34, 0.6), (0.67, 0.4, 0.33, 0.6)],  # One top, three bottom
            'option2': [(0, 0, 0.25, 1), (0.25, 0, 0.25, 1), (0.5, 0, 0.25, 1), (0.75, 0, 0.25, 1)]  # Four vertical strips
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
                        (0, 0.67, 0.33, 0.33), (0.33, 0.67, 0.33, 0.33), (0.66, 0.67, 0.34, 0.33)],  # One top, two middle, three bottom
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
    # Đăng ký font Unicode
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'Fonts/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'Fonts/DejaVuSans-Bold.ttf'))
        main_font = 'DejaVuSans'
    except:
        try:
            pdfmetrics.registerFont(TTFont('ArialUnicode', 'Fonts/ArialUnicode.ttf'))
            main_font = 'ArialUnicode'
        except:
            main_font = 'ComicSansMS'
            print("Warning: No Unicode font available. Vietnamese characters may not display correctly.")

    pdf_path = "story_output.pdf"
    page_width, page_height = A4
    margin = 0.5 * inch
    content_width = page_width - 2 * margin
    content_height = page_height - 2 * margin

    c = canvas.Canvas(pdf_path, pagesize=A4)

    # First page - Images
    # Set title
    title_height = 1 * inch
    c.setFont(main_font, font_size + 8)
    c.setFillColor(Color(0.1, 0.1, 0.1))
    c.drawCentredString(page_width / 2, page_height - 0.5 * inch, title)

    # Adjust content area for images
    image_area_height = content_height * 0.8
    image_start_y = page_height - margin - title_height - image_area_height

    # Create flexible layout with specified style
    layout = create_flexible_layout(len(images), custom_layout, layout_style)

    # Parse frame color
    frame_color = Color(*[int(frame_color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)])

    # Map dialogue positions
    dialogue_position_map = {
        "Inside Top": "inside_top",
        "Inside Bottom": "inside_bottom",
        "Outside Bottom": "outside_bottom"
    }
    position = dialogue_position_map.get(dialogue_position, "inside_bottom")

    # Draw images
    for i, (img_path, (x, y, w, h)) in enumerate(zip(images, layout)):
        img_x = margin + x * content_width
        img_y = image_start_y + (1 - y - h) * image_area_height
        img_w = w * content_width
        img_h = h * image_area_height

        c.setStrokeColor(frame_color)
        c.setLineWidth(border_thickness)
        c.rect(img_x, img_y, img_w, img_h)

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

        if dialogue_position != "None":
            c.setFont(main_font, font_size)
            dialogue_text = f"{i + 1}"

            bubble_margin = 10
            text_width = c.stringWidth(dialogue_text, main_font, font_size)
            bubble_width = min(text_width + 2 * bubble_margin, img_w - 2 * bubble_margin)
            bubble_height = font_size + 2 * bubble_margin

            if position == "inside_bottom":
                bubble_x = img_x + img_w / 2 - bubble_width / 2
                bubble_y = img_y + bubble_height + border_thickness
            elif position == "outside_bottom":
                bubble_x = img_x + img_w / 2 - bubble_width / 2
                bubble_y = img_y - bubble_height
            else:  # inside_top
                bubble_x = img_x + img_w / 2 - bubble_width / 2
                bubble_y = img_y + img_h - bubble_height - border_thickness

            c.setFillColor(Color(1, 1, 1))
            c.setStrokeColor(frame_color)
            c.roundRect(bubble_x, bubble_y, bubble_width, bubble_height, 5, fill=1, stroke=1)

            c.setFillColor(Color(0.1, 0.1, 0.1))
            c.drawCentredString(bubble_x + bubble_width / 2, bubble_y + bubble_margin, dialogue_text)

    # New page for story
    c.showPage()

    # Story page settings
    c.setFont(main_font, font_size + 8)
    c.setFillColor(Color(0.1, 0.1, 0.1))
    c.drawCentredString(page_width / 2, page_height - 0.5 * inch, f"{title} - Story")

    # Draw story content
    text_object = c.beginText()
    text_object.setFont(main_font, font_size)
    text_object.setFillColor(Color(0.1, 0.1, 0.1))
    text_object.setTextOrigin(margin, page_height - margin - title_height)

    # Calculate maximum width for text wrapping
    max_width = page_width - 2 * margin

    # Process and draw text line by line
    y_position = page_height - margin - title_height
    current_page_height = margin
    line_height = font_size * 1.2

    lines = story_content.split('\n')

    for line in lines:
        # If empty line, add extra spacing
        if not line.strip():
            y_position -= line_height
            if y_position < margin:
                c.showPage()
                y_position = page_height - margin - title_height
            continue

        # Handle regular lines
        if len(line.strip()) > 0:
            # Wrap text if too long
            words = line.split()
            current_line = []

            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)

                # Check if current line is too wide
                if c.stringWidth(test_line, main_font, font_size) > max_width:
                    if len(current_line) > 1:
                        current_line.pop()  # Remove last word
                        final_line = ' '.join(current_line)
                        c.setFont(main_font, font_size)
                        c.drawString(margin, y_position, final_line)
                        current_line = [word]  # Start new line with remaining word
                    else:
                        # Handle case where single word is too long
                        c.setFont(main_font, font_size)
                        c.drawString(margin, y_position, test_line)
                        current_line = []

                    y_position -= line_height
                    if y_position < margin:
                        c.showPage()
                        y_position = page_height - margin - title_height

            # Draw remaining words in current line
            if current_line:
                final_line = ' '.join(current_line)
                c.setFont(main_font, font_size)
                c.drawString(margin, y_position, final_line)
                y_position -= line_height
                if y_position < margin:
                    c.showPage()
                    y_position = page_height - margin - title_height

    c.save()
    return pdf_path

def create_layout_preview(n, style='default'):
    layout = create_flexible_layout(n, layout_style=style)
    svg_content = f"""
    <svg viewBox="0 0 100 100" style="width: 100%; max-width: 200px; border: 1px solid #ddd; border-radius: 8px; padding: 8px;">
        <style>
            .frame {{ fill: white; stroke: #666; stroke-width: 1; }}
            .frame-number {{ font-size: 4px; fill: #666; text-anchor: middle; dominant-baseline: middle; }}
        </style>
        {''.join([
            f'<rect x="{x*100}" y="{y*100}" width="{w*100}" height="{h*100}" class="frame"/>'
            f'<text x="{(x*100 + w*50)}" y="{(y*100 + h*50)}" class="frame-number">{i+1}</text>'
            for i, (x,y,w,h) in enumerate(layout)
        ])}
    </svg>
    """
    return svg_content

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
        layout_style  # Thêm tham số này
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

    print(f"Story content: {story_content}")

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
        layout_style  # Thêm parameter này
    )

    return valid_images, pdf_path

# Create the main interface
with gr.Blocks(title="Story to Comic Generator", theme=gr.themes.Soft()) as iface:
    gr.Markdown("""
    # 📚 Story to Comic Generator
    Transform your stories into beautiful comic-style PDFs! Follow these simple steps:
    1. Enter your story
    2. Choose your comic style
    3. Customize text settings
    4. Generate your comic!
    """)

    with gr.Tabs():
        # Story Input Tab
        with gr.TabItem("📝 Story Input"):
            with gr.Row():
                with gr.Column(scale=2):
                    title = gr.Textbox(
                        label="Story Title",
                        value="My Comic Story",
                        placeholder="Enter an engaging title for your comic...",
                        elem_classes="input-title"
                    )
                    story_content = gr.Textbox(
                        label="Story Content",
                        lines=8,
                        placeholder="Once upon a time...",
                        elem_classes="input-story"
                    )
                    with gr.Column(scale=1):
                        gr.Markdown("""### 📤 Upload Story""")
                        story_file = gr.File(
                            label="Upload a .txt file",
                            file_types=[".txt"],
                            elem_classes="file-upload"
                        )
                        gr.Markdown("""
                                    *Tips for better stories:*
                                    - Keep it concise
                                    - Include clear scene transitions
                                    - Focus on key moments
                                    """)

                    # Comic Style Tab
                with gr.TabItem("🎨 Comic Style"):
                    with gr.Row():
                        with gr.Column():
                            num_frames = gr.Slider(
                                minimum=1,
                                maximum=6,
                                step=1,
                                label="Number of Frames",
                                value=2,
                                info="How many panels should your comic have?",
                                elem_classes="slider-frames"
                            )

                            # Thêm Layout Style selector
                            layout_style = gr.Radio(
                                choices=["default", "option1", "option2"],
                                label="Layout Style",
                                value="default",
                                info="Choose the arrangement of your comic panels"
                            )

                            art_style = gr.Dropdown(
                                choices=["comic", "anime", "fairy tale illustration", "realistic"],
                                label="Art Style",
                                value="comic",
                                info="Choose the visual style for your comic",
                                elem_classes="dropdown-style"
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
                        with gr.Column():
                            gr.Markdown("### 📐 Layout Preview")
                            layout_preview = gr.HTML(value=create_layout_preview(2))


                            # Update preview when either num_frames or layout_style changes
                            def update_preview(frames, style):
                                return create_layout_preview(frames, style)


                            num_frames.change(
                                fn=update_preview,
                                inputs=[num_frames, layout_style],
                                outputs=[layout_preview]
                            )
                            layout_style.change(
                                fn=update_preview,
                                inputs=[num_frames, layout_style],
                                outputs=[layout_preview]
                            )

                    # Text Settings Tab
                with gr.TabItem("✍️ Text Settings"):
                    with gr.Row():
                        with gr.Column():
                            font_size = gr.Slider(
                                minimum=8,
                                maximum=24,
                                step=1,
                                label="Font Size",
                                value=12,
                                info="Adjust the size of text in your comic"
                            )
                            dialogue_position = gr.Radio(
                                choices=["Inside Top", "Inside Bottom", "Outside Bottom"],
                                label="Dialogue Position",
                                value="Inside Bottom",
                                info="Where should the dialogue bubbles appear?"
                            )
                        with gr.Column():
                            gr.Markdown("""
                                    ### 💡 Text Tips
                                    - Larger font sizes work better for shorter text
                                    - Inside Bottom is recommended for most comics
                                    - Consider the balance between text and images
                                    """)

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
                                lines=4,
                                placeholder='Example: [[0,0,0.5,1], [0.5,0,0.5,1]]',
                                info="Format: [[x, y, width, height], ...]"
                            )
                        with gr.Column():
                            gr.Markdown("""
                                    ### 📐 Custom Layout Guide
                                    Each panel is defined by 4 values:
                                    1. X position (0-1)
                                    2. Y position (0-1)
                                    3. Width (0-1)
                                    4. Height (0-1)

                                    *Values are proportional to page width/height*
                                    """)

    # Output Section
    with gr.Row():
        generate_btn = gr.Button(
            "🎨 Generate Comic",
            variant="primary",
            scale=2,
            size="lg"
        )

    with gr.Row():
        with gr.Column():
            gallery = gr.Gallery(
                label="Generated Comic Frames",
                elem_classes="gallery-output"
            )
        with gr.Column():
            pdf_output = gr.File(
                label="📥 Download Comic PDF",
                elem_classes="pdf-output"
            )

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
            layout_style  # Thêm input này
        ],
        outputs=[gallery, pdf_output]
    )

if __name__ == "__main__":
    iface.launch()