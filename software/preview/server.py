"""Local UI preview with fake tasks. Never contacts the Pi or a printer."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import time
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1] / "taskticket"
state = {"print_calls": 0, "fail_action": False, "fail_print": False, "offline": False, "current_task": None, "started_at": None}


class Preview(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass

    def json(self, value, code=200):
        data = json.dumps(value).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/current_task":
            return self.json({"task": state["current_task"], "started_at": state["started_at"]})
        if self.path.split("?")[0] == "/terminal_status":
            return self.json({"ok": False, "reason": "connection"} if state["offline"] else {"ok": True, "counts": {"todo": 11, "doing": 0, "btn": 19}})
        if self.path == "/test-state":
            return self.json(state)
        if url.path in ("/", "/display"):
            self.path = "/templates/terminal_mdr.html" if parse_qs(url.query).get("theme") == ["mdr"] else "/templates/terminal.html"
        super().do_GET()

    def do_POST(self):
        if self.path == "/test-state":
            state.update(json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0")))))
            return self.json(state)
        if self.path == "/print_task":
            state["print_calls"] += 1
            if state["fail_print"]:
                code = 503 if state["fail_print"] == 503 else 404
                return self.json({"success": False, "message": "No suitable task found" if code == 404 else "Trello unavailable"}, code)
            state["current_task"] = {"task_id": "preview-task", "ticket_title": "Review the next enclosure revision", "estimated_time": "15", "challenge_time": "10", "motivation": "Consider the lighter walls and the glass seat.\nYour contribution is appreciated.", "source_list": "TODO"}
            state["started_at"] = time.time() * 1000
            return self.json({"success": True, "task": state["current_task"]})
        if self.path in ("/complete_task", "/skip_task"):
            if not state["fail_action"]:
                state["current_task"] = None
                state["started_at"] = None
            return self.json({"success": not state["fail_action"], "message": "Preview action"}, 500 if state["fail_action"] else 200)
        self.json({"success": False}, 404)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8655), Preview).serve_forever()
