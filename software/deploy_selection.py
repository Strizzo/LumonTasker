"""Deploy the staged local-selector release on the Pi; preserve MQTT service."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = Path('/home/srizzo/taskticket/lumon-ui-stage/taskticket')
expected = {'main.py': '22362b73aa3458bb8af1411caa37bab17b6096ca9938aeae37d891362140e5f8', 'core/task_selector.py': '03f1f37e5c6cda89933ce95afa5acf9064e2786bba3f9b20eac0051bbba4037b', 'processors/llm_processor.py': 'b7136939cfdf4456e4f8a4ce42596a6380876e21c0046c2ba2d20872d4bcef64', 'data_sources/trello.py': '2fb3c35d82c9bc68ae1d1066087fd5621c36608a82e6c9203d9b5ed03ec4cc7d'}
for relative, digest in expected.items():
    if hashlib.sha256((app / relative).read_bytes()).hexdigest() != digest:
        raise SystemExit('Source changed since inspection: ' + relative)
files = ['main.py', 'terminal_status.py', 'core/task_selector.py', 'core/task_manager.py', 'data_sources/trello.py', 'processors/llm_processor.py', 'templates/terminal.html', 'static/terminal.js', 'static/terminal.css']
for relative in files:
    if relative.endswith('.py'):
        compile((stage / relative).read_text(), relative, 'exec')
backup = app.parent / 'backups' / ('local-selection-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
for relative in files:
    (backup / relative).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app / relative, backup / relative)
history = app / 'data/task_history.json'
history_hash = hashlib.sha256(history.read_bytes()).hexdigest()
subscriber_pid = subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value'], text=True).strip()
subprocess.run(['sudo', '-n', 'systemctl', 'stop', 'taskiosk.service'], check=True)
try:
    for relative in files:
        shutil.copy2(stage / relative, app / relative)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=True)
except Exception:
    for relative in files:
        shutil.copy2(backup / relative, app / relative)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=False)
    raise
manifest = {'deployed_at': datetime.now(timezone.utc).isoformat(), 'backup': str(backup), 'changed_files': files, 'selection_default': 'local', 'optional_model': 'qwen/qwen3.7-flash', 'history_unchanged': hashlib.sha256(history.read_bytes()).hexdigest() == history_hash, 'subscriber_pid_unchanged': subscriber_pid == subprocess.check_output(['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value'], text=True).strip()}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
