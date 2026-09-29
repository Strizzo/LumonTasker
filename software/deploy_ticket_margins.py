"""Deploy adjusted work-slip margins without printing or changing task history."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

app = Path('/home/srizzo/taskticket/TaskTicket')
relative = 'printer/ticket.py'
source = Path(__file__).resolve().parent / 'taskticket' / relative
expected = '8c84fd8d09b86b2f937c6f5cb51ae290fdef7b552b615a27634d8eb78921c96e'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kiosk(action):
    subprocess.run(['sudo', '-n', 'systemctl', action, 'taskiosk.service'], check=True)


def subscriber_pid():
    return subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service',
                                    '-p', 'MainPID', '--value'], text=True).strip()


if digest(app / relative) != expected:
    raise SystemExit('Source changed since inspection: ' + relative)
compile(source.read_text(), relative, 'exec')
backup = app.parent / 'backups' / ('ticket-margins-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
(backup / 'printer').mkdir(parents=True, exist_ok=False)
shutil.copy2(app / relative, backup / relative)
subscriber_before = subscriber_pid()
kiosk('stop')
history = app / 'data/task_history.json'
history_hash = digest(history)
try:
    shutil.copy2(source, app / relative)
    # Exercise the deployed printer class against a temporary file, never USB.
    sys.path.insert(0, str(app))
    from printer.thermal_printer import ThermalPrinter
    with tempfile.TemporaryDirectory() as folder:
        printer = ThermalPrinter()
        printer.debug_mode = False
        printer.is_initialized = True
        printer.use_direct_access = True
        printer.printer_device = str(Path(folder) / 'captured.bin')
        if not printer.print_task_ticket(dict(task_id='synthetic-margin-check', ticket_title='Review the department filing procedure', estimated_time=15, selection_method='local')):
            raise RuntimeError('Synthetic printer capture failed')
        captured = Path(printer.printer_device).read_bytes()
        if not captured.startswith(b'\x1b@\x1ba\x00\x1dv0\x00') or not captured.endswith(b'\n\x1d\x56\x41\x03'):
            raise RuntimeError('Invalid captured raster job')
    kiosk('start')
    for attempt in range(30):
        try:
            with urlopen('http://127.0.0.1:5000/display', timeout=2) as response:
                if response.status == 200 and b'terminal.js?v=8' in response.read():
                    break
        except OSError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError('Kiosk did not become healthy')
    assert digest(history) == history_hash, 'Task history changed during deployment'
    assert subscriber_pid() == subscriber_before, 'Message-printer service restarted unexpectedly'
except Exception:
    kiosk('stop')
    shutil.copy2(backup / relative, app / relative)
    kiosk('start')
    raise

manifest = {
    'deployed_at': datetime.now(timezone.utc).isoformat(), 'backup': str(backup),
    'changed_files': [relative], 'deployed_sha256': {relative: digest(app / relative)},
    'artwork_top_margin_dots': 8, 'added_bottom_padding_dots': 96,
    'net_added_paper_dots': 80, 'synthetic_job_capture_passed': True,
    'history_unchanged': digest(history) == history_hash,
    'subscriber_pid_unchanged': subscriber_pid() == subscriber_before,
    'physical_tickets_printed': 0,
    'physical_margin_check': 'Pending the next printed ticket.',
    'rollback': 'Stop taskiosk.service, restore printer/ticket.py from backup, then start taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
