import os
import math
# pyrefly: ignore[missing-import]
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# 1. Generate favicon.svg (Vector Scalable Favicon)
# --------------------------------------------------------------------------
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090a10"/>
      <stop offset="50%" stop-color="#11131f"/>
      <stop offset="100%" stop-color="#181a28"/>
    </linearGradient>
    <linearGradient id="primaryGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="45%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#a855f7"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#cbd5e1"/>
    </linearGradient>
    <radialGradient id="glowGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
    </radialGradient>
    <filter id="dropGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Squircle Base with high-contrast border -->
  <rect x="20" y="20" width="472" height="472" rx="112" fill="url(#bgGrad)" stroke="#31384f" stroke-width="8"/>

  <!-- Radial Glow Behind Emblem -->
  <circle cx="256" cy="256" r="190" fill="url(#glowGrad)"/>

  <!-- Subtly grooved orbit ring for video/audio synergy -->
  <circle cx="256" cy="256" r="162" fill="none" stroke="#252a3d" stroke-width="5" stroke-dasharray="14 10"/>

  <!-- Native Audio Soundwave Bars on Left -->
  <rect x="94" y="220" width="12" height="72" rx="6" fill="#475569" opacity="0.7"/>
  <rect x="118" y="190" width="12" height="132" rx="6" fill="#6366f1" opacity="0.85"/>
  <rect x="142" y="162" width="12" height="188" rx="6" fill="url(#primaryGrad)"/>

  <!-- High-Energy Video Play Triangle -->
  <path d="M 204 148 C 204 136 218 130 228 137 L 374 243 C 383 250 383 262 374 269 L 228 375 C 218 382 204 376 204 364 Z" 
        fill="url(#primaryGrad)" filter="url(#dropGlow)"/>

  <!-- MiniMax High-Speed Lightning Bolt Core in Center -->
  <path d="M 278 188 L 234 262 L 268 262 L 240 324 L 312 246 L 274 246 Z" 
        fill="#ffffff" opacity="0.96"/>

  <!-- Upper Glass Sheen -->
  <path d="M 32 135 C 32 80 80 32 135 32 L 377 32 C 432 32 480 80 480 135 C 410 162 310 178 220 168 C 140 158 60 145 32 135 Z" 
        fill="#ffffff" opacity="0.08"/>
</svg>
"""

with open(os.path.join(STATIC_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)
print("Created static/favicon.svg")

# Light Mode SVG Favicon
svg_light_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="bgLightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="50%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#edf2f7"/>
    </linearGradient>
    <linearGradient id="primaryLightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7"/>
      <stop offset="45%" stop-color="#4f46e5"/>
      <stop offset="100%" stop-color="#9333ea"/>
    </linearGradient>
    <radialGradient id="glowLightGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
    </radialGradient>
    <filter id="dropLightGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Clean Light Squircle Base with crisp border -->
  <rect x="20" y="20" width="472" height="472" rx="112" fill="url(#bgLightGrad)" stroke="#cbd5e1" stroke-width="8"/>

  <!-- Radial Soft Glow Behind Emblem -->
  <circle cx="256" cy="256" r="190" fill="url(#glowLightGrad)"/>

  <!-- Subtly grooved orbit ring -->
  <circle cx="256" cy="256" r="162" fill="none" stroke="#e2e8f0" stroke-width="5" stroke-dasharray="14 10"/>

  <!-- Native Audio Soundwave Bars on Left -->
  <rect x="94" y="220" width="12" height="72" rx="6" fill="#94a3b8" opacity="0.8"/>
  <rect x="118" y="190" width="12" height="132" rx="6" fill="#6366f1" opacity="0.9"/>
  <rect x="142" y="162" width="12" height="188" rx="6" fill="url(#primaryLightGrad)"/>

  <!-- High-Energy Video Play Triangle -->
  <path d="M 204 148 C 204 136 218 130 228 137 L 374 243 C 383 250 383 262 374 269 L 228 375 C 218 382 204 376 204 364 Z" 
        fill="url(#primaryLightGrad)" filter="url(#dropLightGlow)"/>

  <!-- MiniMax High-Speed Lightning Bolt Core in Center -->
  <path d="M 278 188 L 234 262 L 268 262 L 240 324 L 312 246 L 274 246 Z" 
        fill="#ffffff" opacity="0.98"/>

  <!-- Upper Soft Sheen -->
  <path d="M 32 135 C 32 80 80 32 135 32 L 377 32 C 432 32 480 80 480 135 C 410 162 310 178 220 168 C 140 158 60 145 32 135 Z" 
        fill="#ffffff" opacity="0.5"/>
</svg>
"""

with open(os.path.join(STATIC_DIR, "favicon-light.svg"), "w", encoding="utf-8") as f:
    f.write(svg_light_content)
print("Created static/favicon-light.svg")

# --------------------------------------------------------------------------
# 2. Render High-Resolution Raster Base Icon (512x512)
# --------------------------------------------------------------------------
def render_base_icon(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor
    scale = size / 512.0

    def s(v):
        return int(round(v * scale))

    # Base squircle
    pad = s(20)
    w = size - 2 * pad
    r = s(112)
    
    # Outer dark squircle background
    draw.rounded_rectangle([pad, pad, pad + w, pad + w], radius=r, fill=(14, 16, 26, 255), outline=(49, 56, 79, 255), width=max(1, s(8)))

    # Subtle inner gradient overlay / glow
    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    center = (size // 2, size // 2)
    glow_r = s(160)
    glow_draw.ellipse([center[0] - glow_r, center[1] - glow_r, center[0] + glow_r, center[1] + glow_r], fill=(99, 102, 241, 70))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(s(25)))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # Soundwave bars (left)
    draw.rounded_rectangle([s(94), s(220), s(106), s(292)], radius=s(6), fill=(71, 85, 105, 200))
    draw.rounded_rectangle([s(118), s(190), s(130), s(322)], radius=s(6), fill=(99, 102, 241, 230))
    draw.rounded_rectangle([s(142), s(162), s(154), s(350)], radius=s(6), fill=(56, 189, 248, 255))

    # Play triangle polygon
    tri_pts = [
        (s(204), s(148)),
        (s(374), s(256)),
        (s(204), s(364))
    ]
    draw.polygon(tri_pts, fill=(129, 140, 248, 255))

    # Gradient highlight facet on play triangle
    facet_pts = [
        (s(204), s(148)),
        (s(374), s(256)),
        (s(204), s(256))
    ]
    draw.polygon(facet_pts, fill=(56, 189, 248, 220))

    # Lightning bolt inside
    bolt_pts = [
        (s(278), s(188)),
        (s(234), s(262)),
        (s(268), s(262)),
        (s(240), s(324)),
        (s(312), s(246)),
        (s(274), s(246))
    ]
    draw.polygon(bolt_pts, fill=(255, 255, 255, 250))

    return img

base_icon_512 = render_base_icon(512)
base_icon_512.save(os.path.join(STATIC_DIR, "icon-512.png"), "PNG")
print("Created static/icon-512.png")

# Icon 192x192
icon_192 = render_base_icon(192)
icon_192.save(os.path.join(STATIC_DIR, "icon-192.png"), "PNG")
print("Created static/icon-192.png")

# Apple touch icon 180x180 (with solid luxurious background, standard for iOS)
apple_icon = render_base_icon(180)
apple_bg = Image.new("RGBA", (180, 180), (10, 11, 18, 255))
apple_final = Image.alpha_composite(apple_bg, apple_icon)
apple_final.save(os.path.join(STATIC_DIR, "apple-touch-icon.png"), "PNG")
apple_final.save(os.path.join(STATIC_DIR, "apple-touch-icon-precomposed.png"), "PNG")
print("Created static/apple-touch-icon.png and apple-touch-icon-precomposed.png")

# Favicon PNGs
fav_32 = render_base_icon(32)
fav_32.save(os.path.join(STATIC_DIR, "favicon-32x32.png"), "PNG")

fav_16 = render_base_icon(16)
fav_16.save(os.path.join(STATIC_DIR, "favicon-16x16.png"), "PNG")
print("Created static/favicon-32x32.png and favicon-16x16.png")

# Favicon.ico multi-resolution
fav_48 = render_base_icon(48)
fav_48.save(
    os.path.join(STATIC_DIR, "favicon.ico"),
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)]
)
print("Created static/favicon.ico (16, 32, 48)")

# Light Mode Raster Favicons
def render_base_icon_light(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    scale = size / 512.0
    def s(v): return int(round(v * scale))
    pad = s(20)
    w = size - 2 * pad
    r = s(112)
    # White squircle base
    draw.rounded_rectangle([pad, pad, pad + w, pad + w], radius=r, fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=max(1, s(8)))
    # Soundwave bars
    draw.rounded_rectangle([s(94), s(220), s(106), s(292)], radius=s(6), fill=(148, 163, 184, 255))
    draw.rounded_rectangle([s(118), s(190), s(130), s(322)], radius=s(6), fill=(99, 102, 241, 255))
    draw.rounded_rectangle([s(142), s(162), s(154), s(350)], radius=s(6), fill=(2, 132, 199, 255))
    # Play triangle
    tri_pts = [(s(204), s(148)), (s(374), s(256)), (s(204), s(364))]
    draw.polygon(tri_pts, fill=(79, 70, 229, 255))
    # Lightning bolt inside
    bolt_pts = [(s(278), s(188)), (s(234), s(262)), (s(268), s(262)), (s(240), s(324)), (s(312), s(246)), (s(274), s(246))]
    draw.polygon(bolt_pts, fill=(255, 255, 255, 255))
    return img

fav_light_32 = render_base_icon_light(32)
fav_light_32.save(os.path.join(STATIC_DIR, "favicon-light-32x32.png"), "PNG")
fav_light_16 = render_base_icon_light(16)
fav_light_16.save(os.path.join(STATIC_DIR, "favicon-light-16x16.png"), "PNG")
fav_light_48 = render_base_icon_light(48)
fav_light_48.save(
    os.path.join(STATIC_DIR, "favicon-light.ico"),
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)]
)
print("Created static/favicon-light.ico, favicon-light-32x32.png, favicon-light-16x16.png")

# --------------------------------------------------------------------------
# 3. Generate Social Share Hero Banner (og-image.png: 1200x630)
# --------------------------------------------------------------------------
def render_og_hero_image():
    W, H = 1200, 630
    og = Image.new("RGBA", (W, H), (8, 9, 14, 255))
    draw = ImageDraw.Draw(og)

    # Ambient radial gradient glows
    glow1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g1_draw = ImageDraw.Draw(glow1)
    g1_draw.ellipse([80, -100, 680, 500], fill=(99, 102, 241, 55))
    g1_draw.ellipse([700, 150, 1300, 750], fill=(56, 189, 248, 45))
    glow1 = glow1.filter(ImageFilter.GaussianBlur(80))
    og = Image.alpha_composite(og, glow1)
    draw = ImageDraw.Draw(og)

    # Grid / circuit pattern effect
    for x in range(40, W, 80):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 7), width=1)
    for y in range(40, H, 80):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 7), width=1)

    # Outer border
    draw.rectangle([12, 12, W - 12, H - 12], outline=(38, 44, 64, 255), width=2)

    # Place Hero App Icon on Left / Center-Left (size 260x260)
    hero_icon = render_base_icon(260)
    og.paste(hero_icon, (100, 185), hero_icon)

    # Load Fonts
    try:
        font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 68)
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
        font_desc = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    except Exception:
        font_badge = font_title = font_subtitle = font_desc = font_tag = ImageFont.load_default()

    # Right Content Area
    tx = 410

    # Badge: MiniMax H3 Native Audio & Video
    badge_text = "  ⚡ POWERED BY MINIMAX H3 + QWEN3-VL  "
    draw.rounded_rectangle([tx, 140, tx + 480, 180], radius=20, fill=(30, 36, 54, 255), outline=(99, 102, 241, 180), width=1)
    draw.text((tx + 18, 148), badge_text, fill=(165, 180, 252, 255), font=font_badge)

    # Main Title: VideoGen Studio
    draw.text((tx, 200), "VideoGen Studio", fill=(255, 255, 255, 255), font=font_title)

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
        ("100% Unlimited Local", (245, 158, 11, 220))
    ]
    px = tx
    py = 460
    for label, col in pills:
        pill_w = len(label) * 11 + 28
        draw.rounded_rectangle([px, py, px + pill_w, py + 38], radius=19, fill=(18, 22, 34, 255), outline=col, width=1)
        draw.text((px + 14, py + 8), label, fill=(241, 245, 249, 255), font=font_tag)
        px += pill_w + 16

    # Bottom branding watermark
    draw.text((W - 320, H - 45), "VideoGen Studio · Local AI Engine", fill=(100, 116, 139, 255), font=font_desc)

    og.save(os.path.join(STATIC_DIR, "og-image.png"), "PNG")
    print("Created static/og-image.png (1200x630)")

render_og_hero_image()

def render_og_hero_image_light():
    W, H = 1200, 630
    og = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    draw = ImageDraw.Draw(og)

    # Ambient soft pastel radial glows
    glow1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g1_draw = ImageDraw.Draw(glow1)
    g1_draw.ellipse([80, -100, 680, 500], fill=(199, 210, 254, 110))
    g1_draw.ellipse([700, 150, 1300, 750], fill=(186, 230, 253, 95))
    glow1 = glow1.filter(ImageFilter.GaussianBlur(80))
    og = Image.alpha_composite(og, glow1)
    draw = ImageDraw.Draw(og)

    # Clean geometric grid lines
    for x in range(40, W, 80):
        draw.line([(x, 0), (x, H)], fill=(15, 23, 42, 10), width=1)
    for y in range(40, H, 80):
        draw.line([(0, y), (W, y)], fill=(15, 23, 42, 10), width=1)

    # Outer border
    draw.rectangle([12, 12, W - 12, H - 12], outline=(203, 213, 225, 255), width=2)

    # Place Hero App Icon on Left / Center-Left (size 260x260)
    hero_icon = render_base_icon(260)
    og.paste(hero_icon, (100, 185), hero_icon)

    # Load Fonts
    try:
        font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 68)
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
        font_desc = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    except Exception:
        font_badge = font_title = font_subtitle = font_desc = font_tag = ImageFont.load_default()

    # Right Content Area
    tx = 410

    # Badge: MiniMax H3 Native Audio & Video
    badge_text = "  ⚡ POWERED BY MINIMAX H3 + QWEN3-VL  "
    draw.rounded_rectangle([tx, 140, tx + 480, 180], radius=20, fill=(238, 242, 255, 255), outline=(99, 102, 241, 180), width=1)
    draw.text((tx + 18, 148), badge_text, fill=(67, 56, 202, 255), font=font_badge)

    # Main Title: VideoGen Studio
    draw.text((tx, 200), "VideoGen Studio", fill=(15, 23, 42, 255), font=font_title)

    # Subtitle: Native Stereo Audio & High-Fidelity Video
    draw.text((tx, 290), "Next-Gen AI Video & Synchronized Audio", fill=(79, 70, 229, 255), font=font_subtitle)

    # Description
    desc_line1 = "Unlimited Image-to-Video generation powered by MiniMax H3"
    desc_line2 = "with crystal-clear native stereo dialogue, SFX & music."
    draw.text((tx, 355), desc_line1, fill=(51, 65, 85, 255), font=font_desc)
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
        draw.rounded_rectangle([px, py, px + pill_w, py + 38], radius=19, fill=(241, 245, 249, 255), outline=col, width=1)
        draw.text((px + 14, py + 8), label, fill=(30, 41, 59, 255), font=font_tag)
        px += pill_w + 16

    # Bottom branding watermark
    draw.text((W - 320, H - 45), "VideoGen Studio · Local AI Engine", fill=(148, 163, 184, 255), font=font_desc)

    og.save(os.path.join(STATIC_DIR, "og-image-light.png"), "PNG")
    print("Created static/og-image-light.png (1200x630)")

render_og_hero_image_light()

# --------------------------------------------------------------------------
# 4. Generate Web App Manifest (site.webmanifest)
# --------------------------------------------------------------------------
manifest_content = """{
  "name": "VideoGen Studio - MiniMax H3",
  "short_name": "VideoGen",
  "description": "Unlimited Image-to-Video generation with native stereo audio powered by MiniMax H3",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#ffffff",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/favicon.svg",
      "sizes": "any",
      "type": "image/svg+xml"
    }
  ]
}
"""

with open(os.path.join(STATIC_DIR, "site.webmanifest"), "w", encoding="utf-8") as f:
    f.write(manifest_content)
print("Created static/site.webmanifest")
