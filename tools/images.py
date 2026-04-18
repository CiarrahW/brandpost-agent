import json
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from agents import function_tool


OUTPUT_DIR = Path(__file__).parent.parent / "output"

BACKGROUND_SUFFIX = (
    ", poster background composition, "
    "soft atmospheric lighting, generous empty space in upper or lower area for text, "
    "no text, no typography, no symbols, no numbers, "
    "professional photography or illustration style, square format"
)

NEGATIVE_PROMPT = (
    "text, letter, word, typography, font, writing, watermark, "
    "logo, label, sign, caption, subtitle, title, inscription, "
    "number, digit, character, calligraphy, handwriting, graffiti, "
    "people, face, crowd, portrait"
)


@function_tool
def generate_image(
    brand_name: str,
    visual_description: str,
    trend: str,
    style: str,
) -> str:
    """
    Generate a clean, minimal poster background image using Pollinations.ai.
    The image is intentionally simple with large negative space for text overlay.
    Do NOT describe people or complex subjects — backgrounds only.

    Args:
        brand_name: Name of the brand or event.
        visual_description: Description of the background mood, colors, and atmosphere.
            Focus on: color palette, lighting, abstract elements, textures.
            Do NOT include people, text descriptions, or dense objects.
        trend: Current trend to incorporate as a subtle visual aesthetic.
        style: Overall visual style (e.g. 'futuristic dark blue', 'warm minimalist').

    Returns:
        JSON with the saved image path.
    """
    image_prompt = (
        f"{visual_description}, {style} style, "
        f"subtle {trend} aesthetic"
        + BACKGROUND_SUFFIX
    )

    encoded_prompt = quote(image_prompt)
    encoded_negative = quote(NEGATIVE_PROMPT)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?model=flux"
        f"&width=1024&height=1024&nologo=true"
        f"&negative_prompt={encoded_negative}"
        f"&seed={hash(brand_name + trend) % 99999}"
    )

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_brand = brand_name.replace(" ", "_").lower()
        filename = OUTPUT_DIR / f"{safe_brand}_{timestamp}.png"

        with open(filename, "wb") as f:
            f.write(response.content)

        return json.dumps({"saved_path": str(filename)})

    except Exception as e:
        return f"Error generating image: {str(e)}"
