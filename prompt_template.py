PROMPT_GENERATION_TEMPLATE = """
Generate {number} text-to-image prompts illustrating static scenes from the provided story. Each prompt must include:

- **Character(s):** Describe the main character(s) with specific traits (e.g., hair color, dress style, age) that remain consistent across all prompts.
- **Scene:** Detail the setting, including lighting and atmosphere.
- **Objects:** Highlight key objects relevant to the scene.
- **Event:** Capture a static moment, avoiding action language.
- **Style:** Use {style} for all illustrations.

Format the output as follows:

[1] "Description of the first scene with consistent character details, scene, objects, and style."
[2] "Description of the second scene with the same character details, scene, objects, and style."
[3] "Continue this for each key event in the story up to {number} events."

Ensure all prompts are concise, written in English, and clearly illustrate each event while adhering to the style: {style}. Provide only the formatted output; do not include any additional information or context.

The story for generating prompts is:
{story}
"""
