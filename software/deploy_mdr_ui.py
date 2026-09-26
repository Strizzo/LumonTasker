"""Deploy the MDR-inspired task terminal UI, preserving history and the MQTT subscriber."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

app = Path('/home/srizzo/taskticket/TaskTicket')
stage = app.parent / 'mdr-ui-stage/taskticket'
expected = {
    'templates/terminal.html': 'f8097d8998d7edbddfb5f51569dfd91898d927ab6ca3f01977de59eb2c6516de',
    'static/terminal.css': '1c552758050e64ec16b7623d15338068e9c7f354484d606c9473e69ee7ce1a29',
    'static/terminal.js': '390882ad16eff538de39f796ad802d381b575770a1bfcccf7c3f9b5074dc9f7f',
}
for relative, digest in expected.items():
    if hashlib.sha256((app / relative).read_bytes()).hexdigest() != digest:
        raise SystemExit('Source changed since inspection: ' + relative)
files = list(expected) + ['static/fonts/LiberationSans-Regular.ttf', 'static/fonts/Liberation-LICENSE.txt']
backup = app.parent / 'backups' / ('mdr-ui-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
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
    'version': 'MDR-inspired task terminal', 'selection_mode': 'local',
    'rollback': 'Restore the three backed-up files to their relative paths, then restart taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
