"""Deploy the two terminal layouts without changing credentials or task history."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import py_compile
import shutil
import subprocess
import time
import urllib.request

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = app.parent / 'themes-ui-stage/taskticket'
expected = {
    'main.py': '614c80ac42c421cf2651b726bcda241b01e7f68b1096d3c0b25958e0872f3989',
    'core/history_manager.py': '39b7fcd0e8b06f584d94a61d2e461a2590359379df3b24a4dd37dd1bd2a25c77',
    'templates/terminal.html': 'c19cae84b531c2a9c4d3ade7e45df5368833c7064f3301644d3d2276269c6b68',
    'static/terminal.css': 'ecb5411c179c33e01be118b6ba4feb0db49bfedeaf54738fc434875a555d1699',
    'static/terminal.js': '2c9d7a89a5d989f60095df88165d999048b8c8e8cbd98889c15184f8d9d6c344',
}
for relative, digest in expected.items():
    if hashlib.sha256((app / relative).read_bytes()).hexdigest() != digest:
        raise SystemExit('Source changed since inspection: ' + relative)
files = list(expected) + ['templates/terminal_mdr.html', 'static/terminal-mdr.css', 'static/terminal-shared.css']
for relative in files:
    if not (stage / relative).is_file():
        raise SystemExit('Missing staged file: ' + relative)
for relative in ['main.py', 'core/history_manager.py']:
    py_compile.compile(str(stage / relative), doraise=True)
backup = app.parent / 'backups' / ('themes-ui-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
existing = []
for relative in files:
    if (app / relative).exists():
        existing.append(relative)
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
    for attempt in range(20):
        try:
            with urllib.request.urlopen('http://127.0.0.1:5000/display', timeout=2) as response:
                if b'terminal-shared.css?v=4' in response.read():
                    break
        except OSError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError('Updated terminal did not become healthy')
except Exception:
    subprocess.run(['sudo', '-n', 'systemctl', 'stop', 'taskiosk.service'], check=False)
    for relative in existing:
        shutil.copy2(backup / relative, app / relative)
    for relative in set(files) - set(existing):
        (app / relative).unlink(missing_ok=True)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=False)
    raise
manifest = {
    'deployed_at': datetime.now(timezone.utc).isoformat(),
    'backup': str(backup), 'changed_files': files, 'backed_up_files': existing,
    'history_unchanged': history_hash == hashlib.sha256(history.read_bytes()).hexdigest(),
    'subscriber_pid_unchanged': subscriber_pid == subprocess.check_output(pid_command, text=True).strip(),
    'version': 'Classic default, optional MDR', 'selection_mode': 'local',
    'rollback': 'Stop taskiosk.service, restore backed_up_files to their relative paths, then start taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
