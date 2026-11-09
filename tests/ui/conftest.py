import os
import socket
import subprocess
import sys
import time

import pytest
import requests


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def base_url():
    """Start the app in fixture mode on a free port and stop it after the session."""
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    env = {**os.environ, "DATA_SOURCE": "fixture"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                if requests.get(f"{url}/api/health", timeout=1).status_code == 200:
                    break
            except requests.ConnectionError:
                time.sleep(0.2)
        else:
            raise RuntimeError("App did not start")
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=5)
