import json
from pathlib import Path
from agents import function_tool
from PIL import Image, ImageDraw, ImageFont, ImageFilter


FONT_STYLES = {
    # style_name: (title_path, body_path)
    "modern":    ("/System/Library/Fonts/Supplemental/Futura.ttc",
                  "/System/Library/Fonts/Supplemental/Futura.ttc"),
    "luxury":    ("/System/Library/Fonts/Supplemental/Bodoni 72.ttc",
                  "/System/Library/Fonts/Supplemental/Bodoni 72.ttc"),
    "editorial": ("/System/Library/Fonts/Supplemental/Didot.ttc",
                  "/System/Library/Fonts/Supplemental/GillSans.ttc"),
    "classic":   ("/System/Library/Fonts/Supplemental/Baskerville.ttc",
                  "/System/Library/Fonts/Supplemental/Baskerville.ttc"),
    "bold":      ("/System/Library/Fonts/Supplemental/Rockwell.ttc",
                  "/System/Library/Fonts/Supplemental/Rockwell.ttc"),
    "minimal":   ("/System/Library/Fonts/Supplemental/GillSans.ttc",
                  "/System/Library/Fonts/Supplemental/GillSans.ttc"),
    "default":   ("/System/Library/Fonts/Helvetica.ttc",
                  "/System/Library/Fonts/Helvetica.ttc"),
}


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    if Path(path).exists():
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _find_font(size: int, bold: bool = False, style: str = "default") -> ImageFont.FreeTypeFont:
    title_path, body_path = FONT_STYLES.get(style, FONT_STYLES["default"])
    path = title_path if bold else body_path
    font = _load_font(path, size)
    if font == ImageFont.load_default():
        # fallback chain
        for fallback in ["/System/Library/Fonts/Helvetica.ttc",
                         "/System/Library/Fonts/Supplemental/Arial.ttf"]:
            font = _load_font(fallback, size)
            if font != ImageFont.load_default():
                break
    return font


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.getbbox(test)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _text_block_height(lines: list[str], line_h: int) -> int:
    return len(lines) * line_h


def _draw_text_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    start_xy: tuple,
    line_h: int,
    fill: tuple,
    align: str = "left",
    max_width: int = 0,
    shadow: bool = True,
):
    x, y = start_xy
    for line in lines:
        lw = font.getbbox(line)[2]
        if align == "center" and max_width:
            lx = x + (max_width - lw) // 2
        elif align == "right" and max_width:
            lx = x + max_width - lw
        else:
            lx = x
        if shadow:
            draw.text((lx + 3, y + 3), line, font=font, fill=(0, 0, 0, 160))
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_h
    return y


def _add_gradient_band(img: Image.Image, region: str, opacity: int) -> Image.Image:
    """Add a dark gradient band at 'top', 'bottom', or 'full' for text readability."""
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    band = int(H * 0.55)

    if region == "bottom":
        for i in range(band):
            alpha = int(opacity * (i / band) ** 1.4)
            draw.rectangle([(0, H - band + i), (W, H - band + i + 1)], fill=(0, 0, 0, alpha))
    elif region == "top":
        for i in range(band):
            alpha = int(opacity * ((band - i) / band) ** 1.4)
            draw.rectangle([(0, i), (W, i + 1)], fill=(0, 0, 0, alpha))
    elif region == "full":
        for i in range(H):
            alpha = int(opacity * 0.55)
            draw.rectangle([(0, i), (W, i + 1)], fill=(0, 0, 0, alpha))
    elif region == "split":
        for i in range(band // 2):
            alpha = int(opacity * ((band // 2 - i) / (band // 2)) ** 1.4)
            draw.rectangle([(0, i), (W, i + 1)], fill=(0, 0, 0, alpha))
        for i in range(band):
            alpha = int(opacity * (i / band) ** 1.4)
            draw.rectangle([(0, H - band + i), (W, H - band + i + 1)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img, overlay)


@function_tool
def add_text_overlay(
    image_path: str,
    title: str,
    subtitle: str,
    body: str,
    text_color: str = "white",
    layout: str = "bottom-center",
    font_style: str = "modern",
    overlay_opacity: int = 160,
) -> str:
    """
    Add professionally laid-out text onto an existing image with multiple layout and font options.

    Args:
        image_path: Path to the base image file.
        title: Main headline (largest text).
        subtitle: Secondary line (speaker name, date, tagline).
        body: Additional detail (venue, website). Use empty string if none.
        text_color: 'white', 'black', 'gold', or 'cyan'.
        layout: Text layout style. Choose from:
            - 'bottom-center': All text centered at the bottom (default, good for most posters)
            - 'bottom-left': All text left-aligned at the bottom
            - 'top-center': All text centered at the top
            - 'top-left': All text left-aligned at the top
            - 'centered': All text centered in the middle of the image
            - 'split': Title at the top, subtitle+body at the bottom (great for event posters)
            - 'editorial': Oversized title fills most of the image, body small at bottom
        font_style: Typography style. Choose from:
            - 'modern': Futura — geometric, clean, tech/startup brands
            - 'luxury': Bodoni 72 — high contrast, elegant, fashion/beauty
            - 'editorial': Didot title + GillSans body — magazine-style
            - 'classic': Baskerville — traditional, authoritative, academic
            - 'bold': Rockwell — slab serif, strong, impactful
            - 'minimal': GillSans — clean humanist sans-serif
            - 'default': Helvetica — reliable universal fallback
        overlay_opacity: Darkness of gradient behind text for readability (0-255, default 160).

    Returns:
        JSON with the path to the new image with text applied.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        W, H = img.size
        margin = int(W * 0.07)
        text_w = W - 2 * margin

        color_map = {
            "white": (255, 255, 255, 255),
            "black": (20, 20, 20, 255),
            "gold": (255, 210, 60, 255),
            "cyan": (100, 240, 255, 255),
        }
        fill = color_map.get(text_color.lower(), (255, 255, 255, 255))
        sub_fill = (*fill[:3], 210)
        body_fill = (*fill[:3], 170)

        # Font sizes
        if layout == "editorial":
            title_size = int(H * 0.11)
        else:
            title_size = int(H * 0.072)
        sub_size = int(H * 0.042)
        body_size = int(H * 0.030)
        line_gap = int(H * 0.022)

        title_font = _find_font(title_size, bold=True, style=font_style)
        sub_font = _find_font(sub_size, style=font_style)
        body_font = _find_font(body_size, style=font_style)

        title_lines = _wrap_text(title, title_font, text_w)
        sub_lines = _wrap_text(subtitle, sub_font, text_w) if subtitle else []
        body_lines = _wrap_text(body, body_font, text_w) if body else []

        title_lh = int(title_size * 1.2)
        sub_lh = int(sub_size * 1.25)
        body_lh = int(body_size * 1.3)

        title_h = _text_block_height(title_lines, title_lh)
        sub_h = _text_block_height(sub_lines, sub_lh) if sub_lines else 0
        body_h = _text_block_height(body_lines, body_lh) if body_lines else 0
        total_h = title_h + (line_gap + sub_h if sub_h else 0) + (line_gap + body_h if body_h else 0)

        # Apply gradient
        if layout in ("bottom-center", "bottom-left"):
            img = _add_gradient_band(img, "bottom", overlay_opacity)
        elif layout in ("top-center", "top-left"):
            img = _add_gradient_band(img, "top", overlay_opacity)
        elif layout == "centered":
            img = _add_gradient_band(img, "full", overlay_opacity)
        elif layout == "split":
            img = _add_gradient_band(img, "split", overlay_opacity)
        elif layout == "editorial":
            img = _add_gradient_band(img, "full", min(overlay_opacity, 100))

        draw = ImageDraw.Draw(img)

        def draw_all(start_y: int, align: str):
            y = start_y
            y = _draw_text_block(draw, title_lines, title_font, (margin, y),
                                  title_lh, fill, align, text_w)
            if sub_lines:
                y += line_gap
                y = _draw_text_block(draw, sub_lines, sub_font, (margin, y),
                                      sub_lh, sub_fill, align, text_w)
            if body_lines:
                y += line_gap
                _draw_text_block(draw, body_lines, body_font, (margin, y),
                                  body_lh, body_fill, align, text_w)

        if layout == "bottom-center":
            draw_all(H - margin - total_h, "center")
        elif layout == "bottom-left":
            draw_all(H - margin - total_h, "left")
        elif layout == "top-center":
            draw_all(margin, "center")
        elif layout == "top-left":
            draw_all(margin, "left")
        elif layout == "centered":
            draw_all((H - total_h) // 2, "center")
        elif layout == "split":
            # Title at top
            _draw_text_block(draw, title_lines, title_font, (margin, margin),
                              title_lh, fill, "center", text_w)
            # Subtitle + body at bottom
            bottom_h = sub_h + (line_gap + body_h if body_h else 0)
            y = H - margin - bottom_h
            if sub_lines:
                y = _draw_text_block(draw, sub_lines, sub_font, (margin, y),
                                      sub_lh, sub_fill, "center", text_w)
            if body_lines:
                y += line_gap
                _draw_text_block(draw, body_lines, body_font, (margin, y),
                                  body_lh, body_fill, "center", text_w)
        elif layout == "editorial":
            # Large title centered vertically with slight upward bias
            title_y = int(H * 0.22)
            y = _draw_text_block(draw, title_lines, title_font, (margin, title_y),
                                  title_lh, fill, "center", text_w)
            if sub_lines:
                y += line_gap * 2
                y = _draw_text_block(draw, sub_lines, sub_font, (margin, y),
                                      sub_lh, sub_fill, "center", text_w)
            if body_lines:
                _draw_text_block(draw, body_lines, body_font,
                                  (margin, H - margin - body_h),
                                  body_lh, body_fill, "center", text_w)

        out_path = Path(image_path).with_stem(Path(image_path).stem + "_text")
        img.convert("RGB").save(str(out_path), "PNG")
        return json.dumps({"saved_path": str(out_path)})

    except Exception as e:
        return f"Error adding text overlay: {str(e)}"
