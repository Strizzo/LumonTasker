"""Guarded task-picker deployment; never issues a ticket or edits task history."""
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
expected = {
    'main.py': '6efd262778571c62f9af74c2574dbcd9f48c2048465bc7b5c4785ca39af8dddb',
    'core/task_selector.py': '5d0df4bef9dcaff0dc562f949df0487d7bdbcb8b7a1ace5c3adbadae80200c01',
    'templates/terminal.html': 'c9296fdb4be7a2f050b807e30063af792ce68f54ed4f9e227094e93c219ad0aa',
    'templates/terminal_mdr.html': '41cc5f464ec073a77c5e582ea5d09dc019c424def0255b11cd3aa72d60d1dfd2',
    'static/terminal.js': 'f495f5db43b4b892d4a4a95d8625decf1a32b9a44a676134c5536030f36203a4',
    'static/terminal-shared.css': 'c579b15e27770e4690020a5e7251bb128499c3900e23625d52063795acccde76',
}


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

backup = app.parent / 'backups' / ('manage-ui-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
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
                if b'id="manageBtn"' in body and b'terminal.js?v=5' in body:
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
    'version': 'Manual task picker, 3x3, both layouts',
    'rollback': 'Stop taskiosk.service, restore changed_files from backup, then start taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
