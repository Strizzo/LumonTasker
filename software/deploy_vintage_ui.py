"""Deploy the simplified terminal UI, preserving history and the MQTT subscriber."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = app.parent / 'vintage-ui-stage/taskticket'
expected = {
    'main.py': 'ba6068ecdf1c6680ec1bd20f8e037244afbc714a3d8ec42e7e55610d604462a2',
    'templates/terminal.html': '61df93b9114b1688b3d8500b187665307adb99a53b4538451b0f16c3a458bf15',
    'static/terminal.css': 'f5c883933d51be430980ac386fcd9bc9fba083dd95a318c91e8b5b9f17d7de4e',
    'static/terminal.js': 'a6de68923791c88c1a3e220e86592ed7e795fdcf3e39bca29d82d9c2e3263aa2',
}
for relative, digest in expected.items():
    if hashlib.sha256((app / relative).read_bytes()).hexdigest() != digest:
        raise SystemExit('Source changed since inspection: ' + relative)
compile((stage / 'main.py').read_text(), 'main.py', 'exec')
files = list(expected) + ['static/fonts/DejaVuSansMono.ttf', 'static/fonts/DejaVu-LICENSE.txt']
backup = app.parent / 'backups' / ('vintage-ui-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
for relative in expected:
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app / relative, target)
history = app / 'data/task_history.json'
history_hash = hashlib.sha256(history.read_bytes()).hexdigest()
pid_command = ['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value']
subscriber_pid = subprocess.check_output(pid_command, text=True).strip()
subprocess.run(['sudo', '-n', 'systemctl', 'stop', 'taskiosk.service'], check=True)
try:
    for relative in files:
        (app / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(stage / relative, app / relative)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=True)
except Exception:
    for relative in expected:
        shutil.copy2(backup / relative, app / relative)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=False)
    raise
manifest = {
    'deployed_at': datetime.now(timezone.utc).isoformat(),
    'backup': str(backup), 'changed_files': files,
    'history_unchanged': history_hash == hashlib.sha256(history.read_bytes()).hexdigest(),
    'subscriber_pid_unchanged': subscriber_pid == subprocess.check_output(pid_command, text=True).strip(),
    'version': 'simple terminal', 'selection_mode': 'local',
    'rollback': 'Restore the four backed-up files to their relative paths, then restart taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
