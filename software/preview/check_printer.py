"""Check ticket bytes and failure handling without contacting a printer or Trello."""
import ast
import contextlib
from dataclasses import dataclass
from datetime import datetime
import io
import logging
import os
from pathlib import Path
import random
import struct
import sys
import tempfile
from types import SimpleNamespace
from typing import Dict, Optional
import unittest
from unittest.mock import patch

from PIL import Image

APP = Path(__file__).resolve().parents[1] / 'taskticket'
sys.path.insert(0, str(APP))
from printer.logo import raster_logo, raster_image
from printer.ticket import render_ticket, format_ticket_text


def printer_classes():
    # Load the real methods without importing USB drivers or application config.
    path = APP / 'printer/thermal_printer.py'
    nodes = [node for node in ast.parse(path.read_text()).body
             if isinstance(node, ast.ClassDef)]
    namespace = dict(dataclass=dataclass, Optional=Optional, Dict=Dict, os=os,
                     Path=Path, raster_logo=raster_logo, raster_image=raster_image,
                     render_ticket=render_ticket, format_ticket_text=format_ticket_text, __file__=str(path),
                     logger=logging.getLogger('ticket-check'))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


class TicketPrinting(unittest.TestCase):
    def setUp(self):
        self.namespace = printer_classes()
        self.printer = self.namespace['ThermalPrinter'].__new__(self.namespace['ThermalPrinter'])
        self.printer.format = self.namespace['ThermalFormatting']()
        self.printer.debug_mode = False
        self.printer.is_initialized = True
        self.printer.use_direct_access = True
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.output = Path(self.folder.name) / 'captured.bin'
        self.printer.printer_device = str(self.output)
        env = patch.dict(os.environ, {'PRINTER_TASK_LOGO': '1', 'PRINTER_WIDTH_DOTS': '576'})
        env.start()
        self.addCleanup(env.stop)

    def test_bitmap_polarity_dimensions_and_centering(self):
        data = raster_logo(APP / 'static/lumon-print.png')
        self.assertEqual(data[:7], b'\x1ba\x00\x1dv0\x00')
        width_bytes, height = struct.unpack('<HH', data[7:11])
        self.assertEqual((width_bytes, height), (72, 172))
        dots = data[11:-1]
        self.assertEqual(len(dots), width_bytes * height)
        decoded = Image.frombytes('1', (width_bytes * 8, height), dots)
        with Image.open(APP / 'static/lumon-print.png') as source:
            self.assertEqual(source.size, (320, 164))
            # ESC/POS set bits must correspond to black, not white, source pixels.
            for y in range(source.height):
                for x in range(source.width):
                    self.assertEqual(bool(decoded.getpixel((x + 128, y + 4))),
                                     source.getpixel((x, y)) == 0)
        self.assertEqual(decoded.crop((0, 0, 128, height)).getbbox(), None)
        self.assertEqual(decoded.crop((448, 0, 576, height)).getbbox(), None)
        self.assertEqual(decoded.crop((0, 0, 576, 4)).getbbox(), None)

    def test_logo_and_text_share_one_job_and_final_cut(self):
        self.assertTrue(self.printer.print_text('A SYNTHETIC TASK\n', logo=True))
        job = self.output.read_bytes()
        bitmap = raster_logo(APP / 'static/lumon-print.png')
        self.assertEqual(job, b'\x1b@' + bitmap + b'A SYNTHETIC TASK\n' +
                         self.printer.format.FEED_AND_CUT.encode())

    def test_plain_print_and_disabled_logo_remain_text_only(self):
        self.assertTrue(self.printer.print_text('PLAIN\n'))
        plain = self.output.read_bytes()
        with patch.dict(os.environ, {'PRINTER_TASK_LOGO': '0'}):
            self.assertTrue(self.printer.print_text('PLAIN\n', logo=True))
        self.assertEqual(self.output.read_bytes(), plain)
        self.assertNotIn(b'\x1dv0', plain)

    def test_missing_artwork_falls_back_to_text(self):
        with patch.dict(self.namespace, {'raster_logo': lambda *a: (_ for _ in ()).throw(FileNotFoundError())}):
            with self.assertLogs('ticket-check', level='WARNING'):
                self.assertTrue(self.printer.print_text('STILL PRINTS\n', logo=True))
        self.assertIn(b'STILL PRINTS', self.output.read_bytes())
        self.assertNotIn(b'\x1dv0', self.output.read_bytes())

    def test_invalid_width_falls_back_to_text(self):
        with patch.dict(os.environ, {'PRINTER_WIDTH_DOTS': '577'}):
            with self.assertLogs('ticket-check', level='WARNING'):
                self.assertTrue(self.printer.print_text('STILL PRINTS\n', logo=True))
        self.assertNotIn(b'\x1dv0', self.output.read_bytes())

    def test_failed_write_reports_failure_without_retry(self):
        bitmap = raster_logo(APP / 'static/lumon-print.png')
        with patch.dict(self.namespace, {'raster_logo': lambda *a: bitmap}), \
                patch('builtins.open', side_effect=OSError('synthetic device unavailable')) as writer:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertFalse(self.printer.print_text('SYNTHETIC\n', logo=True))
        self.assertEqual(writer.call_count, 1)

    def test_usb_library_path_receives_binary_bitmap_before_text(self):
        calls = []
        self.printer.use_direct_access = False
        self.printer.printer = SimpleNamespace(text=lambda text: calls.append(('text', text)),
                                              _raw=lambda data: calls.append(('raw', data)))
        self.assertTrue(self.printer.print_text('SYNTHETIC\n', logo=True))
        self.assertEqual([kind for kind, _ in calls], ['text', 'raw', 'text', 'text'])
        self.assertEqual(calls[1][1], raster_logo(APP / 'static/lumon-print.png'))

    def test_task_ticket_renders_full_slip_and_propagates_write_failure(self):
        tree = ast.parse((APP / 'core/task_manager.py').read_text())
        manager = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'TaskTicketManager')
        method = next(node for node in manager.body if isinstance(node, ast.FunctionDef) and node.name == 'print_task_ticket')
        namespace = dict(Dict=Dict, datetime=datetime, random=random)
        exec(compile(ast.Module(body=[method], type_ignores=[]), 'task_manager.py', 'exec'), namespace)
        task = dict(ticket_title='Synthetic verification', estimated_time=15, motivation='Test only')
        namespace['print_task_ticket'](SimpleNamespace(printer=self.printer), task)
        self.assertIn(b'\x1dv0', self.output.read_bytes())
        self.assertTrue(self.output.read_bytes().endswith(b'\n\x1d\x56\x41\x03'))
        with patch.object(self.printer, 'print_task_ticket', return_value=False):
            with self.assertRaises(RuntimeError):
                namespace['print_task_ticket'](SimpleNamespace(printer=self.printer), task)

    def test_missing_font_falls_back_before_any_usb_write(self):
        task=dict(ticket_title='Résumé\x1b@ test',estimated_time=15,selection_method='local')
        with patch.dict(self.namespace, {'render_ticket':lambda *a,**k: (_ for _ in ()).throw(OSError('font missing'))}):
            with patch.object(self.printer,'print_text',return_value=True) as fallback:
                with self.assertLogs('ticket-check',level='WARNING'):
                    self.assertTrue(self.printer.print_task_ticket(task))
        self.assertFalse(self.output.exists())
        text=fallback.call_args.args[0]
        self.assertIn('WORK ASSIGNMENT',text)
        self.assertNotIn('\x1b',text)

    def test_image_usb_path_sends_one_complete_job(self):
        calls=[]
        self.printer.use_direct_access=False
        self.printer.printer=SimpleNamespace(_raw=calls.append)
        image=render_ticket(dict(ticket_title='Synthetic',estimated_time=15,selection_method='local'))
        payload=raster_image(image)
        self.assertTrue(self.printer.print_image_job(payload))
        self.assertEqual(calls,[b'\x1b@'+payload+b'\n\x1d\x56\x41\x03'])

    def test_failed_image_write_is_not_retried_or_reprinted_as_text(self):
        with patch('builtins.open',side_effect=OSError('synthetic failure')) as writer:
            with self.assertLogs('ticket-check',level='ERROR'):
                self.assertFalse(self.printer.print_image_job(b'prepared bitmap'))
        self.assertEqual(writer.call_count,1)


if __name__ == '__main__':
    unittest.main()
