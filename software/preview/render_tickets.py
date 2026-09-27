"""Render synthetic ticket previews; never accesses USB, Trello or task history."""
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'taskticket'))
from printer.ticket import render_ticket

SAMPLES = [
    ('work-slip', 'Review the department filing procedure'),
    ('long-title', 'Prepare the quarterly records and verify that every department submission has been filed under the correct reference number.'),
    ('accented-title', 'Organizzare le attività della settimana e aggiornare il résumé'),
]


def main():
    output=Path(__file__).resolve().parent/'tickets'
    output.mkdir(exist_ok=True)
    for name,title in SAMPLES:
        task=dict(task_id='layout-proof',ticket_title=title,estimated_time=15,selection_method='local')
        if name=='accented-title':task['challenge_time']=10
        image=render_ticket(task,issued_at=datetime(2026,9,27,8,24))
        image.save(output/(name+'.png'),dpi=(203,203))
        print(name, image.size)


if __name__=='__main__':main()
