"""Run over SSH on the Pi after staging; only updates the task kiosk."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = Path('/home/srizzo/taskticket/lumon-ui-stage/taskticket')
expected = '607e0527ac7e0f384399578d07ea51cb3feb28610ef540f98841fbd04513d7f6'
if hashlib.sha256((app / 'main.py').read_bytes()).hexdigest() != expected:
    raise SystemExit('Main source changed since inspection; stop and review before deploying.')
for name in ('main.py', 'terminal_status.py'):
    compile((stage / name).read_text(), str(stage / name), 'exec')
backup = app.parent / 'backups' / ('lumon-ui-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(app / 'main.py', backup / 'main.py')
shutil.copy2(app / 'templates/display.html', backup / 'display.html')
history = app / 'data/task_history.json'
history_hash = hashlib.sha256(history.read_bytes()).hexdigest()
before_subscriber = subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value'], text=True).strip()
for relative in ('terminal_status.py', 'templates/terminal.html'):
    target = app / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(stage / relative, target)
shutil.copytree(stage / 'static', app / 'static', dirs_exist_ok=True)
temp = app / '.main.py.lumon-ui-new'
shutil.copy2(stage / 'main.py', temp)
os.replace(temp, app / 'main.py')
result = subprocess.run(['sudo', '-n', 'systemctl', 'restart', 'taskiosk.service'], capture_output=True, text=True)
if result.returncode:
    shutil.copy2(backup / 'main.py', app / 'main.py')
    subprocess.run(['sudo', '-n', 'systemctl', 'restart', 'taskiosk.service'], check=False)
    raise SystemExit('Kiosk restart failed; restored original main.py.')
after_subscriber = subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value'], text=True).strip()
manifest = {'deployed_at': datetime.now(timezone.utc).isoformat(), 'backup': str(backup), 'history_unchanged': hashlib.sha256(history.read_bytes()).hexdigest() == history_hash, 'subscriber_pid_unchanged': before_subscriber == after_subscriber, 'changed_files': ['main.py', 'terminal_status.py', 'templates/terminal.html', 'static/terminal.css', 'static/terminal.js', 'static/lumon.svg', 'static/fonts/'], 'rollback': 'Restore this backup main.py into TaskTicket/main.py, then sudo systemctl restart taskiosk.service.'}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
