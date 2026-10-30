import os
import math
# pyrefly: ignore[missing-import]
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# 1. Generate favicon.svg (Vector Scalable Favicon with Dark/Light Support)
# --------------------------------------------------------------------------
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100%" height="100%">
  <rect width="24" height="24" rx="6.5" fill="#09090b" stroke="#27272a" stroke-width="0.8"/>
  <!-- Pure Monochrome Black & White Video Logo -->
  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm0 2v12h16V6H4zm6 2.5l6 3.5-6 3.5v-7z" 
        fill="#ffffff"/>
</svg>
"""

with open(os.path.join(STATIC_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)
print("Created static/favicon.svg")

# Light Mode SVG Favicon
svg_light_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100%" height="100%">
  <rect width="24" height="24" rx="6.5" fill="#ffffff" stroke="#e4e4e7" stroke-width="0.8"/>
  <!-- Pure Monochrome Black & White Video Logo (Light Variant) -->
  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm0 2v12h16V6H4zm6 2.5l6 3.5-6 3.5v-7z" 
        fill="#09090b"/>
</svg>
"""

with open(os.path.join(STATIC_DIR, "favicon-light.svg"), "w", encoding="utf-8") as f:
    f.write(svg_light_content)
print("Created static/favicon-light.svg")

# --------------------------------------------------------------------------
# 2. Render High-Resolution Raster Base Icon with New Monochrome Logo
# --------------------------------------------------------------------------
def render_base_icon(size=512, is_light=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    scale = size / 24.0

    def s(v):
        return int(round(v * scale))

    bg_col = (255, 255, 255, 255) if is_light else (9, 9, 11, 255)
    border_col = (228, 228, 231, 255) if is_light else (39, 39, 42, 255)
    icon_col = (9, 9, 11, 255) if is_light else (255, 255, 255, 255)

    pad = max(1, s(0.75))
    radius = max(3, s(6.5))
    border_w = max(1, s(0.8))

    draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=radius, fill=bg_col, outline=border_col, width=border_w)

    # Outer film frame outline: M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z
    frame_x1, frame_y1 = s(4.2), s(4.2)
    frame_x2, frame_y2 = s(19.8), s(19.8)
    frame_rad = max(2, s(2.0))
    line_w = max(1, s(1.75))

    draw.rounded_rectangle([frame_x1, frame_y1, frame_x2, frame_y2], radius=frame_rad, outline=icon_col, width=line_w)

    # Top & bottom film horizontal divider lines (cutout at y=6 and y=18)
    draw.line([(frame_x1, s(6.2)), (frame_x2, s(6.2))], fill=icon_col, width=line_w)
    draw.line([(frame_x1, s(17.8)), (frame_x2, s(17.8))], fill=icon_col, width=line_w)

    # Center play triangle: (10, 8.5) -> (16, 12) -> (10, 15.5)
    tri_pts = [
        (s(10.0), s(8.5)),
        (s(16.0), s(12.0)),
        (s(10.0), s(15.5))
    ]
    draw.polygon(tri_pts, fill=icon_col)

    return img

base_icon_512 = render_base_icon(512, is_light=False)
base_icon_512.save(os.path.join(STATIC_DIR, "icon-512.png"), "PNG")
print("Created static/icon-512.png")

# Icon 192x192
icon_192 = render_base_icon(192, is_light=False)
icon_192.save(os.path.join(STATIC_DIR, "icon-192.png"), "PNG")
print("Created static/icon-192.png")

# Apple touch icon 180x180
apple_icon = render_base_icon(180, is_light=False)
apple_bg = Image.new("RGBA", (180, 180), (9, 9, 11, 255))
apple_final = Image.alpha_composite(apple_bg, apple_icon)
apple_final.save(os.path.join(STATIC_DIR, "apple-touch-icon.png"), "PNG")
apple_final.save(os.path.join(STATIC_DIR, "apple-touch-icon-precomposed.png"), "PNG")
print("Created static/apple-touch-icon.png and apple-touch-icon-precomposed.png")

# Favicon PNGs
fav_32 = render_base_icon(32, is_light=False)
fav_32.save(os.path.join(STATIC_DIR, "favicon-32x32.png"), "PNG")

fav_16 = render_base_icon(16, is_light=False)
fav_16.save(os.path.join(STATIC_DIR, "favicon-16x16.png"), "PNG")

fav_light_32 = render_base_icon(32, is_light=True)
fav_light_32.save(os.path.join(STATIC_DIR, "favicon-light-32x32.png"), "PNG")

fav_light_16 = render_base_icon(16, is_light=True)
fav_light_16.save(os.path.join(STATIC_DIR, "favicon-light-16x16.png"), "PNG")
print("Created static/favicon-32x32.png and static/favicon-16x16.png")

# Favicon.ico multi-resolution (monochrome logo)
fav_48 = render_base_icon(48, is_light=False)
fav_48.save(
    os.path.join(STATIC_DIR, "favicon.ico"),
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)]
)
print("Created static/favicon.ico")

fav_light_48 = render_base_icon(48, is_light=True)
fav_light_48.save(
    os.path.join(STATIC_DIR, "favicon-light.ico"),
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)]
)
print("Created static/favicon-light.ico")

# --------------------------------------------------------------------------
# 3. Generate Social Share Hero Banners (og-image.png & og-image-light.png)
# --------------------------------------------------------------------------
def render_og_hero_image():
    W, H = 1200, 630
    og = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    draw = ImageDraw.Draw(og)

    # Ambient radial gradient glows
    glow1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g1_draw = ImageDraw.Draw(glow1)
    g1_draw.ellipse([60, -80, 680, 520], fill=(249, 115, 22, 45))
    g1_draw.ellipse([700, 150, 1300, 750], fill=(99, 102, 241, 40))
    glow1 = glow1.filter(ImageFilter.GaussianBlur(80))
    og = Image.alpha_composite(og, glow1)
    draw = ImageDraw.Draw(og)

    # Dark mesh grid lines
    for x in range(40, W, 80):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
    for y in range(40, H, 80):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)

    # Outer border
    draw.rectangle([12, 12, W - 12, H - 12], outline=(38, 44, 64, 255), width=2)

    # Place Hero App Icon on Left (New Monochrome Black & White Video Logo)
    hero_icon = render_base_icon(260, is_light=False)
    og.paste(hero_icon, (100, 185), hero_icon)

    # Load Fonts
    try:
        font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 72)
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
        font_desc = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    except Exception:
        font_badge = font_title = font_subtitle = font_desc = font_tag = ImageFont.load_default()

    # Right Content Area
    tx = 410

    # Badge: MiniMax H3 Native Audio & Video
    badge_text = "  ⚡ POWERED BY MINIMAX H3 + QWEN3-VL  "
    draw.rounded_rectangle([tx, 135, tx + 480, 175], radius=20, fill=(30, 36, 54, 255), outline=(249, 115, 22, 180), width=1)
    draw.text((tx + 18, 143), badge_text, fill=(253, 186, 116, 255), font=font_badge)

    # Main Title: Dual-Tone VidGen (Vid in white, Gen in vivid orange)
    vid_bbox = draw.textbbox((tx, 195), "Vid", font=font_title)
    vid_w = vid_bbox[2] - vid_bbox[0]
    draw.text((tx, 195), "Vid", fill=(255, 255, 255, 255), font=font_title)
    draw.text((tx + vid_w, 195), "Gen", fill=(249, 115, 22, 255), font=font_title)

    # Subtitle: Native Stereo Audio & High-Fidelity Video
    draw.text((tx, 290), "Next-Gen AI Video & Synchronized Audio", fill=(56, 189, 248, 255), font=font_subtitle)

    # Description
    desc_line1 = "Unlimited Image-to-Video generation powered by MiniMax H3"
    desc_line2 = "with crystal-clear native stereo dialogue, SFX & music."
    draw.text((tx, 355), desc_line1, fill=(203, 213, 225, 255), font=font_desc)
    draw.text((tx, 395), desc_line2, fill=(148, 163, 184, 255), font=font_desc)

    # Feature Pills at bottom
    pills = [
        ("NVIDIA RTX 5080", (34, 197, 94, 220)),
        ("9:16 Shorts & 16:9 Cinema", (147, 51, 234, 220)),
        ("Zero Subscription", (59, 130, 246, 220)),
        ("100% Unlimited Local", (249, 115, 22, 220))
    ]
    px = tx
    py = 460
    for label, col in pills:
        pill_w = len(label) * 11 + 28
        draw.rounded_rectangle([px, py, px + pill_w, py + 38], radius=19, fill=(18, 22, 34, 255), outline=col, width=1)
        draw.text((px + 14, py + 8), label, fill=(241, 245, 249, 255), font=font_tag)
        px += pill_w + 16

    # Bottom branding watermark with dual-tone
    wm_vid_bbox = draw.textbbox((W - 320, H - 45), "Vid", font=font_desc)
    wm_vid_w = wm_vid_bbox[2] - wm_vid_bbox[0]
    draw.text((W - 320, H - 45), "Vid", fill=(255, 255, 255, 220), font=font_desc)
    draw.text((W - 320 + wm_vid_w, H - 45), "Gen", fill=(249, 115, 22, 255), font=font_desc)
    wm_gen_bbox = draw.textbbox((W - 320 + wm_vid_w, H - 45), "Gen", font=font_desc)
    wm_gen_w = wm_gen_bbox[2] - wm_gen_bbox[0]
    draw.text((W - 320 + wm_vid_w + wm_gen_w, H - 45), " · Local AI Engine", fill=(100, 116, 139, 255), font=font_desc)

    og.save(os.path.join(STATIC_DIR, "og-image.png"), "PNG")
    print("Created static/og-image.png (1200x630)")

render_og_hero_image()

def render_og_hero_image_light():
    W, H = 1200, 630
    # Warm cream background matching UI light theme (#faf7f2)
    og = Image.new("RGBA", (W, H), (250, 247, 242, 255))
    draw = ImageDraw.Draw(og)

    # Ambient soft warm orange & peach radial glow
    glow1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g1_draw = ImageDraw.Draw(glow1)
    g1_draw.ellipse([60, -80, 680, 520], fill=(251, 146, 60, 55))
    g1_draw.ellipse([700, 150, 1300, 750], fill=(254, 215, 170, 65))
    glow1 = glow1.filter(ImageFilter.GaussianBlur(80))
    og = Image.alpha_composite(og, glow1)
    draw = ImageDraw.Draw(og)

    # Warm orange mesh grid lines matching UI light theme
    for x in range(40, W, 80):
        draw.line([(x, 0), (x, H)], fill=(249, 115, 22, 22), width=1)
    for y in range(40, H, 80):
        draw.line([(0, y), (W, y)], fill=(249, 115, 22, 22), width=1)

    # Outer border (subtle warm border)
    draw.rectangle([12, 12, W - 12, H - 12], outline=(231, 229, 224, 255), width=2)

    # Place Hero App Icon on Left (Monochrome Black & White on clean squircle)
    hero_icon = render_base_icon(260, is_light=True)
    og.paste(hero_icon, (100, 185), hero_icon)

    # Load Fonts
    try:
        font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 72)
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
        font_desc = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    except Exception:
        font_badge = font_title = font_subtitle = font_desc = font_tag = ImageFont.load_default()

    # Right Content Area
    tx = 410

    # Badge: MiniMax H3 Native Audio & Video
    badge_text = "  ⚡ POWERED BY MINIMAX H3 + QWEN3-VL  "
    draw.rounded_rectangle([tx, 135, tx + 480, 175], radius=20, fill=(254, 243, 199, 255), outline=(249, 115, 22, 180), width=1)
    draw.text((tx + 18, 143), badge_text, fill=(180, 83, 9, 255), font=font_badge)

    # Main Title: Dual-Tone VidGen (Vid in dark slate, Gen in vivid orange)
    vid_bbox = draw.textbbox((tx, 195), "Vid", font=font_title)
    vid_w = vid_bbox[2] - vid_bbox[0]
    draw.text((tx, 195), "Vid", fill=(15, 23, 42, 255), font=font_title)
    draw.text((tx + vid_w, 195), "Gen", fill=(249, 115, 22, 255), font=font_title)

    # Subtitle: Native Stereo Audio & High-Fidelity Video
    draw.text((tx, 290), "Next-Gen AI Video & Synchronized Audio", fill=(30, 41, 59, 255), font=font_subtitle)

    # Description
    desc_line1 = "Unlimited Image-to-Video generation powered by MiniMax H3"
    desc_line2 = "with crystal-clear native stereo dialogue, SFX & music."
    draw.text((tx, 355), desc_line1, fill=(71, 85, 105, 255), font=font_desc)
    draw.text((tx, 395), desc_line2, fill=(100, 116, 139, 255), font=font_desc)

    # Feature Pills at bottom
    pills = [
        ("NVIDIA RTX 5080", (22, 163, 74, 255)),
        ("9:16 Shorts & 16:9 Cinema", (126, 34, 206, 255)),
        ("Zero Subscription", (37, 99, 235, 255)),
        ("100% Unlimited Local", (217, 119, 6, 255))
    ]
    px = tx
    py = 460
    for label, col in pills:
        pill_w = len(label) * 11 + 28
        draw.rounded_rectangle([px, py, px + pill_w, py + 38], radius=19, fill=(255, 255, 255, 255), outline=col, width=1)
        draw.text((px + 14, py + 8), label, fill=(30, 41, 59, 255), font=font_tag)
        px += pill_w + 16

    # Bottom branding watermark with dual-tone
    wm_vid_bbox = draw.textbbox((W - 320, H - 45), "Vid", font=font_desc)
    wm_vid_w = wm_vid_bbox[2] - wm_vid_bbox[0]
    draw.text((W - 320, H - 45), "Vid", fill=(15, 23, 42, 220), font=font_desc)
    draw.text((W - 320 + wm_vid_w, H - 45), "Gen", fill=(249, 115, 22, 255), font=font_desc)
    wm_gen_bbox = draw.textbbox((W - 320 + wm_vid_w, H - 45), "Gen", font=font_desc)
    wm_gen_w = wm_gen_bbox[2] - wm_gen_bbox[0]
    draw.text((W - 320 + wm_vid_w + wm_gen_w, H - 45), " · Local AI Engine", fill=(148, 163, 184, 255), font=font_desc)

    og.save(os.path.join(STATIC_DIR, "og-image-light.png"), "PNG")
    print("Created static/og-image-light.png (1200x630)")

render_og_hero_image_light()

# --------------------------------------------------------------------------
# 4. Generate Web App Manifest (site.webmanifest)
# --------------------------------------------------------------------------
manifest_content = """{
  "name": "VidGen - MiniMax H3",
  "short_name": "VidGen",
  "description": "Unlimited Image-to-Video generation with native stereo audio powered by MiniMax H3",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#ffffff",
  "icons": [
    {
      "src": "/favicon-16x16.png",
      "sizes": "16x16",
      "type": "image/png"
    },
    {
      "src": "/favicon-32x32.png",
      "sizes": "32x32",
      "type": "image/png"
    },
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""

with open(os.path.join(STATIC_DIR, "site.webmanifest"), "w", encoding="utf-8") as f:
    f.write(manifest_content)
print("Created static/site.webmanifest")
