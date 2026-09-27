# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Start/stop only this edition's local review processes; never install a service.

Linux process start times guard against PID reuse. Children run in their own
process groups so stopping npm also stops its preview process. No global kill,
Docker action or dataset deletion is performed.
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".runtime" / "services.json"


def identity(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return None if fields[0] == "Z" else fields[19]
    except (FileNotFoundError, ProcessLookupError):
        return None


def alive(entry):
    return entry["start_time"] is not None and identity(entry["pid"]) == entry["start_time"]


def stop(entries):
    """Signal only process groups whose leader identity still matches our record."""
    for entry in entries:
        if alive(entry):
            os.killpg(entry["pid"], signal.SIGTERM)
    for _ in range(50):
        if not any(alive(entry) for entry in entries):
            return
        time.sleep(0.1)


def ready(url):
    try:
        with urlopen(url, timeout=1) as response:
            return response.status == 200
    except (OSError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "stop", "status"])
    parser.add_argument("--api-port", type=int, default=9010)
    parser.add_argument("--web-port", type=int, default=5180)
    args = parser.parse_args()
    if not Path("/proc/self/stat").is_file():
        parser.error(
            "The background launcher requires Linux. See docs/DEVELOPMENT.md for foreground commands."
        )
    previous = json.loads(STATE.read_text()) if STATE.exists() else {}
    entries = previous.get("services", [])
    if args.action == "stop":
        stop(entries)
        if any(alive(e) for e in entries):
            sys.exit("A Community process has not stopped. Inspect .runtime logs before retrying.")
        STATE.unlink(missing_ok=True)
        print("Community review services stopped.")
        return
    if args.action == "status":
        for entry in entries:
            print(f"{entry['name']}: {'running' if alive(entry) else 'stopped'} (PID {entry['pid']})")
        print(previous.get("web_url", "Not started"))
        print(previous.get("api_url", ""))
        return
    if any(alive(e) for e in entries):
        sys.exit("Community is already running. Use ./scripts/status.sh or ./scripts/stop.sh first.")
    if not (ROOT / ".venv/bin/python").exists() or not (ROOT / "web/dist/index.html").exists():
        sys.exit("Run ./scripts/setup.sh first.")
    if args.api_port == args.web_port:
        parser.error("API and Web ports must differ")
    for port in (args.api_port, args.web_port):
        if not 1024 <= port <= 65535:
            parser.error("Ports must be between 1024 and 65535")
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                sys.exit(f"Port {port} is in use. Nothing was stopped or replaced.")
    STATE.parent.mkdir(exist_ok=True)
    processes = []
    entries = []
    env = {**os.environ, "COMMUNITY_API_TARGET": f"http://127.0.0.1:{args.api_port}"}
    commands = [
        (
            "api",
            ROOT,
            [
                str(ROOT / ".venv/bin/python"),
                "-m",
                "uvicorn",
                "sedge_community.api:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.api_port),
            ],
        ),
        (
            "web",
            ROOT / "web",
            [
                "node",
                "node_modules/vite/bin/vite.js",
                "preview",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.web_port),
                "--strictPort",
            ],
        ),
    ]
    try:
        for name, cwd, command in commands:
            with (STATE.parent / f"{name}.log").open("ab") as log:
                proc = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
            processes.append(proc)
            entries.append({"name": name, "pid": proc.pid, "start_time": identity(proc.pid)})
        web_url = f"http://localhost:{args.web_port}"
        api_url = f"http://localhost:{args.api_port}/api/docs"
        STATE.write_text(json.dumps({"services": entries, "web_url": web_url, "api_url": api_url}, indent=2))
        for _ in range(100):
            if any(proc.poll() is not None for proc in processes):
                raise RuntimeError("A review process exited. See .runtime/api.log and .runtime/web.log")
            if ready(f"http://127.0.0.1:{args.api_port}/api/v1/healthz") and ready(web_url):
                print(f"SEDGE Community 1.0.0\nWeb: {web_url}\nAPI: {api_url}\nNo startup service installed.")
                return
            time.sleep(0.2)
        raise RuntimeError("Health check timed out. See .runtime logs.")
    except (OSError, RuntimeError, KeyboardInterrupt) as exc:
        stop(entries)
        for proc in processes:
            proc.wait(timeout=5)
        STATE.unlink(missing_ok=True)
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
