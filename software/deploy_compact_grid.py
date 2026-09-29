"""Guarded compact-grid deployment; never issues a ticket or edits task history."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from urllib.request import urlopen

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = Path(__file__).resolve().parent / 'taskticket'
expected = {'templates/terminal.html': '8d2a93f924291d404c902d7959feba99014d77d0083d04f3ec316a0e93b14c88', 'templates/terminal_mdr.html': 'da741ffb5c50519677a57cf3551333a7c8db78847100c5aec5c6214e433c00d4', 'static/terminal.js': '7c69abb1534ceffb5e4e3e57632aa8a1682ebc32f01fb802214f67e7e181a2ae', 'static/terminal-shared.css': 'f1779e4deb8203bef7348d6d5fadaa87c5e809bf19c11d2329dea14901f20b10'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kiosk(action):
    subprocess.run(['sudo', '-n', 'systemctl', action, 'taskiosk.service'], check=True)


def subscriber_pid():
    return subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value'], text=True).strip()


for relative, checksum in expected.items():
    if digest(app / relative) != checksum:
        raise SystemExit('Source changed since inspection: ' + relative)
    if not (stage / relative).is_file():
        raise SystemExit('Missing staged file: ' + relative)
    if relative.endswith('.py'):
        compile((stage / relative).read_text(), relative, 'exec')

backup = app.parent / 'backups' / ('compact-grid-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
for relative in expected:
    (backup / relative).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app / relative, backup / relative)

history = app / 'data/task_history.json'
subscriber_before = subscriber_pid()
kiosk('stop')
history_hash = digest(history)
try:
    for relative in expected:
        shutil.copy2(stage / relative, app / relative)
    kiosk('start')
    for attempt in range(30):
        try:
            with urlopen('http://127.0.0.1:5000/display', timeout=2) as response:
                body = response.read()
                if b'id="manageBtn"' in body and b'terminal.js?v=8' in body:
                    break
        except OSError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError('Updated kiosk did not become healthy')
    with urlopen('http://127.0.0.1:5000/display?theme=mdr', timeout=5) as response:
        assert b'id="taskGrid"' in response.read()
    assert digest(history) == history_hash, 'History changed during deployment'
    assert subscriber_pid() == subscriber_before, 'Message-printer service restarted unexpectedly'
except Exception:
    kiosk('stop')
    for relative in expected:
        shutil.copy2(backup / relative, app / relative)
    kiosk('start')
    raise

manifest = {
    'deployed_at': datetime.now(timezone.utc).isoformat(), 'backup': str(backup),
    'changed_files': list(expected), 'history_unchanged': digest(history) == history_hash,
    'subscriber_pid_unchanged': subscriber_before == subscriber_pid(),
    'deployed_sha256': {relative: digest(app / relative) for relative in expected},
    'version': 'Larger task cards; no fixed focus UI on active tasks',
    'rollback': 'Stop taskiosk.service, restore changed_files from backup, then start taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
