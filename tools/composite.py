import json
from pathlib import Path
from agents import function_tool
from PIL import Image, ImageFilter, ImageDraw


@function_tool
def composite_person_on_poster(
    background_path: str,
    person_path: str,
    position: str = "right",
    person_scale: float = 0.6,
) -> str:
    """
    Composite a person's photo onto a background poster image with edge feathering.

    Args:
        background_path: Path to the background image (generated poster base).
        person_path: Path to the person's photo (JPEG or PNG).
        position: Where to place the person — 'left', 'right', or 'center'.
        person_scale: How tall the person should be relative to the poster height (0.0–1.0).

    Returns:
        JSON with the path to the composited image.
    """
    try:
        bg = Image.open(background_path).convert("RGBA")
        person = Image.open(person_path).convert("RGBA")
        W, H = bg.size

        # Scale person to desired height, preserve aspect ratio
        target_h = int(H * person_scale)
        ratio = target_h / person.height
        target_w = int(person.width * ratio)
        person = person.resize((target_w, target_h), Image.LANCZOS)

        # Create soft feathered mask for the person
        mask = Image.new("L", (target_w, target_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        feather = int(target_w * 0.12)
        mask_draw.rectangle(
            [feather, feather, target_w - feather, target_h - feather],
            fill=255,
        )
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
        person.putalpha(mask)

        # Determine paste position
        padding = int(W * 0.04)
        py = H - target_h  # bottom-aligned
        if position == "right":
            px = W - target_w - padding
        elif position == "left":
            px = padding
        else:  # center
            px = (W - target_w) // 2

        # Composite
        composite = bg.copy()
        composite.paste(person, (px, py), person)

        out_path = Path(background_path).with_stem(Path(background_path).stem + "_person")
        composite.convert("RGB").save(str(out_path), "PNG")

        return json.dumps({"saved_path": str(out_path)})

    except Exception as e:
        return f"Error compositing person: {str(e)}"
