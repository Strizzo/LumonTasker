"""Guarded deployment of the confirmed ticket logo; never issues a ticket."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = Path(__file__).resolve().parent / 'taskticket'
expected = {
    'printer/thermal_printer.py': 'bb748a537cc3655477fcece2ceba209a052891c7a4d9dbba29d9c4d623fb048e',
    'core/task_manager.py': '2450131ae8cbc70fd08a93cf044746f2ecc2ae557a3d6d9cecbe44b6f6407fec',
}
new_files = ['printer/logo.py', 'static/lumon-print.png']
files = list(expected) + new_files


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subscriber_pid():
    return subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service',
                                    '-p', 'MainPID', '--value'], text=True).strip()


def kiosk(action):
    subprocess.run(['sudo', '-n', 'systemctl', action, 'taskiosk.service'], check=True)


for relative, checksum in expected.items():
    if digest(app / relative) != checksum:
        raise SystemExit('Source changed since inspection: ' + relative)
for relative in new_files:
    if (app / relative).exists():
        raise SystemExit('Unexpected existing file: ' + relative)
for relative in files:
    if relative.endswith('.py'):
        compile((stage / relative).read_text(), relative, 'exec')

backup = app.parent / 'backups' / ('ticket-logo-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
for relative in expected:
    (backup / relative).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app / relative, backup / relative)
history = app / 'data/task_history.json'
history_hash = digest(history)
subscriber_before = subscriber_pid()

kiosk('stop')
try:
    for relative in files:
        shutil.copy2(stage / relative, app / relative)
    # Import the actual deployed class and capture a synthetic job in a file.
    # is_initialized prevents even the initial ESC @ from reaching USB.
    sys.path.insert(0, str(app))
    from printer.thermal_printer import ThermalPrinter
    with tempfile.TemporaryDirectory() as folder:
        printer = ThermalPrinter()
        printer.debug_mode = False
        printer.is_initialized = True
        printer.printer_device = str(Path(folder) / 'captured.bin')
        if not printer.print_text('SYNTHETIC DEPLOYMENT CHECK\n', logo=True):
            raise RuntimeError('Synthetic printer capture failed')
        captured = Path(printer.printer_device).read_bytes()
        if b'\x1dv0\x00' not in captured or b'SYNTHETIC DEPLOYMENT CHECK' not in captured:
            raise RuntimeError('Logo or task text absent from captured job')
    kiosk('start')
    deadline = time.monotonic() + 25
    while True:
        try:
            with urlopen('http://127.0.0.1:5000/display', timeout=2) as response:
                if response.status != 200 or b'/static/terminal.js' not in response.read():
                    raise RuntimeError('Terminal page did not pass its health check')
            break
        except Exception:
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
except Exception:
    kiosk('stop')
    for relative in expected:
        shutil.copy2(backup / relative, app / relative)
    for relative in new_files:
        (app / relative).unlink(missing_ok=True)
    kiosk('start')
    raise

manifest = {
    'deployed_at': datetime.now(timezone.utc).isoformat(),
    'backup': str(backup),
    'changed_files': files,
    'sha256': {relative: digest(app / relative) for relative in files},
    'logo_enabled': True,
    'logo_dimensions_dots': [320, 164],
    'paper_width_dots': 576,
    'physical_test': 'User confirmed the standalone logo receipt was clear and complete.',
    'synthetic_job_capture_passed': True,
    'terminal_http_status': 200,
    'history_unchanged': digest(history) == history_hash,
    'subscriber_pid_unchanged': subscriber_before == subscriber_pid(),
    'real_tasks_printed_during_deployment': 0,
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
