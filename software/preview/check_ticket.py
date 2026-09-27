"""Check wrapping, print bounds and lossless bitmap strips with synthetic tasks."""
from datetime import datetime
from pathlib import Path
import struct
import sys
import unittest

from PIL import Image, ImageChops, ImageOps

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'taskticket'))
from printer.ticket import render_ticket, ticket_content, format_ticket_text, wrap_pixels, font
from printer.logo import raster_image


class WorkSlips(unittest.TestCase):
    def setUp(self):
        self.task=dict(task_id='synthetic-proof',ticket_title='Review the department filing procedure',
                       estimated_time=15,selection_method='local',motivation='A 15-minute focus session.')
        self.stamp=datetime(2026,9,27,8,24)

    def test_time_is_focus_allowance_and_old_estimate_stays_an_estimate(self):
        content=ticket_content(self.task,self.stamp)
        self.assertEqual(content['duration'],'15 MIN')
        self.assertEqual(content['time_label'],'FOCUS ALLOCATION')
        self.assertEqual(content['date'],'27 SEP 2026')
        self.assertEqual(content['time'],'08:24')
        self.assertEqual(content['guidance'],'')
        legacy={**self.task,'selection_method':None,'challenge_time':8}
        content=ticket_content(legacy,self.stamp)
        self.assertEqual(content['time_label'],'TIME ESTIMATE')
        self.assertEqual(content['challenge'],'8 MIN')
        self.assertEqual(content['guidance'],self.task['motivation'])

    def test_accented_long_titles_wrap_without_clipping_or_losing_words(self):
        title='Organizzare le attività della settimana, aggiornare il résumé e rivedere tutte le scadenze.'
        lines=wrap_pixels(title,font(28,True),516)
        self.assertEqual(' '.join(lines),title)
        self.assertTrue(all(font(28,True).getlength(line)<=516 for line in lines))
        url='https://example.com/'+('abcdefghij'*25)
        lines=wrap_pixels(url,font(28,True),516)
        self.assertEqual(''.join(lines),url)
        self.assertTrue(all(font(28,True).getlength(line)<=516 for line in lines))

    def test_paper_margins_and_ticket_length_with_variable_titles(self):
        for width in (384,576,640):
            for title in (self.task['ticket_title'],'W'*160,'Résumé – attività e priorità'):
                image=render_ticket({**self.task,'ticket_title':title},self.stamp,width=width)
                black=ImageOps.invert(image.convert('L'))
                box=black.getbbox()
                self.assertGreaterEqual(box[0],29)
                self.assertLessEqual(box[2],width-29)
                self.assertGreaterEqual(box[1],23)
                self.assertLess(box[3],image.height-10)
        image=render_ticket(self.task,self.stamp)
        self.assertEqual(image.width,576)
        self.assertLess(image.height,800)

    def test_raster_strips_reconstruct_exact_preview_without_blank_seams(self):
        image=render_ticket(self.task,self.stamp)
        data=raster_image(image)
        self.assertEqual(data[:3],b'\x1ba\x00')
        pos,rows,decoded=3,0,bytearray()
        while pos<len(data):
            self.assertEqual(data[pos:pos+4],b'\x1dv0\x00')
            row_bytes,height=struct.unpack('<HH',data[pos+4:pos+8])
            self.assertEqual(row_bytes,72)
            self.assertLessEqual(height,128)
            pos+=8
            decoded.extend(data[pos:pos+row_bytes*height])
            pos+=row_bytes*height
            rows+=height
        self.assertEqual(rows,image.height)
        recovered=Image.frombytes('1',image.size,bytes(decoded))
        recovered=ImageOps.invert(recovered.convert('L'))
        self.assertIsNone(ImageChops.difference(image.convert('L'),recovered).getbbox())

    def test_no_control_commands_currency_or_missing_duration_crash(self):
        task={**self.task,'ticket_title':'Résumé\x1b@\n  attività\x00','estimated_time':'invalid'}
        content=ticket_content(task,self.stamp)
        self.assertEqual(content['title'],'Résumé@ attività')
        self.assertEqual(content['duration'],'NOT SET')
        text=format_ticket_text(task,self.stamp)
        self.assertNotIn('\x1b',text)
        self.assertNotIn('EUR',text)
        self.assertIn('[ ] COMPLETED',text)
        self.assertTrue(text.isascii())
        self.assertEqual(render_ticket(task,self.stamp).width,576)

    def test_proof_and_no_logo_are_explicit_variants(self):
        normal=render_ticket(self.task,self.stamp)
        proof=render_ticket(self.task,self.stamp,proof=True)
        no_logo=render_ticket(self.task,self.stamp,show_logo=False)
        self.assertGreater(proof.height,normal.height)
        self.assertLess(no_logo.height,normal.height)
        with self.assertRaises(ValueError):render_ticket(self.task,width=575)


if __name__=='__main__':unittest.main()
