"""Guarded task-total deployment; never issues a ticket or edits task history."""
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
expected = {'main.py': '937ab5ebe5ed0a2cbf6a98d7484dc83e0d73f03d95755fea2a673e12a4b9ec93', 'templates/terminal.html': 'd5d0a81218d540d54dbce882fb842d62e7217d79c354b97a97db98a8e8e1da6b', 'templates/terminal_mdr.html': '3bab65c2e0d02653dc3246c777a13d785664ae1cef2524cead452f4532120863', 'static/terminal.js': '3be487fc1eb205d5ef90602d462f9d05c3a5b8a30079e491ddf582b4403ae562', 'static/terminal-shared.css': 'e0371068c8a4943959c4ead1f79de2fb6871563e755ddfc626d296b0a2eb2556'}


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

backup = app.parent / 'backups' / ('task-total-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
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
                if b'id="manageBtn"' in body and b'terminal.js?v=7' in body:
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
    'version': 'Total focus across regular tasks, excluding BTN',
    'rollback': 'Stop taskiosk.service, restore changed_files from backup, then start taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
