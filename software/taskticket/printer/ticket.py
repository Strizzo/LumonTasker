"""A compact Lumon-inspired work slip, rendered at the printer's actual dot width.

This is original themed stationery, not a reproduction of a screen-used prop.
The saved preview and USB job use the same monochrome pixels.
"""
from datetime import datetime
from functools import lru_cache
import hashlib
import math
import os
from pathlib import Path
import textwrap
import unicodedata
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / 'static'
MOTTO = 'The work is mysterious and important.'
# The POS80 leaves a leading margin between its print head and cutter. Keep
# only 1 mm of artwork above the logo, and add 12 mm to the former footer
# padding to balance the physical ticket. At 203 dpi, eight dots are about 1 mm.
TOP_MARGIN_DOTS = 8
BOTTOM_PADDING_DOTS = 112


def clean_text(value):
    value = unicodedata.normalize('NFC', str(value or ''))
    # Card text cannot introduce ESC/POS commands or unexpected blank lines.
    value = ''.join(' ' if char.isspace() else char for char in value
                    if char.isspace() or not unicodedata.category(char).startswith('C'))
    return ' '.join(value.split())


def ticket_content(task, issued_at=None):
    if issued_at is None:
        issued_at = datetime.now(ZoneInfo(os.getenv('TASKTICKET_TIMEZONE', 'Europe/Luxembourg')))
    title = clean_text(task.get('ticket_title') or task.get('title')) or 'Untitled assignment'
    reference = hashlib.sha256(str(task.get('task_id') or title).encode()).hexdigest()[:6].upper()
    def duration(value):
        try:
            minutes = float(value)
            if not math.isfinite(minutes) or minutes <= 0:
                return 'NOT SET'
            return '%g MIN' % minutes
        except (TypeError, ValueError):
            return 'NOT SET'
    return dict(title=title, reference='MDR-' + reference,
                date='%02d %s %d' % (issued_at.day, 'JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split()[issued_at.month - 1], issued_at.year),
                time=issued_at.strftime('%H:%M'),
                time_label='FOCUS ALLOCATION' if task.get('selection_method') else 'TIME ESTIMATE',
                duration=duration(task.get('estimated_time')),
                challenge=duration(task['challenge_time']) if task.get('challenge_time') else None,
                # Current local selection already explains the focus allowance.
                # Keep any older, task-specific guidance without repeating it.
                guidance=clean_text(task.get('motivation')) if not task.get('selection_method') else '')


@lru_cache(maxsize=12)
def font(size, bold=False):
    filename = 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'
    return ImageFont.truetype(str(ASSETS / 'fonts' / filename), size)


def wrap_pixels(text, face, width, stroke=0):
    """Wrap words, including unbroken URLs, without losing title characters."""
    lines, line = [], ''
    for word in clean_text(text).split():
        candidate = (line + ' ' + word).strip()
        if face.getlength(candidate) + 2 * stroke <= width:
            line = candidate
            continue
        if line:
            lines.append(line)
            line = ''
        while face.getlength(word) + 2 * stroke > width:
            count = max(1, int(width / face.getlength('M')) - 1)
            while face.getlength(word[:count]) + 2 * stroke > width:
                count -= 1
            lines.append(word[:count])
            word = word[count:]
        line = word
    if line:
        lines.append(line)
    return lines or ['']


class Receipt:
    def __init__(self, width):
        self.width = width
        self.margin = 30
        self.inner = width - 2 * self.margin
        self.y = TOP_MARGIN_DOTS
        self.operations = []

    def text(self, text, size=18, align='left', bold=False, gap=0):
        face, stroke = font(size, bold), 0
        for line in wrap_pixels(text, face, self.inner, stroke):
            length = face.getlength(line)
            x = (self.width - length) / 2 if align == 'center' else self.margin
            self.operations.append(('text', (x, self.y), line, face, stroke))
            self.y += size + 9
        self.y += gap

    def pair(self, left, right, size=18):
        face = font(size)
        if face.getlength(left + '  ' + right) > self.inner:
            self.text(left, size)
            self.text(right, size)
            return
        self.operations.extend([('text', (self.margin, self.y), left, face, 0),
                                ('text', (self.width - self.margin - face.getlength(right), self.y), right, face, 0)])
        self.y += size + 10

    def rule(self):
        self.y += 10
        self.operations.append(('line', (self.margin, self.y, self.width - self.margin - 1, self.y)))
        self.y += 18

    def logo(self):
        with Image.open(ASSETS / 'lumon-print.png') as source:
            width = min(256, self.inner)
            height = round(source.height * width / source.width)
            logo = source.convert('L').resize((width, height), Image.Resampling.LANCZOS)
        self.operations.append(('image', ((self.width - width) // 2, self.y), logo))
        self.y += height + 14

    def checkboxes(self):
        for x, label in [(self.margin, 'COMPLETED'), (self.width / 2 + 22, 'DEFERRED')]:
            self.operations.append(('box', (x, self.y + 1, x + 19, self.y + 20)))
            self.operations.append(('text', (x + 31, self.y), label, font(18), 0))
        self.y += 32

    def image(self):
        image = Image.new('L', (self.width, self.y + BOTTOM_PADDING_DOTS), 255)
        draw = ImageDraw.Draw(image)
        for operation in self.operations:
            kind, position, *args = operation
            if kind == 'text':
                text, face, stroke = args
                draw.text(position, text, font=face, fill=0, anchor='lt', stroke_width=stroke)
            elif kind == 'line':
                draw.line(position, fill=0, width=2)
            elif kind == 'box':
                draw.rectangle(position, outline=0, width=2)
            else:
                image.paste(args[0], position)
        return image.convert('1', dither=Image.Dither.NONE)


def render_ticket(task, issued_at=None, width=576, show_logo=True, proof=False):
    if not 384 <= width <= 1024 or width % 8:
        raise ValueError('Ticket width must be 384–1024 dots, divisible by eight.')
    content = ticket_content(task, issued_at)
    slip = Receipt(width)
    if show_logo:
        slip.logo()
    slip.text('MACRODATA REFINEMENT', size=18, align='center', gap=6)
    slip.text('WORK ASSIGNMENT', size=26, align='center', bold=True, gap=18)
    slip.pair('REF. ' + content['reference'], 'STATION 775', size=17)
    slip.pair(content['date'], content['time'], size=17)
    slip.rule()
    slip.text('ASSIGNED WORK', size=17, gap=8)
    slip.text(content['title'], size=28, bold=True, gap=12)
    if content['guidance']:
        slip.text(content['guidance'], size=20, gap=10)
    slip.rule()
    slip.pair(content['time_label'], content['duration'], size=22)
    if content['challenge']:
        slip.pair('CHALLENGE', content['challenge'])
    slip.rule()
    slip.checkboxes()
    slip.rule()
    slip.text(MOTTO, size=17, align='center', gap=8)
    slip.pair('FORM MDR / 01', 'INTERNAL USE ONLY', size=16)
    if proof:
        slip.text('LAYOUT PROOF / NO TASK ISSUED', size=16, align='center')
    return slip.image()


def format_ticket_text(task, issued_at=None):
    """Readable native-text fallback if fonts or graphics assets are unavailable."""
    content = ticket_content(task, issued_at)
    lines = ['MACRODATA REFINEMENT'.center(48), 'WORK ASSIGNMENT'.center(48), '',
             'REF. ' + content['reference'] + ' / STATION 775', content['date'] + '  ' + content['time'],
             '-' * 44, 'ASSIGNED WORK', *textwrap.wrap(content['title'], 44), '',
             content['time_label'] + ': ' + content['duration']]
    if content['challenge']:
        lines.append('CHALLENGE: ' + content['challenge'])
    if content['guidance']:
        lines.extend(['', *textwrap.wrap(content['guidance'], 44)])
    lines.extend(['-' * 44, '[ ] COMPLETED        [ ] DEFERRED', '', MOTTO,
                  'FORM MDR / 01              INTERNAL USE ONLY'])
    # Native firmware does not interpret UTF-8 consistently. Raster output
    # preserves accented text; only the emergency text fallback transliterates.
    return unicodedata.normalize('NFKD', '\n'.join(lines) + '\n').encode('ascii', 'replace').decode()
