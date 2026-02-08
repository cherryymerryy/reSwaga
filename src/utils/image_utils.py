import colorsys
import math
from PIL import Image

from elyx import assets # type: ignore


MIN_LIGHTNESS_FOR_TEXT = 0.725
MAX_LIGHTNESS_FOR_TEXT = 0.25
LIGHTNESS_THRESHOLD = 0.5


def get_cover_accent_color(cover: Image.Image):
    img = cover.resize((16, 16), Image.Resampling.LANCZOS)
    pixels = img.load()
    l_width, l_height = img.size

    for y in range(l_height):
        for x in range(l_width):
            if img.mode == 'L':
                r = pixels[x, y]
                r = math.pow(r / 255.0, 1 / 2.2) * 255.0
                pixels[x, y] = int(r)
            else:
                r, g, b = pixels[x, y][:3]
                r = math.pow(r / 255.0, 1 / 2.2) * 255.0
                g = math.pow(g / 255.0, 1 / 2.2) * 255.0
                b = math.pow(b / 255.0, 1 / 2.2) * 255.0
                if img.mode == 'RGB':
                    pixels[x, y] = (int(r), int(g), int(b))
                elif img.mode == 'RGBA':
                    a = pixels[x, y][3]
                    pixels[x, y] = (int(r), int(g), int(b), a)

    if img.mode == 'L':
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size)
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img

    pixels = list(img.getdata())
    i_width, i_height = img.size

    if img.mode == 'RGB':
        total_r, total_g, total_b = 0, 0, 0
        darkness_index = 2.5
        for r, g, b in pixels:
            total_r += int(r // darkness_index)
            total_g += int(g // darkness_index)
            total_b += int(b // darkness_index)
        count = i_width * i_height
        average = (total_r // count, total_g // count, total_b // count)
    else:
        total = sum(pixels)
        average = (total // (i_width * i_height),) * 3

    return average


def adjust_color_for_readability(rgb_color: tuple) -> tuple:
    r, g, b = [x / 255.0 for x in rgb_color]
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    if l < LIGHTNESS_THRESHOLD:
        new_lightness = MIN_LIGHTNESS_FOR_TEXT
    else:
        new_lightness = MAX_LIGHTNESS_FOR_TEXT

    new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_lightness, s)
    return tuple(int(x * 255) for x in (new_r, new_g, new_b))


def get_font_family(font: int, is_bold: bool):
    if font == 0:
        return assets.fonts.Onest_Bold.java_file if is_bold else assets.fonts.Onest_Regular.java_file
    elif font == 1:
        return assets.fonts.Circular_Bold.java_file if is_bold else assets.fonts.Circular_Regular.java_file
    elif font == 2:
        return assets.fonts.NotoSansJP_Bold.java_file if is_bold else assets.fonts.NotoSansJP_Regular.java_file
    elif font == 3:
        return assets.fonts.YSMusic_Bold.java_file if is_bold else assets.fonts.YSMusic_Regular.java_file
    elif font == 4:
        return assets.fonts.YSText_Bold.java_file if is_bold else assets.fonts.YSText_Regular.java_file
    else:
        return None
