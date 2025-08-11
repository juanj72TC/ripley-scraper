import os
import socket
import subprocess
import tempfile
import time
import uuid
from urllib.request import urlopen, URLError


class BrowserManager:
    def __init__(self, brave_bin="brave-browser"):
        self.brave_bin = brave_bin
        self.proc = None
        self.port = None
        self.user_data_dir = None

    def _get_free_port(self):
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def _wait_for_cdp(self, timeout=10):
        url = f"http://127.0.0.1:{self.port}/json/version"
        start = time.time()
        while time.time() - start < timeout:
            try:
                with urlopen(url, timeout=1) as resp:
                    if resp.status == 200:
                        return True
            except URLError:
                time.sleep(0.2)
        return False

    def launch_browser(self):
        self.port = self._get_free_port()
        self.user_data_dir = os.path.join(
            tempfile.gettempdir(), f"brave_{uuid.uuid4().hex}"
        )

        print(f"[*] Lanzando Brave en puerto {self.port}...")
        self.proc = subprocess.Popen(
            [
                self.brave_bin,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={self.user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                # flags críticos en contenedores:
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if not self._wait_for_cdp():
            self.terminate_browser()
            raise RuntimeError("Brave no inició en el tiempo esperado")

        print(f"[✅] Brave lanzado en CDP: http://127.0.0.1:{self.port}")

    def terminate_browser(self):
        if self.proc:
            print("[*] Cerrando Brave...")
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            print("[✅] Brave cerrado.")
        self.proc = None
