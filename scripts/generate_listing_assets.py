import argparse
import json
import os
import random
import shutil
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


BRAND = "AutonomaX Commerce"
DEFAULT_OUTPUT = Path("static/assets/listings")
MARKETING_OUTPUT = Path("marketing_assets")


def load_catalog(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pick_palette(seed: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    random.seed(seed)
    palettes = [
        ((10, 19, 36), (30, 64, 175), (248, 200, 70)),
        ((16, 24, 40), (34, 197, 94), (14, 116, 144)),
        ((12, 20, 45), (59, 130, 246), (251, 113, 133)),
        ((15, 23, 42), (245, 158, 11), (239, 68, 68)),
        ((8, 18, 30), (99, 102, 241), (56, 189, 248)),
    ]
    return random.choice(palettes)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    if hasattr(draw, "textlength"):
        return draw.textlength(text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    words = text.split()
    if not words:
        return []
    lines: List[str] = []
    current: List[str] = []
    for word in words:
        test = " ".join(current + [word])
        if text_width(draw, test, font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def make_gradient(size: Tuple[int, int], start: Tuple[int, int, int], end: Tuple[int, int, int]) -> Image.Image:
    width, height = size
    base = Image.new("RGBA", size, (*start, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(start[0] + (end[0] - start[0]) * ratio)
        g = int(start[1] + (end[1] - start[1]) * ratio)
        b = int(start[2] + (end[2] - start[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return base


def render_card(
    size: Tuple[int, int],
    title: str,
    subtitle: str,
    badge: str,
    palette: Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]
) -> Image.Image:
    background = make_gradient(size, palette[0], palette[1])
    draw = ImageDraw.Draw(background)
    width, height = size

    accent = palette[2]
    draw.ellipse((width * 0.68, height * -0.2, width * 1.2, height * 0.5), fill=(*accent, 120))
    draw.ellipse((width * -0.2, height * 0.6, width * 0.4, height * 1.2), fill=(255, 255, 255, 40))

    title_font = load_font(int(height * 0.08), bold=True)
    subtitle_font = load_font(int(height * 0.035))
    badge_font = load_font(int(height * 0.03), bold=True)
    brand_font = load_font(int(height * 0.028))

    max_title_width = int(width * 0.78)
    lines = wrap_text(draw, title, title_font, max_title_width)
    title_block_height = len(lines) * int(height * 0.09)

    y = int(height * 0.18)
    for line in lines[:3]:
        draw.text((width * 0.1, y), line, font=title_font, fill=(248, 250, 252))
        y += int(height * 0.09)

    subtitle_lines = wrap_text(draw, subtitle, subtitle_font, int(width * 0.72))
    y += int(height * 0.02)
    for line in subtitle_lines[:3]:
        draw.text((width * 0.1, y), line, font=subtitle_font, fill=(203, 213, 225))
        y += int(height * 0.05)

    badge_width = text_width(draw, badge, badge_font) + 30
    badge_height = int(height * 0.06)
    badge_box = (width * 0.1, height * 0.78, width * 0.1 + badge_width, height * 0.78 + badge_height)
    draw.rounded_rectangle(badge_box, radius=badge_height // 2, fill=(*accent, 200))
    draw.text((badge_box[0] + 15, badge_box[1] + badge_height * 0.2), badge, font=badge_font, fill=(15, 23, 42))

    draw.text((width * 0.1, height * 0.9), BRAND, font=brand_font, fill=(148, 163, 184))

    return background.convert("RGB")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_assets_for_product(product: Dict[str, Any], output_root: Path, marketing_root: Path) -> Dict[str, Path]:
    sku = product.get("sku", "unknown")
    title = product.get("title", "Untitled")
    subtitle = product.get("short_description", "Launch-ready product asset.")
    palette = pick_palette(sku)

    product_dir = output_root / sku
    marketing_dir = marketing_root / sku
    ensure_dir(product_dir)
    ensure_dir(marketing_dir)

    listing_path = product_dir / "listing.png"
    thumb_path = product_dir / "thumbnail.png"
    banner_path = product_dir / "banner.png"
    video_path = product_dir / "preview.mp4"

    listing_img = render_card((1200, 1200), title, subtitle, "Launch Ready", palette)
    listing_img.save(listing_path)

    thumb_img = render_card((1280, 720), title, subtitle, "Passive Income", palette)
    thumb_img.save(thumb_path)

    banner_img = render_card((1920, 1080), title, subtitle, "Automation Stack", palette)
    banner_img.save(banner_path)

    shutil.copy2(listing_path, marketing_dir / listing_path.name)
    shutil.copy2(thumb_path, marketing_dir / thumb_path.name)
    shutil.copy2(banner_path, marketing_dir / banner_path.name)

    video_result = generate_preview_video(listing_path, video_path, marketing_dir / "preview.mp4")
    return {
        "listing": listing_path,
        "thumbnail": thumb_path,
        "banner": banner_path,
        "video": video_result,
    }


def generate_preview_video(image_path: Path, video_path: Path, marketing_video_path: Path) -> Path:
    if not shutil.which("ffmpeg"):
        guide_path = marketing_video_path.parent / "preview_video_guide.txt"
        guide_path.write_text(
            "FFmpeg not available. Use the listing.png image to create a 6-8 second promo clip in Canva or CapCut.",
            encoding="utf-8",
        )
        return guide_path

    try:
        from moviepy.editor import ImageClip
    except Exception:
        guide_path = marketing_video_path.parent / "preview_video_guide.txt"
        guide_path.write_text(
            "MoviePy not available. Use the listing.png image to create a 6-8 second promo clip in Canva or CapCut.",
            encoding="utf-8",
        )
        return guide_path

    clip = ImageClip(str(image_path)).set_duration(6)
    clip.write_videofile(str(video_path), fps=24, codec="libx264", audio=False, verbose=False, logger=None)
    shutil.copy2(video_path, marketing_video_path)
    return video_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate listing visuals for catalog SKUs.")
    parser.add_argument("--catalog", default="docs/commerce/product_catalog.json")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--marketing-output", default=str(MARKETING_OUTPUT))
    parser.add_argument("--sku", action="append", dest="skus")
    args = parser.parse_args()

    catalog = load_catalog(Path(args.catalog))
    output_root = Path(args.output)
    marketing_root = Path(args.marketing_output)
    ensure_dir(output_root)
    ensure_dir(marketing_root)

    count = 0
    for product in catalog.get("products", []):
        if args.skus and product.get("sku") not in args.skus:
            continue
        generate_assets_for_product(product, output_root, marketing_root)
        count += 1

    print(f"Generated listing assets for {count} products.")


if __name__ == "__main__":
    main()
