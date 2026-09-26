"""Add native pointer hiding to the existing kiosk launcher, with a backup."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

launcher = Path('/home/srizzo/Desktop/taskiosk.sh')
expected = 'fdc0eadb172be6bb6405012c4055ffd212fccc2d55782f15dff301d413afdea4'
source = launcher.read_text()
if hashlib.sha256(launcher.read_bytes()).hexdigest() != expected:
    raise SystemExit('Kiosk launcher changed since inspection')
backup = Path('/home/srizzo/taskticket/backups') / ('kiosk-cursor-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(launcher, backup / 'taskiosk.sh')
command = 'unclutter --timeout 1 --ignore-scrolling --debug >> "$LOG_FILE" 2>&1 &'
source = source.replace('# Start the Flask app in the background', '# Hide the native pointer, including before Chromium receives mouse motion.\n' + command + '\nCURSOR_PID=$!\n\n# Start the Flask app in the background', 1)
source = source.replace('while true; do\n', 'while true; do\n    if ! ps -p "$CURSOR_PID" > /dev/null; then\n        ' + command + '\n        CURSOR_PID=$!\n    fi\n\n', 1)
candidate = backup / 'taskiosk-updated.sh'
candidate.write_text(source)
subprocess.run(['bash', '-n', str(candidate)], check=True)
history = Path('/home/srizzo/taskticket/TaskTicket/data/task_history.json')
history_hash = hashlib.sha256(history.read_bytes()).hexdigest()
pid_command = ['systemctl', 'show', 'thermal-printer-subscriber.service', '-p', 'MainPID', '--value']
subscriber_pid = subprocess.check_output(pid_command, text=True).strip()
subprocess.run(['sudo', '-n', 'systemctl', 'stop', 'taskiosk.service'], check=True)
try:
    launcher.write_text(source)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=True)
except Exception:
    shutil.copy2(backup / 'taskiosk.sh', launcher)
    subprocess.run(['sudo', '-n', 'systemctl', 'start', 'taskiosk.service'], check=False)
    raise
manifest = {
    'deployed_at': datetime.now(timezone.utc).isoformat(), 'backup': str(backup),
    'launcher': str(launcher), 'installed_package': 'unclutter-xfixes 1.5-3',
    'idle_timeout_seconds': 1,
    'history_unchanged': history_hash == hashlib.sha256(history.read_bytes()).hexdigest(),
    'subscriber_pid_unchanged': subscriber_pid == subprocess.check_output(pid_command, text=True).strip(),
    'rollback': 'Restore taskiosk.sh from this backup to the launcher path, then restart taskiosk.service.',
}
(backup / 'deployment.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
