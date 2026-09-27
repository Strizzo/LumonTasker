"""Encode the small ticket logo as an ESC/POS monochrome raster image."""
import struct
from PIL import Image, ImageOps


def raster_image(image, fragment_height=128):
    """Encode contiguous strips, keeping each bitmap below the POS80 buffer size.

    GS v 0 advances by exactly the image height and returns to the start of the
    line. No newlines belong between strips: they would add seams to the page.
    """
    if image.width % 8 or not 8 <= image.width <= 1024 or image.height < 1:
        raise ValueError('Invalid raster image dimensions.')
    if not 1 <= fragment_height <= 512:
        raise ValueError('Invalid raster fragment height.')
    mono = image.convert('1', dither=Image.Dither.NONE)
    dots = ImageOps.invert(mono.convert('L')).convert('1', dither=Image.Dither.NONE).tobytes()
    row_bytes = image.width // 8
    chunks = [b'\x1ba\x00']
    for y in range(0, image.height, fragment_height):
        height = min(fragment_height, image.height - y)
        chunks.extend([b'\x1dv0\x00' + struct.pack('<HH', row_bytes, height),
                       dots[y * row_bytes:(y + height) * row_bytes]])
    return b''.join(chunks)


def raster_logo(path, paper_width=576):
    """Return a centred GS v 0 bitmap, with black pixels encoded as set bits.

    The POS80 uses a 576-dot printable width. White padding centres the logo
    without relying on firmware-specific image alignment behavior.
    """
    if not 128 <= paper_width <= 1024 or paper_width % 8:
        raise ValueError('Printable width must be 128–1024 dots and divisible by eight.')
    with Image.open(path) as source:
        rgba = source.convert('RGBA')
        flattened = Image.new('RGBA', rgba.size, 'white')
        flattened.alpha_composite(rgba)
        width = min(320, paper_width)
        height = max(1, round(rgba.height * width / rgba.width))
        logo = flattened.convert('L').resize((width, height), Image.Resampling.LANCZOS)
        logo = logo.convert('1', dither=Image.Dither.NONE)
    canvas = Image.new('1', (paper_width, height + 8), 1)
    canvas.paste(logo, ((paper_width - width) // 2, 4))
    # Pillow's 1-bit white is 1; ESC/POS's printed black is 1.
    dots = ImageOps.invert(canvas.convert('L')).convert('1', dither=Image.Dither.NONE).tobytes()
    header = b'\x1dv0\x00' + struct.pack('<HH', paper_width // 8, canvas.height)
    return b'\x1ba\x00' + header + dots + b'\n'
